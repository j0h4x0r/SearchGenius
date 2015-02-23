import requests
import urllib
import sys
import codecs
from lxml import etree
import nltk

rootURL = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
# To be substituted
accKey = 'gQ+gama5GAfLoQmix8AKEn5Nop24Tlu34tRapNPOImI'
# iteration times
times = 1

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
	data = [{} for i in range(10)]
	# for test only
	tree = etree.fromstring(result.text.encode('ascii', 'replace'))
	#tree = etree.fromstring(result.text)
	metas = tree.findall('.//m:properties', tree.nsmap)
	#set data dict values
	for i in range(10):
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
# Adjust query - key part
def adjustQuery(queryStr, data):
	### start calculating TF-IDF scores
	tf={}  
	df={}
	all_doc=[]
	all_word=[]
	tfidf={}
	N=len(data)
	print 'Indexing results ....'
	for i in xrange(N):
		#tokenize each description, more pre-processing measure to be added...
		tmp_dj=nltk.word_tokenize(data[i]['description'])
		all_doc.append(tmp_dj)
		for word in tmp_dj: 
			word=word.lower() #here we use lower case words for all results
			if word not in tf[i]:
				tf[i][word]=1
			else:
				tf[i][word]=tf[i].get(word)+1
			if word not in all_word:
				all_word.append(word)
	for word in all_word:
		df=0
		for i in xrange(N):
			if word in all_doc[i]:
				df=df+1
		tfidf[word]=(float(tf[i][word])/sum(tf[i].itervalues()))*math.log((float(N)/df),2)
	return rocchio(tfidf,queryStr)
#	
def rocchio(tfidf,queryStr):

	print 'Augmenting by: [' ,queryStr,']'
	return queryStr
if __name__ == '__main__': main()