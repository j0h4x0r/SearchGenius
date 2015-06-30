# SearchGenius

An information retrieval system that exploits user-provided relevance feedback to improve the search results returned by Bing.

## How to run?

### Dependency libraries (Python)

* requests
* nltk

### To install these libraries

# set python library path

```
:~$ mkdir lib
:~$ export PYTHONPATH=$PYTHONPATH:~/lib
# install python packages
:~$ pip install --user requests
:~$ pip install --user nltk
:~$ python
>>> import nltk
>>> nltk.download()
>>> d
>>> book # download corpus
>>> exit()
```

### To run the code

python main.py

## System Design

### Summary

The system takes a query (separated by spaces), target precision, and Account Key(listed at the end of this document) as input, and runs until the target precision is reached. For more accurate results, we incorporated nltk.stopwords and string.punctuations in python to filter out unmeaningful words previous adding to our TF-IDF dictioinary.

### Functions

```python
main()
# Main function is a loop that runs until the target precision is reached
# Target precision and query inputs are also obtained here

startSearch(queryStr, times, accKey)
# Start the search using Bing API
#  Params queryStr: query string
#  Params times: iteration time
#  Params accKey: Bing account key

calcPrecision(data)
# calculate the precision after receiving the feedback from user
#  Params data: search results from Bing API and the feedback
#  Return: precision

adjustQuery(queryStr, data)
# add query words according to the feedback
#  Params queryStr: query string
#  Params data: search results from Bing API and the feedback
#  Return: new query string

tfidfvec(query, data)
# compute the TF-IDF vectors of documents and the query
#  Params query: query string
#  Params data: search results from Bing API and the feedback
#  Return: query vector, document vectors, features of a vector(words list)

rocchio(qvec, tfidf, data, word_set, old_query)
# implementation of the Rocchio algorithm
#  Params qvec: query vector
#  Params tfidf: document vectors
#  Params data: search results from Bing API and the feedback
#  Params word_set: features of a vector(words list)
#  Params old_query: old query string
#  Return: new query string
```

## Query-modification Method

The system applied Rocchio algorithm for relevance feedback process [Relevance feedback and query expansion](http://nlp.stanford.edu/IR-book/pdf/09expand.pdf).

The rocchio() function takes in five parameters as stated above

- old_query was converted into df-vector
- for each element of old_query, increment it with corresponding tfidf[] if it was marked as relevant.
- for each element of old_query, decrement it with corresponding tfidf[] if it was marked as irrelevant. 
- sort the updated query vector, and return the top two words and add them to the new query returned.
- because we have filtered unuseful words (stopwords, puctuations) in the first place, we don't need to worry about adding them to the new query.
- after experimenting with different queries, we find that setting parameters as alpha = 2.0, beta = 0.75, gamma = 0.15 performs best.
