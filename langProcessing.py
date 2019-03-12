 # -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify
import nltk
import requests
import parser
import datetime
import json
from flask_restful import Api, Resource, reqparse
from nltk import CFG
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import stopwords
from nltk.corpus import treebank
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag, map_tag
from nltk.tree import Tree
from nltk.util import ngrams

##TODO
##RESTFUL API
##Machine learning framework
#pos_tag

RA = ["Above all", "additionally", "again", "also"," as well as", "at the same time", "besides", "equally important", "furthermore", "in addition", "least of all", "likewise", "moreover", "more importantly", "most of all", "too", "not only", "what’s more", "as", "as a consequence of", "as a result"," as it is", "as it was", "because", "consequently", "due to ","hence", "in response", "so", "since", "therefore", "thus", "equally", "exactly", "identically", "in much the same way"," in relation to", "like", "matching", "of little difference", "resembling", "same as", "similar to", "similarly"," as illustrated by", "as revealed by", "for example", "for instance", "in other words", "in particular"]
CA = ["A striking difference", "accepting that", "admittedly", "after all, against", "allowing that", "although", "and yet", "but", "by contrast", "despite", "doubtless", "even so", "for all that", "fortunately", "granted that", "however", "in another way", "in contrast", "in one way", "in opposition to", "in spite of", "instead", "it is true that", "it may well be", "naturally", "nevertheless", "nonetheless", "on one hand", "on the other hand", "on the contrary","otherwise", "to differ from", "to oppose", "unlike", "until", "versus"," while it is true", "yet", "against", "although", "be that as it may", "besides", "despite this fact", "in one way", "instead", "nonetheless"]

#positivePolarity
PP=["After","and","as","as soon as","because","before","considering" "that","ever" "since","for", "given that","if","in case","in order that","in that","in so far as","now", " now that","on the grounds that","once","seeing as","since","so","so that","the instant","the moment","then","to the extent that","when","whenever"]
#negativePolarity
NP=["Although","but","even if","even though","even when","only if","only when","or",   "or else","though","unless","until","whereas","yet"]
#veridical
V=["after", "although","and","as","as soon as","because","but","considering that","even though","even when","ever since","for", "given that","in order that","in that","in so far as","now","now that","on the grounds that","once","only when","seeing as","since","so","so that","the instant","the moment","then","though","to the extent that","until","when","whenever", "whereas","while","yet"]
#non-veridical
NV=["Assuming that","even if","if","if ever",  "if only",  "incase","on condition that","on the assumption that","only if","or","or else","supposing that","unless"]
#additive
A=["and","but","whereas"]
#temporal
T=["After","as soon as","before","ever since","now",  "now that","once","until","when","whenever"]
#casual
C=["Although","because","even though","for", "given that","if","if ever"," incase","on the condition that","on the assumption that","on the grounds that","provided that","providing that","so","so that","supposing that","though","unless"]

CANode=[]
RANode=[]
fromID=[]
proposedRA=[]
proposedCA=[]
establishedRA=[]
establishedCA=[]
dataset=[]
posTotal=[]
negTotal=[]
resultSetRAMarker=[]
resultSetCAMarker=[]

rObject=None
match = ""
polarity =""
mtype=""
targetNode=0
topNode=0
topEdge=0
nodeType=""
app = Flask(__name__)
api = Api(app)
#r = requests.get("http://www.aifdb.org/json/7")
#rObject = json.loads(r.text)

def printDataSets():
	#for i in proposedRA:
	#	print("proposed RA:",i)
	#for i in proposedCA:
	#	print("Proposed RA:",i)
	for i in establishedRA: 
		print("Established RA:",i)
	for i in establishedCA:
		print("Established CA:",i)
	#for i in RANode:
	#	print("detected RA:",i)
	#for i in CANode:
	#	print("detected CA:",i)
	#for i in resultSetRAMarker:
	#	print("RA marker:",i)
	#for i in resultSetCAMarker:
	#	print("CA marker:",i)

def resultsFilter(proposedRA,proposedCA):
	for i in proposedRA:
		j=str(i)
		result = [x.strip() for x in j.split('|')]	
		marker=str(result[2])
	#	print(result[2])
		resultSetRAMarker.append(marker)
	for i in proposedCA:
		j=str(i)
		result = [x.strip() for x in j.split('|')]
		marker=str(result[2])
	#	print(result[2])
		resultSetCAMarker.append(marker)
		
def createDataSet():
	header="araucaria/"
	numerator=8
	footer=".json"
	while numerator <= 101:
		request=header+"nodeset"+str(numerator)+".json"
		with open(request,'r') as x:
			item = json.load(x)
			dataset.append(item)
			numerator+=1

def countAll(resp):
	rObject=resp
	nodeTotal=0
	edgeTotal=0
	caTotal=0
	iNodeTotal=0
	raTotal=0
	for o in rObject['nodes']:
		nodeTotal+=1
		nType=str(o['type'])
		if nType == "CA":
			caTotal+=1
		elif nType == "RA":
			raTotal+=1
		elif nType == "I":
			iNodeTotal+=1
	for e in rObject['edges']:
		edgeTotal+=1
	#print("Total nodes: ",nodeTotal,"Total edges: ", edgeTotal,"Total CA:", caTotal, "Total RA: ", raTotal,"Total iNode: ",iNodeTotal)


def chooseNodeSet(key):
	#createDataSet()
	#for x in dataset:
		#print(x)
	nodekey=str(key)
	#print("Key =",key)
	request="http://www.aifdb.org/json/"+str(nodekey)
	r = requests.get(request)
	rObject = json.loads(r.text)
	#print("Request ran successfully",rObject)
	return rObject

#createNode
#node ID and type
#Create new node to be linked with edges
def createNode(resp,topNode,nodeType):
	rObject=resp
	nid=topNode
	nid+=1
	time = str(datetime.datetime.now())
	nType=nodeType
	rObject["nodes"].append({'nodeID':nid,'text':'','type':nType,'timestamp':time})
	#print("Created node at:",nid,"with type",nType)
	return nid
#
#
#
def createEdge(resp,topEdge,nodeFrom,nodeTo):
	rObject=resp
	eid=int(topEdge)
	eid+=1
	edgeFrom = nodeFrom
	edgeTo = nodeTo
	rObject["edges"].append({'edgeID':eid,'fromID':edgeFrom,'toID':edgeTo,'formEdgeID':'null'})
	#print("Created edge with ID:",eid,"from node:",edgeFrom,"toID",edgeTo)
	return eid
	

#nodeCount
#take last nodeID and edgeID
#returns new ID after comparing IDs and incrementing the highest one.
def nodeCount(nodeCounter,top):
	topNode=int(top)
	IDCounter=int(nodeCounter)
	if IDCounter > topNode:
		IDCounter = topNode
		return topNode
	else:
		return topNode
#
#
#
def edgeCount(edgeCounter,top):
	topEdge=int(top)
	#print("edgeID pre increment:",edgeCounter)
	eCounter =int(edgeCounter)
	if eCounter > topEdge:
		topEdge = eCounter
		return topEdge
	else:
		return topEdge

def proposeRA(nid):
	raNid = str(nid)
	raData = raNid
	proposedRA.append(raData)
	#	for i in proposedRA:
	#	print(i)

#
#Add node id, text and marker to established set
#
def detectRA(nid,text,marker):
	raNid = str(nid)
	raText=str(text)
	raMarker=str(marker)
	raData = raNid + '|' + raText + '|' + raMarker
	establishedRA.append(raData)

def detectCA(nid,text,marker):
	caNid = str(nid)
	caText=str(text)
	caMarker=str(marker)
	caData = caNid + '|' + caText + '|' + caMarker	
	establishedCA.append(caData)

def detectNodeType(nid,ntype):
	node=str(nid)
	nodetype=str(ntype)
	if ntype =="RA":
		RANode.append(node)
	if ntype=="CA":
		CANode.append(node)

def proposeCA(nid,text,marker):
	caNid = str(nid)
	caText=str(text)
	caMarker=str(marker)
	caData = caNid + '|' + caText + '|' + caMarker	
	proposedCA.append(caData)
	#for i in proposedCA:
	#	print(i)

def getPolarity(r):
	sentoke=r
	sia=SentimentIntensityAnalyzer()
	for s in sentoke:
		ss=sia.polarity_scores(s)
		poscore=str(ss['pos'])
		negscore=str(ss['neg'])
		if poscore>negscore:
			polarity="positive"
			return polarity
		elif negscore>poscore:
			polarity="negative"
			return polarity



#returns RA or CA based on discourse markers present in node and checks proposed node against existing discourse in AIFDB.
def counterSearch(resp):
	rObject=resp
	#print("Pre-search:")
	countAll(resp)
	rType=0
	cType=0		
	for o in rObject['nodes']:
		nid = str(o['nodeID'])
		t = str(o['text'])
		n = int(nid)
		ntype = str(o["type"])
		detectNodeType(nid,ntype)
		token = nltk.word_tokenize(o['text'])
		text = nltk.ConcordanceIndex(token)
		sentoke = nltk.sent_tokenize(o['text'])
		polarity = getPolarity(sentoke)
		for e in rObject['edges']:#check the node connections from finished product
			eid = str(e['edgeID'])
			etid = str(e['toID'])
			efid = str(e['fromID'])
			tagged = nltk.pos_tag(token)
			bg=ngrams(tagged,3)
			l = WordNetLemmatizer()
			#print('lemmatizer results for marker',ra,":",l.lemmatize(ra))
			processed=0
		for b in bg:
			if processed == 0:
				for c in b:
					y = nltk.ConcordanceIndex(c)
					for w in RA:
						ra = w.lower()
						if y.offsets(ra):
							print('detection on' ,ra)
							if polarity =='positive':
								print('positive polarity detected')
								for z in PP:
									if y.offsets(z):
										print('Positive Polarity marker')
										processed=1
										fromID.append(n)
										rType=1
										proposeRA(n)
										processed=1
										synset=list(swn.senti_synsets(ra, "a"))
										es=int(eid)
										for f in RANode:
											if etid==nid or efid==nid:
												if etid == f or efid == f:
													detectRA(n,t,ra)
													es=int(eid)
								for z in C:
									if y.offsets(z):
										print('positive and casual')
										processed=1
										fromID.append(n)
										rType=1
										print(n)
										proposeRA(n)
										processed=1
										synset=list(swn.senti_synsets(ra, "a"))
										for e in rObject['edges']:#check the node connections from finished product
											eid = str(e['edgeID'])
											etid = str(e['toID'])
											efid = str(e['fromID'])
											es=int(eid)
											for f in RANode:
												if etid==nid or efid==nid:
													if etid == f or efid == f:
														detectRA(n,t,ra)
														es=int(eid)	
								for z in V:
									if y.offsets(z):
										if y.offsets(z):
											print('positive verdict')
											processed=1
											fromID.append(n)
											rType=1
											proposeRA(n)
											processed=1
											synset=list(swn.senti_synsets(ra, "a"))
											for e in rObject['edges']:#check the node connections from finished product
												eid = str(e['edgeID'])
												etid = str(e['toID'])
												efid = str(e['fromID'])
												es=int(eid)
												for f in RANode:
													if etid==nid or efid==nid:
														if etid == f or efid == f:
															detectRA(n,t,ra)
															es=int(eid)
								for z in NV:
									if y.offsets(z):
										if y.offsets(z):
											print('positively not a verdict')
											processed=1
											fromID.append(n)
											rType=1
											proposeRA(n,t,ra)
											processed=1
											synset=list(swn.senti_synsets(ra, "a"))
											for e in rObject['edges']:#check the node connections from finished product
												eid = str(e['edgeID'])
												etid = str(e['toID'])
												efid = str(e['fromID'])
												es=int(eid)
												for f in RANode:
													if etid==nid or efid==nid:
														if etid == f or efid == f:
															detectRA(n,t,ra)
															es=int(eid)
								for z in T:
									if y.offsets(z):
											print('temporal pos')
											processed=1
											fromID.append(n)
											rType=1
											proposeRA(n,t,ra)
											processed=1
											synset=list(swn.senti_synsets(ra, "a"))
											for e in rObject['edges']:#check the node connections from finished product
												eid = str(e['edgeID'])
												etid = str(e['toID'])
												efid = str(e['fromID'])
												es=int(eid)
												for f in RANode:
													if etid==nid or efid==nid:
														if etid == f or efid == f:
															detectRA(n,t,ra)
															es=int(eid)	
														
					for x in CA:
						ca = x.lower()
						#print(n,"CA:",ca)
						tagged = nltk.pos_tag(token)
						bg=ngrams(tagged,3)
						for b in bg:
							for x in b:
								y = nltk.ConcordanceIndex(x)
								if y.offsets(ca):
									for c in b:
										#print(b)
										z = nltk.ConcordanceIndex(c)
										if z.offsets(ca):
											for d in c:
												if d =='IN':
													t = str(d)
													proposeCA(n,t,ca)
													processed=1
													for e in rObject['edges']:#check the node connections from finished product
														eid = e['edgeID']
														etid = e['toID']
														efid = e['fromID']
														es=int(eid)
														for f in CANode:
															if etid==nid or efid==nid:
																if etid == f or efid == f:
																	detectCA(n,t,ca)
																	ns=int(nid)
	if rType == 1:
		nodeType="RA"
		topNode=nodeCount(nid,ns)	
		topEdge=edgeCount(es,eid)
		targetNode = createNode(rObject,topNode,nodeType)
		for x in fromID:
			topEdge=createEdge(rObject,topEdge,x,targetNode)
	if cType == 1:
		nodeType="CA"
		topNode=nodeCount(nid,ns)	
		topEdge=edgeCount(es,eid)
		targetNode = createNode(rObject,topNode,nodeType)
		for x in fromID:
			topEdge=createEdge(rObject,topEdge,x,targetNode)
	#print("\nPost-search:")
	countAll(resp)
	#print("\nDetected",len(proposedRA),"potential RA(s)")
	#print("Detected",len(proposedCA),"potential CA(s)\n")
	return rObject

createDataSet()
key=7
rObject = chooseNodeSet(key)
counterSearch(rObject)



#print("\nMost frequent RA markers")
#for w, f in raCount.most_common(50):
#    print(u'{}:{}'.format(w, f))
#print("\nMost frequent CA markers")
#for w, f in caCount.most_common(50):
#    print(u'{}:{}'.format(w, f))
#print(rObject["edges"])
#print(rObject)



	#for i in breakdown:
	#	print(i)
#for x in CA:
#	t = nltk.sent_tokenize(x)
#	tagged = nltk.pos_tag(t)
#	dumb = [(word,map_tag('en-ptb','universal',tag))for word, tag in tagged]
	

#for d in dataset:
#	nObject = counterSearch(d)
#	for o in nObject['nodes']:
#		print(o['text'])
		
	
#POS TAGGING
#for x in RA:
#	t = nltk.sent_tokenize(x)
#	tagged = nltk.pos_tag(t)
#	print('RA:',tagged)
#for x in CA:
#	t = nltk.sent_tokenize(x)
#	tagged = nltk.pos_tag(t)
#	print('CA:',tagged)
#	dumb = [(word,map_tag('en-ptb','universal',tag))for word, tag in tagged]
#	breakdown = swn.senti_synsets(x,'r')
	#print(dumb)
#print("Actual RA:", len(establishedRA))
#print("Actual CA:", len(establishedCA))
#print("Detected RA:", len(proposedRA))
#print("Detected CA:", len(proposedCA))
#print("CA:", len(CANode))
#print("RA:", len(RANode))
for i in RANode:
	print("RA:",i)
for i in CANode:
	print("CA",i)
#	printDataSets()
#resultsFilter(proposedRA,proposedCA)
#sentAnalysis()
#print("\nResult set RA length: " + str(len(resultSetRAMarker)))
#print("Result set CA length: " + str(len(resultSetCAMarker)))
#raCount = nltk.FreqDist(resultSetRAMarker)
#caCount = nltk.FreqDist(resultSetCAMarker)

