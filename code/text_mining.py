import pandas as pd
import matplotlib.pyplot as plt
import os
import regex
import numpy as np 
import seaborn as sns

import nltk
#nltk.download('stopwords')
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer, PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, ConfusionMatrixDisplay

from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.chunk import conlltags2tree, tree2conlltags

os.chdir(r'C:\Users\chizi\Documents\GitHub\MSIS 5223\project-deliverable-2-apt-rent\data')

apt_data = pd.read_csv('final_aptrent.csv')
apt_data.columns

# load in the final aprtment rent file and rename the column 'descr' as 'aptdescr' to make it more descriptive
apt_data.rename(columns={'descr': 'aptdescr'}, inplace=True)
apt_data.columns

# adjust the case of the apartment description that all values are lowercase
apt_data['aptdescr'][2]
apt_data['aptdescr'][5]

# -- Optional: can add a screenshot of comparation, same for all the following
apt_data['aptdescr'] = apt_data['aptdescr'].apply(lambda x: " ".join(x.lower() for x in x.split()))

# remove the numerical values and punctuation
patterndigits = '\\b[0-9]+\\b'
apt_data['aptdescr'] = apt_data['aptdescr'].str.replace(patterndigits,'')

patternpunc = '[^\w\s]'
apt_data['aptdescr'] = apt_data['aptdescr'].str.replace(patternpunc,'')

# remove the stop words - in, the, is, an, etc
stop = stopwords.words('english')
apt_data['aptdescr'] = apt_data['aptdescr'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))

# check the top 30 words
word_freq = Counter(" ".join(apt_data['aptdescr']).split()).most_common(30)
rslt = pd.DataFrame(word_freq, columns=['Word', 'Frequency'])
print(rslt)

# stem the word
porstem = PorterStemmer()
apt_data['aptdescr'] = apt_data['aptdescr'].apply(lambda x: " ".join([porstem.stem(word) for word in x.split()]))

apt_data['aptdescr'][2]
apt_data['aptdescr'][5]

# create a document-term matrix
vectorizer = CountVectorizer()
tokens_data = pd.DataFrame(vectorizer.fit_transform(apt_data['aptdescr']).toarray(), columns=vectorizer.get_feature_names())
tokens_data.columns

#print(tokens_data.columns.tolist())

# Retrieve the top 10 in terms of volume
sort_text = tokens_data.sum()
sort_text.sort_values(ascending = False).head(10)


# ---------------- Sentiment Analysis ------------------------
## We created two bar charts of sentitment analysis for apartment description in R
## Joy vs Sadness, and Trust vs Fear
## We assume apartment owners prefer to describe their apartments as positive as possible to attractive people to rent
## Our results are consistent with this assumption.
## Now, try to do topic analysis

## ----------- Topic Analysis -------------
## According to previous text mining part, we want to use bedroom numbers as categorize

# Generate a bar chart of the number of terms categorized by bedromm numbers.
plot_size = plt.rcParams["figure.figsize"] 
print(plot_size[0]) 
print(plot_size[1])

plot_size[0] = 8
plot_size[1] = 6
plt.rcParams["figure.figsize"] = plot_size

apt_data.beds.value_counts()

apt_data.beds.value_counts().plot(kind='bar')
plt.xlabel('Bedrooms Number', fontsize = 12, weight = 'bold')
plt.ylabel('Frequencies by Apartment', fontsize = 12, weight = 'bold')
plt.title('Apartment Frequencies by Bedrooms Number', fontsize = 14, weight = 'bold')
plt.show()

## ----------- Topic Analysis -------------
## We used LDA because we want to create topics based on word's frequency
vectorizer = CountVectorizer(max_df=0.8, min_df=4, stop_words='english')
doc_term_matrix = vectorizer.fit_transform(apt_data['aptdescr'].values.astype('U'))
doc_term_matrix.shape
# Result: The document-term matrix results in 1,520 terms with 2,935 documents (i.e. apt descr).

# Generate the LDA with 5 topics to divide the text into 
# Set the seed to 35 so that we end up with the same result
LDA = LatentDirichletAllocation(n_components=5, random_state=35)
LDA.fit(doc_term_matrix)

first_topic = LDA.components_[0]
top_topic_words = first_topic.argsort()[-10:]

for i in top_topic_words:
    print(vectorizer.get_feature_names()[i])

for i,topic in enumerate(LDA.components_):
    print(f'Top 10 words for topic #{i}:')
    print([vectorizer.get_feature_names()[i] for i in topic.argsort()[-10:]])
    print('\n')

topic_values = LDA.transform(doc_term_matrix)
topic_values.shape

## Results of Topic Analysis - All 5 topics are trying their best to describe the strength of apartments
## Most strength are relative with the conviences of living
## For example, the apartment may be near with park which is friendly for people who have pets
## the apartment is location at the business center which could be a good choice for people who is working in this area
## the apartment including kitchen, bathrooms, and enough bedrooms that is suitable for a big family, etc.
## The result is consistant with the previous emotions analysis


## ----------- Classification in Sentiment Analysis -------------
# Create a term-frequency inverse-document-frequency (TF-IDF)
# matrix with sklearn:
# TF  = (Frequency of a word in the document)/(Total words in the document)
# IDF = Log((Total number of docs)/(Number of docs containing the word))
# We use this because this is one of the most frequently used metrics in in text mining to observe frequencies.
features = apt_data['aptdescr']

# We set only the 1,500 most frequently occurring terms, 
# only those terms that occur in a maximum of 90% of the documents (we prefer to be conservative), 
# but at least in 5 documents (i.e., apt description).
vectorizer = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.9, stop_words=stop)
processed_features = vectorizer.fit_transform(features).toarray()

# The test dataset will be 20% of the data; this results in a training set of 80%.
labels = apt_data['beds']
X_train, X_test, y_train, y_test = train_test_split(processed_features, labels, test_size=0.2, random_state=0)

text_classifier = RandomForestClassifier(n_estimators=200, random_state=0)
text_classifier.fit(X_train, y_train)
predictions = text_classifier.predict(X_test)

cm = confusion_matrix(y_test,predictions)
print(cm)

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot()
plt.show()

print(classification_report(y_test,predictions))
print(accuracy_score(y_test, predictions))

## Result: This classification model is not a conclusive model. This is because we analyze and predictive
## users' emotions/feelings/sentiments in sentiment analysis classification model.
## However, we don't have a column pointed the sentiment of descrptions in our dataset.
## We used bedroom numbers to label the classification model. But we don't think the bedroom numbers has relationships between users' emotions.
## And the result also figured it out that the accuracy score onlh has 52.63%
## If we want to improve the accuracy, we'd better have a column labeled sentiments in the dataset.

## ----------- Named-entity Recognition Analysis -------------
apt_data['NN'] = ''
apt_data['JJ'] = ''
apt_data['VB'] = ''
apt_data['GEO'] = ''

def apt_ner(chunker):
    treestruct = ne_chunk(pos_tag(word_tokenize(chunker)))
    entitynn = []
    entityjj = []
    entityg_air = []
    entityvb = []
    for y in str(treestruct).split('\n'):
        if 'GPE' in y or 'GSP' in y:
            entityg_air.append(y)
        elif '/VB' in y:
            entityvb.append(y)
        elif '/NN' in y:
            entitynn.append(y)
        elif '/JJ' in y:
            entityjj.append(y)
    stringnn = ''.join(entitynn)
    stringjj = ''.join(entityjj)
    stringvb = ''.join(entityvb)
    stringg = ''.join(entityg_air)
    return stringnn, stringjj, stringvb, stringg

i = 0
for x in apt_data['aptdescr']:
    entitycontainer = apt_ner(x)
    apt_data.at[i,'NN'] = entitycontainer[0]
    apt_data.at[i,'JJ'] = entitycontainer[1]
    apt_data.at[i,'VB'] = entitycontainer[2]
    apt_data.at[i,'GEO'] = entitycontainer[3]
    i += 1

apt_data['NN'].unique().tolist()
apt_data['JJ'].unique().tolist()
apt_data['VB'].unique().tolist()
apt_data['GEO'].unique().tolist()

len(apt_data['NN'].unique().tolist())
len(apt_data['JJ'].unique().tolist())
len(apt_data['VB'].unique().tolist())
len(apt_data['GEO'].unique().tolist())

## Result: The GEO column almost does not contain any information while the other three columns do.
## According to earlier results of sentiment analysis, apartment owners prefer to describe the
## attributes (aka strength) of apartment as much as possible to attractive rentors.
## It's unavoidable to use lots of noun, adjective, and verbs to descrive an apartment.
## Our result is consistant with the assumption (using length of lists) 


