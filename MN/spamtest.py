import requests
from bs4 import BeautifulSoup
import spacy
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

nlp = spacy.load('en_core_web_md')

def extract_features(text):
    doc = nlp(text)
    return doc.vector

# url = 'https://www.timestelegram.com/story/news/2010/07/15/ilion-couple-uses-farmers-market/44787064007/'

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}
# try:
#     r = requests.get(url, timeout=10, headers=headers)
#     if r.status_code == requests.codes.ok:
#         print("good")
#         soup = BeautifulSoup(r.text, 'html.parser')
#         text_soup = ' '.join([st for st in soup.stripped_strings])
#         print(text_soup)
#         text_data = ' '.join([p.text for p in soup.find_all('p')])
#         print(text_data)
#         vec = extract_features(text_soup)
#         print(vec)
#     else:
#         r.raise_for_status()
# except Exception as e:
#     print(e)

excel_path = r'checkbystate\work_00_NY_results.xlsx'
df = pd.read_excel(excel_path, sheet_name=0, usecols=['state', 'type', 'web_status', 'title', 'url', 'desc'])
df = df[:1000]
df.dropna(axis = 0, how = 'all', inplace = True)
df_good = df[df['web_status'] == 'good']

# Handle missing values
df_good['desc'].fillna("", inplace=True)

df_good['title_features'] = df_good['title'].apply(extract_features)
df_good['desc_features'] = df_good['desc'].apply(extract_features)
df_good['type'].replace({"1": 1, "listings": 2, "other": 3}, inplace=True)
df_good = df_good[df_good['type'].isin([1, 2, 3])]
df_good['type'] = df_good['type'].astype(int)


# Calculate mean vector for each document
df_good['title_features_mean'] = df_good['title_features'].apply(lambda x: np.mean(x, axis=0))
df_good['desc_features_mean'] = df_good['desc_features'].apply(lambda x: np.mean(x, axis=0))

# Create a DataFrame with mean vectors
df_sk = df_good[['title_features_mean', 'desc_features_mean', 'type']]
#df_sk = df_sk[df_sk['type'].isin([1, 2, 3])]
print(df_sk['type'].unique())
df_sk.columns = ['title', 'desc', 'type']

X = df_sk[['title', 'desc']]
y = df_sk['type']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = np.vstack(X_train['title'].values)
X_test_scaled = np.vstack(X_test['title'].values)

X_train_scaled = scaler.fit_transform(X_train_scaled)
X_test_scaled = scaler.transform(X_test_scaled)

classifier = LogisticRegression()
classifier.fit(X_train_scaled, y_train)

predictions = classifier.predict(X_test_scaled)
accuracy = accuracy_score(y_test, predictions)
X_test['predictions'] = predictions


result_df = pd.DataFrame({'predicted_type': predictions, 'actual_type': y_test.values}, index=X_test.index)


result_df = pd.concat([X_test, result_df], axis=1)


incorrect_predictions = result_df[result_df['predicted_type'] != result_df['actual_type']]

original_text_data = df_sk.loc[incorrect_predictions.index, ['title', 'desc']]
incorrect_predictions[['original_title', 'original_desc']] = original_text_data

print(X_test[X_test['predictions'] != 1])
print(f"Accuracy: {accuracy}")

print(incorrect_predictions[['title', 'desc', 'original_title', 'original_desc', 'predicted_type', 'actual_type']])
