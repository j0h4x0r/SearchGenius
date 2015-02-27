import itertools
import nltk
import math

N = 10
alpha = 1.0
beta = 0.75
gamma = 0.15

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
	qwords = [word.lower() for word in query.split()]
	# tf vector
	qvec = [qwords.count(w) for w in word_set]
	# tf-idf vector
	qvec = [tf * idf for tf, idf in zip(qvec, idfs)]
	# normalize
	nom = math.sqrt(sum(x**2 for x in qvec))
	qvec = [x / nom for x in qvec]
	return qvec, tfidf, word_set

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
	qwords = [word.lower() for word in old_query.split()] # may need restore later
	# top 2 largest
	# t1 = 0 if new_qvec[0] >= new_qvec[1] else 1
	# t2 = 0 if t1 == 1 else 1
	# maxv1 = new_qvec[t1]
	# maxv2 = new_qvec[t2]
	# for i in range(len(new_qvec)):
	# 	if i == 0 or i == 1:
	# 		continue
	# 	if new_qvec[i] > maxv1:
	# 		maxv2 = maxv1
	# 		t2 = t1
	# 		maxv1 = new_qvec[i]
	# 		t1 = i
	# 	elif new_qvec[i] > maxv2:
	# 		maxv2 = new_qvec[i]
	# 		t2 = i
	# print t1, t2
	# qwords.append(word_set[t1])
	# if new_qvec[t2] > 0:
	# 	qwords.append(word_set[t2])
	# qwords.sort(key = lambda w: new_qvec[word_set.index(w)], reverse = True)
	sorted_qvec = [(new_qvec[i], i) for i in range(len(new_qvec))]
	sorted_qvec.sort(reverse = True)
	quota = 2
	for vec_val, index in sorted_qvec:
		if quota <= 0:
			break
		elif word_set[index] not in qwords:
			qwords.append(word_set[index])
			print vec_val
			quota -= 1
		else:
			print vec_val
	qwords.sort(key = lambda w: new_qvec[word_set.index(w)], reverse = True)
	queryStr = ' '.join(qwords)

	return queryStr


# data = [
# 	{'description': 'Gates Corporation is Powering Progress? in the Oil &amp; Gas, Energy, Mining, Marine, Agriculture, Transportation and Automotive Industries.', 'rel': False},
# 	{'description': 'Gates Chevy World in Mishawaka serves South Bend, Michiana and Elkhart Chevrolet customers with new and used vehicles. Stop by for a test drive today!', 'rel': False},
# 	{'description': 'Product Description... The position and lock gate helps parents keep their children safe from ...', 'rel': False},
# 	{'description': 'Gates offers a complete line of original equipment (OE) automotive aftermarket products and solutions, including automotive hose, belts, &amp; accessories.', 'rel': False},
# 	{'description': 'Kevin Dye from Gates performs an acoustic version of the very first song Gates wrote together. He also discusses how he started playing music, ...', 'rel': False},
# 	{'description': 'Driveway Gates - Automatic Gates The high-quality driveway gates from GateCrafters.com come in a wide variety of options to ...', 'rel': False},
# 	{'description': 'With the tantalizing hickory barbecue smell drawing the customer through the ranch-style doors, he is immediately greeted.', 'rel': False},
# 	{'description': 'Gates high quality belt &amp; hose solutions support your energy, exploration, extraction, infrastructure, agriculture &amp; transportation needs.', 'rel': False},
# 	{'description': 'Safe &amp; durable baby gates will keep your baby safe. Choose from a large assortment of baby gates including extra wide gates to suit your needs. Shop today.', 'rel': False},
# 	{'description': 'William Henry "Bill" Gates III (born October 28, 1955) is an American business magnate, philanthropist, investor, computer programmer, and inventor. Gates ...', 'rel': True}
# ]

data = [
	{'description': 'Gates Corporation is Powering Progress? in the Oil & Gas, Energy, Mining, Marine, Agriculture, Transportation and Automotive Industries.', 'rel': False},
	{'description': 'The Gates Foundation?s effort to eradicate polio offers the chance to protect millions of children from paralysis forever', 'rel': False},
	{'description': 'With the tantalizing hickory barbecue smell drawing the customer through the ranch-style doors, he is immediately greeted.', 'rel': False},
	{'description': 'William Henry "Bill" Gates III (born October 28, 1955) is an American business magnate, philanthropist, investor, computer programmer, and inventor. Gates originally ...', 'rel': True},
	{'description': 'Kevin Dye from Gates performs an acoustic version of the very first song Gates wrote together. He also discusses how he started playing music, ...', 'rel': False},
	{'description': 'Product Description... Easy Open Extra Wide Safety Gate boasts 100 percent steel ...', 'rel': False},
	{'description': 'Driveway Gates - Automatic Gates The high-quality driveway gates from GateCrafters.com come in a wide variety of options to ...', 'rel': False},
	{'description': 'Gates offers a complete line of original equipment (OE) automotive aftermarket products and solutions, including automotive hose, belts, & accessories.', 'rel': False},
	{'description': 'Gates high quality belt & hose solutions support your energy, exploration, extraction, infrastructure, agriculture & transportation needs.', 'rel': False},
	{'description': 'America\'s richest man, Bill Gates, is using his billions to effect major social change around the globe. The Bill & Melinda Gates Foundation has given away $30 ...', 'rel': True}
]

qvec, tfidf, word_set = tfidf('gates', data)
newq = rocchio(qvec, tfidf, data, word_set, 'gates')
print newq
print word_set