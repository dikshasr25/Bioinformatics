# -*- coding: utf-8 -*-
"""Mice_classification (2) (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vDncNorwtlKxHwJsAJVuX3CJbK4gju6I
"""

#Importing the necessary libraries
import pandas as pd
import numpy as np

#Loading the dataset
df = pd.read_csv("Data_Cortex_Nuclear.csv")
df.head()

df.shape

df.info()

df.describe()

df[df["class"] == 't-CS-s'].isnull()

"""Data Preprocessing"""

#Checking the null values
df.isna().sum()

# Group the DataFrame by 'class'
grouped = df.groupby('class')

# Get all column names
all_columns = df.columns.tolist()

# Extract numeric columns (assuming they start from the 2nd and end at 'CaNA_N')
start_index = all_columns.index('DYRK1A_N')  # Find the index of the starting column
end_index = all_columns.index('CaNA_N') + 1  # Find the index of the ending column + 1 (to include it)
numeric_columns = all_columns[start_index:end_index]

# Fill missing values in numerical columns with the mean for each class
df[numeric_columns] = grouped[numeric_columns].transform(lambda x: x.fillna(x.mean()))

df[numeric_columns]

#Normalizing the data
from sklearn.preprocessing import MinMaxScaler
for i in numeric_columns:
    df[[i]] = MinMaxScaler().fit_transform(df[[i]])

df

df.isna().sum()

for col in df.select_dtypes("object"):
    print(f'{col :-<50} {df[col].unique()}')

def encoding(df):
    code = {'Control':1,
            'Ts65Dn':0,
            'Memantine':1,
            'Saline':0,
            'C/S':0,
            'S/C':1,
            'c-CS-m':0,
            'c-SC-m':1,
            'c-CS-s':2,
            'c-SC-s':3,
            't-CS-m':4,
            't-SC-m':5,
            't-CS-s':6,
            't-SC-s':7,
           }
    for col in df.select_dtypes('object'):
        if col!='MouseID':
            df.loc[:,col]=df[col].map(code)

    return df

df = encoding(df)

df

X = df[numeric_columns]
y = df['class']

X

y

df[df["class"] == 6].isnull()

df

df.to_csv("clean_dataset.csv")

"""Exploratory Data Analysis"""

# Ensure all columns are numeric and handle non-numeric data
df = df.apply(pd.to_numeric, errors='coerce')

# Compute the correlation matrix and plot it as a heatmap
import matplotlib.pyplot as plt
import seaborn as sns

corr_matrix = df.corr()

plt.figure(figsize=(30,20))
plt.title('Correlation Matrix of 77 proteins')
ax = sns.heatmap(corr_matrix, cmap='RdBu_r')

plt.show()

#Correaltion Heatmap
corr= df.corr(method='pearson')
plt.figure(figsize=(50,40))

# Using Seaborn to create a heatmap
sns.heatmap(corr, annot=True, fmt='.2f', cmap='Pastel2', linewidths=2)

plt.title('Correlation Heatmap')
plt.show()

df.corr()['class'].abs().sort_values()

df.head(5)

"""## Feature Selection"""

# function to separate categorical from numeric features
def feature_types(df):
    categ = []
    numer = []
    for c in df.columns:
        if df[c].dtype == 'object': categ.append(c)
        else: numer.append(c)
    return categ, numer
#display information on categorical features
categ, numer = feature_types(df)

# temporarily remove null-values and min-max scale data
from sklearn.preprocessing import MinMaxScaler

nonna=df.dropna(axis=1,thresh=901)
nonna=nonna.dropna(axis=0,how='any')
categ,numeri=feature_types(nonna)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(nonna[numeri].values)

#identify most important features via Random Forest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OrdinalEncoder

ordinal = OrdinalEncoder()
labels = ordinal.fit_transform(nonna['class'].values[:,np.newaxis]).astype('int').squeeze()

forest = RandomForestClassifier(n_estimators=1000, max_depth=8, random_state=33)
forest.fit(scaled, labels)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Assuming df is your DataFrame and forest is your trained RandomForest model
# and 'numer' is the list of numerical columns used for training

# Get the indices of the top 40 important features
# Get the indices of the top 40 important features (excluding 'Behavior', 'Genotype', 'Treatment')
# Get the indices of the top 40 important features (excluding 'Behavior', 'Genotype', 'Treatment')
feats = np.argsort(forest.feature_importances_)[-40:]
# Use the columns that were actually used in training to get feature names
important_features_all = nonna[numeri].columns[feats][::-1]  # Use nonna[numeri] instead of df[numer]
important_features = [feature for feature in important_features_all if feature not in ['Behavior', 'Genotype', 'Treatment', 'class']]

# Get the feature importances for the selected features
importances = forest.feature_importances_[np.isin(nonna[numeri].columns, important_features)]

# Create a DataFrame to hold features and their importances
feature_importance_df = pd.DataFrame({
    'feature': important_features,
    'importance': importances
})

# Sort the DataFrame by importance in descending order
feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)

# Plot the feature importances
plt.figure(figsize=(15, 10))
sns.barplot(
    y=feature_importance_df['feature'],
    x=feature_importance_df['importance'],
    color='Grey'
)
plt.title('Significance of Most Important Features (Excluding Behavior, Genotype, Treatment)')
plt.xlabel('Feature Importance')
plt.ylabel('Features')
plt.show()

# Display the feature_importance_df DataFrame
print(feature_importance_df)

# Store the important features in variable 'x' for training
# Ensure you are using the correct DataFrame (df or nonna) based on your intent
x = df[feature_importance_df['feature']]  # Or x = nonna[feature_importance_df['feature']]

# Check the first few rows of x
print(x.head())

"""## Splite the dataset into train and test data"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

y = df['class'].values  # Directly use the values without re-encoding

# Scale features to a range
minmax = MinMaxScaler()
x = minmax.fit_transform(x)

X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.1, random_state=33)

X_train.shape,y_train.shape,X_test.shape,y_test.shape

results = {}

"""## XGBClassifier"""

from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, cross_val_predict, KFold
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix


# Define the XGBoost Classifier
xgb_clf = XGBClassifier()

# Set up k-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and calculate scores
cv_acc_scores = cross_val_score(xgb_clf, X_train, y_train, cv=kf, scoring='accuracy')
cv_f1_scores = cross_val_score(xgb_clf, X_train, y_train, cv=kf, scoring='f1_macro')

# Print cross-validation scores
print(f'Cross-validation accuracy scores: {cv_acc_scores}')
print(f'Cross-validation F1 scores: {cv_f1_scores}')
print(f'Mean cross-validation accuracy: {np.mean(cv_acc_scores)}')
print(f'Mean cross-validation F1 score: {np.mean(cv_f1_scores)}')

# Perform cross-validation prediction
pred_xgb_cv = cross_val_predict(xgb_clf, X_train, y_train, cv=kf)

# Calculate metrics for cross-validation prediction
acc_xgb_cv = accuracy_score(y_train, pred_xgb_cv)
f1_xgb_cv = f1_score(y_train, pred_xgb_cv, average='macro')

# Print the accuracy and F1 score for cross-validation prediction
print('Cross-validation prediction accuracy: ', acc_xgb_cv)
print('Cross-validation prediction F1 score: ', f1_xgb_cv)
print(classification_report(y_train, pred_xgb_cv))

# Get unique labels from y_train
labels = np.unique(y_train)

# Plot the confusion matrix for cross-validation prediction
sns.heatmap(confusion_matrix(y_train, pred_xgb_cv),
            xticklabels=labels, yticklabels=labels,
            annot=True, fmt='1d', cbar=False)
plt.title('Confusion Matrix (Cross-Validation Prediction)')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

"""## DNN"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dense(32, activation='relu'),
    layers.Dense(8, activation='softmax')  # 8 output classes
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(X_train, y_train, epochs=50, batch_size=32)

loss, accuracy = model.evaluate(X_test, y_test)
print('Test accuracy:', accuracy)

"""## KNeighborsClassifier"""

from sklearn.neighbors import KNeighborsClassifier

# Define the K-Nearest Neighbors Classifier
knn_clf = KNeighborsClassifier()

# Set up k-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Perform cross-validation and calculate scores
cv_acc_scores = cross_val_score(knn_clf, X_train, y_train, cv=kf, scoring='accuracy')
cv_f1_scores = cross_val_score(knn_clf, X_train, y_train, cv=kf, scoring='f1_macro')

# Print cross-validation scores
print(f'K-Nearest Neighbors cross-validation accuracy scores: {cv_acc_scores}')
print(f'K-Nearest Neighbors cross-validation F1 scores: {cv_f1_scores}')
print(f'Mean cross-validation accuracy: {np.mean(cv_acc_scores)}')
print(f'Mean cross-validation F1 score: {np.mean(cv_f1_scores)}')

# Perform cross-validation prediction
pred_knn_cv = cross_val_predict(knn_clf, X_train, y_train, cv=kf)

# Calculate metrics for cross-validation prediction
acc_knn_cv = accuracy_score(y_train, pred_knn_cv)
f1_knn_cv = f1_score(y_train, pred_knn_cv, average='macro')

# Print the accuracy and F1 score for cross-validation prediction
print('K-Nearest Neighbors cross-validation prediction accuracy: ', acc_knn_cv)
print('K-Nearest Neighbors cross-validation prediction F1 score: ', f1_knn_cv)
print(classification_report(y_train, pred_knn_cv))

# Plot the confusion matrix for cross-validation prediction
sns.heatmap(confusion_matrix(y_train, pred_knn_cv),
            xticklabels=labels, yticklabels=labels,
            annot=True, fmt='1d', cbar=False)
plt.title('Confusion Matrix (Cross-Validation Prediction) - K-Nearest Neighbors')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

"""## RandomForestClassifier"""

from sklearn.ensemble import RandomForestClassifier

# Define the Random Forest Classifier
rf_clf = RandomForestClassifier(random_state=42)

# Perform cross-validation and calculate scores
cv_acc_scores = cross_val_score(rf_clf, X_train, y_train, cv=kf, scoring='accuracy')
cv_f1_scores = cross_val_score(rf_clf, X_train, y_train, cv=kf, scoring='f1_macro')

# Print cross-validation scores
print(f'Random Forest cross-validation accuracy scores: {cv_acc_scores}')
print(f'Random Forest cross-validation F1 scores: {cv_f1_scores}')
print(f'Mean cross-validation accuracy: {np.mean(cv_acc_scores)}')
print(f'Mean cross-validation F1 score: {np.mean(cv_f1_scores)}')

# Perform cross-validation prediction
pred_rf_cv = cross_val_predict(rf_clf, X_train, y_train, cv=kf)

# Calculate metrics for cross-validation prediction
acc_rf_cv = accuracy_score(y_train, pred_rf_cv)
f1_rf_cv = f1_score(y_train, pred_rf_cv, average='macro')

# Print the accuracy and F1 score for cross-validation prediction
print('Random Forest cross-validation prediction accuracy: ', acc_rf_cv)
print('Random Forest cross-validation prediction F1 score: ', f1_rf_cv)
print(classification_report(y_train, pred_rf_cv))

# Plot the confusion matrix for cross-validation prediction
sns.heatmap(confusion_matrix(y_train, pred_rf_cv),
            xticklabels=labels, yticklabels=labels,
            annot=True, fmt='1d', cbar=False)
plt.title('Confusion Matrix (Cross-Validation Prediction) - Random Forest')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

"""## SVC"""

from sklearn.svm import SVC

# Define the Support Vector Machine Classifier
svm_clf = SVC(random_state=42)

# Perform cross-validation and calculate scores
cv_acc_scores = cross_val_score(svm_clf, X_train, y_train, cv=kf, scoring='accuracy')
cv_f1_scores = cross_val_score(svm_clf, X_train, y_train, cv=kf, scoring='f1_macro')

# Print cross-validation scores
print(f'Support Vector Machine cross-validation accuracy scores: {cv_acc_scores}')
print(f'Support Vector Machine cross-validation F1 scores: {cv_f1_scores}')
print(f'Mean cross-validation accuracy: {np.mean(cv_acc_scores)}')
print(f'Mean cross-validation F1 score: {np.mean(cv_f1_scores)}')

# Perform cross-validation prediction
pred_svm_cv = cross_val_predict(svm_clf, X_train, y_train, cv=kf)

# Calculate metrics for cross-validation prediction
acc_svm_cv = accuracy_score(y_train, pred_svm_cv)
f1_svm_cv = f1_score(y_train, pred_svm_cv, average='macro')

# Print the accuracy and F1 score for cross-validation prediction
print('Support Vector Machine cross-validation prediction accuracy: ', acc_svm_cv)
print('Support Vector Machine cross-validation prediction F1 score: ', f1_svm_cv)
print(classification_report(y_train, pred_svm_cv))

# Plot the confusion matrix for cross-validation prediction
sns.heatmap(confusion_matrix(y_train, pred_svm_cv),
            xticklabels=labels, yticklabels=labels,
            annot=True, fmt='1d', cbar=False)
plt.title('Confusion Matrix (Cross-Validation Prediction) - Support Vector Machine')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

"""## DecisionTreeClassifier"""

from sklearn.tree import DecisionTreeClassifier

# Define the Decision Tree Classifier
dt_clf = DecisionTreeClassifier(random_state=42)

# Perform cross-validation and calculate scores
cv_acc_scores = cross_val_score(dt_clf, X_train, y_train, cv=kf, scoring='accuracy')
cv_f1_scores = cross_val_score(dt_clf, X_train, y_train, cv=kf, scoring='f1_macro')

# Print cross-validation scores
print(f'Decision Tree Classifier cross-validation accuracy scores: {cv_acc_scores}')
print(f'Decision Tree Classifier cross-validation F1 scores: {cv_f1_scores}')
print(f'Mean cross-validation accuracy: {np.mean(cv_acc_scores)}')
print(f'Mean cross-validation F1 score: {np.mean(cv_f1_scores)}')

# Perform cross-validation prediction
pred_dt_cv = cross_val_predict(dt_clf, X_train, y_train, cv=kf)

# Calculate metrics for cross-validation prediction
acc_dt_cv = accuracy_score(y_train, pred_dt_cv)
f1_dt_cv = f1_score(y_train, pred_dt_cv, average='macro')

# Print the accuracy and F1 score for cross-validation prediction
print('Decision Tree Classifier cross-validation prediction accuracy: ', acc_dt_cv)
print('Decision Tree Classifier cross-validation prediction F1 score: ', f1_dt_cv)
print(classification_report(y_train, pred_dt_cv))

# Plot the confusion matrix for cross-validation prediction
sns.heatmap(confusion_matrix(y_train, pred_dt_cv),
            xticklabels=labels, yticklabels=labels,
            annot=True, fmt='1d', cbar=False)
plt.title('Confusion Matrix (Cross-Validation Prediction) - Decision Tree Classifier')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

results = {}
results['XGBClassifier'] = {'Accuracy': acc_xgb_cv, 'F1-score': f1_xgb_cv}

results['KNeighborsClassifier'] = {'Accuracy': acc_knn_cv, 'F1-score': f1_knn_cv}

results_df = pd.DataFrame.from_dict(results, orient='index')
print(results_df)

results_df.plot(kind='bar', figsize=(10, 6))
plt.title('Model Comparison')
plt.ylabel('Score')
plt.xticks(rotation=0)
plt.show()

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

models = {
    'K-Nearest Neighbors': KNeighborsClassifier(),
    'Random Forest': RandomForestClassifier(),
    'XGBoost Classifier': XGBClassifier(),
    'SVM': SVC(),
    'Decision Tree': DecisionTreeClassifier()
}


results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    confusion = confusion_matrix(y_test, y_pred)

    results[name] = {
        'Accuracy': accuracy,
        'Classification Report': report,
        'Confusion Matrix': confusion
    }

for name, result in results.items():
    print(f"Model: {name}")
    print(f"Accuracy: {result['Accuracy']}")
    print("Classification Report:")
    print(result['Classification Report'])
    print("Confusion Matrix:")
    print(result['Confusion Matrix'])
    print("\n")

import matplotlib.pyplot as plt

accuracies = [result['Accuracy'] for result in results.values()]
model_names = list(results.keys())

plt.bar(model_names, accuracies)
plt.xlabel('Model')
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.xticks(rotation=45)
plt.show()