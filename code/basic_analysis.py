import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import KFold

os.getcwd()
os.chdir('C:/Users/chizi/Documents/GitHub/MSIS 5223/project-deliverable-1-apt-rent/data')

# Step 1: clean data
df1 = pd.read_csv('aptrent_2000_2018.csv', sep=',')

df1.shape
df1.columns

# get rid of null values
df2 = df1.dropna()
df2.shape
df2.columns

df2.to_csv('delete_null.csv', sep=',')

# remove the first untitiled column which is originally row numbers of old dataset
df3 = pd.read_csv('delete_null.csv', sep=',')
df3.shape
df3.columns

df4 = df3.drop('Unnamed: 0', axis=1)
df4.shape
df4.columns
df4.dtypes

df4.to_csv('cleaned_aptrent.csv', sep=',')


# remove rows that price is greater than 10,000
df5 = df4.drop(df4[(df4.price > 10000)].index)
df5.shape

# create a new attribute for length of description
len_descr = df5['descr'].map(str).apply(len)
len_descr

df6 = df5[['post_id', 'date', 'year', 'nhood', 'city', 'county', 'price', 'beds',
       'baths', 'sqft', 'room_in_apt', 'address', 'lat', 'lon', 'title', 'descr']]
df6.columns

df7 = df5[['details']]
df7.columns

df8 = pd.concat([df6, len_descr, df7], axis=1)
df8.columns

df8.columns.values[16] = 'len_descr'
df8.columns

os.getcwd()
os.chdir('C:/Users/chizi/Documents/GitHub/MSIS 5223/project-deliverable-1-apt-rent/data')
df8.to_csv('final_aptrent.csv', sep=',')