import requests
import urllib
import sys
import codecs
from lxml import etree
import nltk
import itertools
import math
# Stop words could be choosed ffrom :http://www.nltk.org/book/ch02.html
rootURL = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
# To be substituted
accKey = 'gQ+gama5GAfLoQmix8AKEn5Nop24Tlu34tRapNPOImI'
# iteration times
times = 1
# top N documents we should do calculation on
N = 10
# rocchio parameters
alpha = 1.0
beta = 0.75
gamma = 0.15

def main():
	queryStr = raw_input('Please input the query word(s), separated by space: ')
	target = raw_input('Please input the target precision: ')
	try:
		target = float(target)
		if target < 0 or target > 1:
			raise ValueError
	except ValueError:
		print 'Illegal precision!'
		sys.exit()

	data, precision = startSearch(queryStr)

	while precision < target:
		print 'Still below than the target precision of', target
		queryStr = adjustQuery(queryStr, data)
		times += 1
		data, precision = startSearch(queryStr)
	print 'Target precision reached. Done.'

#calculate precison each iteration:
def calcPrecison(data):
	rel = 0
	for item in data:
		if item['rel']:
			rel += 1
	return float(rel) / len(data)

#pre-process text: str_source is the text needed to be processed; replace all words to char
def str_replace(str_source,char,*words):
    str_temp=str_source    
    for word in words:
        str_temp=str_temp.replace(word,char)
    return str_temp	

def startSearch(queryStr):
	print '========================'
	print 'Round', times
	print 'Query:', queryStr
	print '========================'
	uri = rootURL + "?Query=" + urllib.quote_plus("'" + queryStr + "'")
	result = requests.get(uri, auth=(accKey, accKey))
	# Parse result
	data = [{} for i in range(N)]
	# for test only
	tree = etree.fromstring(result.text.encode('ascii', 'ignore'))
	#tree = etree.fromstring(result.text)
	metas = tree.findall('.//m:properties', tree.nsmap)
	#set data dict values
	for i in range(N):
		title = metas[i].find('d:Title', tree.nsmap).text
		description = metas[i].find('d:Description', tree.nsmap).text
		url = metas[i].find('d:Url', tree.nsmap).text
		# record data
		data[i]['url'] = url
		data[i]['title'] = title
		data[i]['description'] = description
		print 'Result', i + 1
		print '['
		print ' URL:', url
		print ' Ttile:', title
		print ' Summary:', description
		print ']'
		rel = raw_input('\nRelevant (Y/N)?')
		data[i]['rel'] = True if rel == 'Y' or rel == 'y' else False
	#calculate precsion
	precision = calcPrecison(data)
	print '========================'
	print 'Feedback Summary'
	print 'Query:', queryStr
	print 'Precision:', precision
	return data, precision

# # Adjust query - key part
# def adjustQuery(queryStr, data):
# 	### start calculating TF-IDF scores
# 	tf={}  
# 	df={}
# 	all_doc=[]
# 	all_word=[]
# 	tfidf={}
# 	print 'Indexing results ....'
# 	for i in xrange(N):
# 		#tokenize each description, more pre-processing measure to be added...
# 		tmp_dj=nltk.word_tokenize(data[i]['description'])
# 		all_doc.append(tmp_dj)
# 		for word in tmp_dj: 
# 			word=word.lower() #here we use lower case words for all results
# 			if word not in tf[i]:
# 				tf[i][word]=1
# 			else:
# 				tf[i][word]=tf[i].get(word)+1
# 			if word not in all_word:
# 				all_word.append(word)
# 	for word in all_word:
# 		df=0
# 		for i in xrange(N):
# 			if word in all_doc[i]:
# 				df=df+1
# 		tfidf[word]=(float(tf[i][word])/sum(tf[i].itervalues()))*math.log((float(N)/df),2)
# 	return rocchio(tfidf,queryStr)

# Adjust query - key part
def adjustQuery(queryStr, data):
	qvec, tfidf, word_set = tfidf(queryStr, data)
	new_queryStr = rocchio(qvec, tfidf, data, word_set, queryStr)
	return new_queryStr

def tfidf(query, data):
	# extract docs form raw data
	docs = [item['description'] for item in data]
	# build a list of tokenized docs
	words_list = []
	for doc in docs:
		# you may want to do more pre-processing here...
		words_list.append([word.lower() for word in nltk.word_tokenize(doc)])
	# a list of all words, with duplicates
	all_words = list(itertools.chain(*words_list))
	# a list of all words, without duplicates - for vector bases
	word_set = list(set(all_words))
	
	# construct tf vectors
	tf_vecs = [0 for i in range(N)]
	for i in range(N):
		tf_vecs[i] = [words_list[i].count(w) for w in word_set]
	# compute idf values
	idf_all_words = list(itertools.chain(*[set(doc_words) for doc_words in words_list]))
	idfs = [math.log(float(N) / idf_all_words.count(w), 10) for w in word_set]
	# compute tf-idf & normalize
	tfidf = [0 for i in range(N)]
	for i in range(N):
		tfidf[i] = [tf * idf for tf, idf in zip(tf_vecs[i], idfs)]
		nom = math.sqrt(sum(x**2 for x in tfidf[i]))
		tfidf[i] = [x / nom for x in tfidf[i]]

	# now let's work on the query vector
	qwords = [word.lower() for query.split()]
	# tf vector
	qvec = [qwords.count(w) for w in word_set]
	# tf-idf vector
	qvec = [tf * idf for tf, idf in zip(qvec, idfs)]
	# normalize
	nom = math.sqrt(sum(x**2 for x in qvec))
	qvec = [x / nom for x in qvec]
	return qvec, tfidf, word_set

#to be added...
def rocchio(qvec, tfidf, data, word_set, old_query):
	# record relevant & irrelevant count
	rel_count = sum(1 for item in data if item['rel'])
	irr_count = N - rel_count
	# compute new qvec
	new_qvec = [alpha * x for x in qvec]
	for i in range(N):
		if data[i]['rel']:
			new_qvec = [q + beta / float(rel_count) * r for q, r in zip(new_qvec, tfidf[i])]
		else:
			new_qvec = [q - gamma / float(irr_count) * r for q, r in zip(new_qvec, tfidf[i])]
	# extract new query, order matters
	qwords = [word.lower() for old_query.split()] # may need restore later
	# top 2 largest
	t1 = 0 new_qvec[0] >= new_qvec[1] else 1
	t2 = 0 if t1 == 1 else 1
	maxv1 = new_qvec[t1]
	maxv2 = new_qvec[t2]
	for i in range(len(new_qvec)):
		if new_qvec[i] > maxv1:
			maxv2 = maxv1
			t2 = t1
			maxv1 = new_qvec[i]
			t1 = i
		elif new_qvec[i] > maxv2:
			maxv2 = new_qvec[i]
			t2 = i
	qwords.append(word_set[t1])
	if new_qvec[t2] > 0:
		qwords.append(word_set[t2])
	qwords.sort(key = lambda w: new_qvec[word_set.index(w)], reverse = True)
	queryStr = ' '.join(qwords)

	return queryStr

if __name__ == '__main__': main()