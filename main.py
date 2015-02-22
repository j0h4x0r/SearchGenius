import requests
import urllib
import sys
import codecs
from lxml import etree

rootUri = 'https://api.datamarket.azure.com/Bing/Search/v1/Web'
# To be substituted
accKey = 'gQ+gama5GAfLoQmix8AKEn5Nop24Tlu34tRapNPOImI'
# iteration times
times = 1

def calcPrecison(data):
	rel = 0
	for item in data:
		if item['rel']:
			rel += 1
	return float(rel) / len(data)

def startSearch(queryStr):
	print '========================'
	print 'Round', times
	print 'Query:', queryStr
	print '========================'
	uri = rootUri + "?Query=" + urllib.quote_plus("'" + queryStr + "'")
	result = requests.get(uri, auth=(accKey, accKey))
	# Parse result
	data = [{} for i in range(10)]
	# for test only
	tree = etree.fromstring(result.text.encode('ascii', 'replace'))
	#tree = etree.fromstring(result.text)
	metas = tree.findall('.//m:properties', tree.nsmap)
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
	precision = calcPrecison(data)
	print '========================'
	print 'Feedback Summary'
	print 'Query:', queryStr
	print 'Precision:', precision
	return data, precision

# Adjust query - key part
def adjustQuery(queryStr, data):
	###

if __name__ == '__main__':
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