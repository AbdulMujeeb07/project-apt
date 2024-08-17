import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from sklearn import metrics
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier

from sklearn.model_selection import train_test_split
from sklearn import preprocessing

from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf

os.chdir(r'C:\Users\chizi\Documents\GitHub\MSIS 5223\project-deliverable-2-apt-rent\data')

apt_data = pd.read_csv('final_aptrent.csv')
apt_data.columns

# initial data sets
df_model = pd.DataFrame(apt_data, columns=['year', 'beds', 'baths', 'sqft'])
df_model.columns
df_model.drop(df_model.columns[np.isnan(df_model).any()], axis=1)

# Split data into training and testing
apt_data_train, apt_data_test, y_train, y_test = train_test_split(df_model, apt_data.price, test_size=0.4)

scaler = preprocessing.StandardScaler()
scaler.fit(apt_data_train)

apt_data_train_std = scaler.transform(apt_data_train)
apt_data_test_std = scaler.transform(apt_data_test)

apt_data_train_std
apt_data_test_std

nnreg1 = MLPRegressor(activation='logistic', solver='sgd', 
                      hidden_layer_sizes=(20,20), 
                      early_stopping=True)
nnreg1.fit(apt_data_train_std, y_train)

nnpred1_pred1 = nnreg1.predict(apt_data_test_std)
nnreg1.n_layers_
nnreg1.coefs_
metrics.mean_absolute_error(y_test, nnpred1_pred1)
metrics.mean_squared_error(y_test, nnpred1_pred1)
metrics.r2_score(y_test, nnpred1_pred1)

nnpred1_pred2 = nnreg1.predict(apt_data_train_std)
metrics.mean_absolute_error(y_train, nnpred1_pred2)
metrics.mean_squared_error(y_train, nnpred1_pred2)
metrics.r2_score(y_train, nnpred1_pred2)





