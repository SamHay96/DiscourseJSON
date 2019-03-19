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
#causal
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
raEvalData=[]
caEvalData=[]

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
	#for i in establishedRA: 
	#	print("Established RA:",i)
	#for i in establishedCA:
	#	print("Established CA",i)
	#for i in RANode:
	#	print("detected RA on node:",i)
	#for i in CANode:
	#	print("detected CA on node:",i)
	#for i in resultSetRAMarker:
	#	print("RA marker:",i)
	for i in resultSetCAMarker:
		print("CA marker:",i)

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
	while numerator <= 668:
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
	nid=topNode+1
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
	eid = eid + 1
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
		print(node)
	if ntype=="CA":
		CANode.append(node)

def proposeCA(nid):
	caNid = str(nid)
	caData = caNid 
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

def raEval(nid,text,marker,desc,polarity):
	nid=str(nid)
	ntext=str(text)
	nmarker=str(marker)
	ndescription=str(desc)
	npolarity=str(polarity)
	data='node id:',nid,'node content:',ntext,'node marker:',nmarker,'node desc:',ndescription,'node polarity:',npolarity
	raEvalData.append(data)

	
	
	
def caEval(nid,text,marker,desc,polarity):
	nid=str(nid)
	ntext=str(text)
	nmarker=str(marker)
	ndescription=str(desc)
	npolarity=str(polarity)
	data='node id:',nid,'node content:',ntext,'node marker:',nmarker,'node desc:',ndescription,'node polarity:',npolarity
	caEvalData.append(data)
	




#safe bet = new RA node for every 2 matches
#counterSearch 
#JSON object from AIFB or in AIF format.	
#returns RA or CA based on discourse markers present in node and checks proposed node against existing discourse in AIFDB.
def counterSearch(resp):
	rObject=resp

	#to check
	rtc=[]
	ctc=[]
	
	#print("Pre-search:")
	countAll(resp)
	rType=0
	cType=0

	for n in rObject['nodes']:
		nid = str(n['nodeID'])
		ntype = str(n["type"])
		detectNodeType(nid,ntype)
		processed=0
		

	for e in rObject['edges']:#check the node connections 
		eid = str(e['edgeID'])
		etid = str(e['toID'])
		efid = str(e['fromID'])
		for r in RANode:
			#print(eid,'vs',r)
			if r == etid:
				#print("boop1")
				rtc.append(etid)
			if efid == r:
				#print("boop2")
				rtc.append(efid)
	for r in rtc:
			if nid==r:
				print(str(n['text']))
	
	
	for o in rObject['nodes']:
		nid = str(o['nodeID'])
		n = int(nid)
		ntype = str(o["type"])
		token = nltk.word_tokenize(o['text'])
		text = nltk.ConcordanceIndex(token)
		sentoke = nltk.sent_tokenize(o['text'])
		sia=SentimentIntensityAnalyzer()
		polarity=getPolarity(sentoke)
		tagged = nltk.pos_tag(token)
		bg=ngrams(tagged,3)
		l = WordNetLemmatizer()
		for w in RA:
			ra = w.lower()
			if text.offsets(ra):
				if polarity =='positive':
					for z in PP:
						if w == z:
							detection='Positive polarity, PP marker '
							raEval(nid,str(o['text']),w,detection,polarity)
							proposeRA(n)
					for z in C:
						if w == z:
							detection='Positive polarity, causal marker'
							raEval(nid,str(o['text']),w,detection,polarity)
							proposeRA(n)
					for z in V:
						if w == z:
							detection='Positive polarity, veridical marker'
							raEval(nid,str(o['text']),w,detection,polarity)
							proposeRA(n)
					for z in NV:
						if w == z:
							detection='Positive polarity, non-veridical marker'
							raEval(nid,str(o['text']),w,detection,polarity)
							proposeRA(n)
					for z in T:
						if w == z:
							detection='Positive polarity, temporal marker'
							raEval(nid,str(o['text']),w,detection,polarity)
							proposeRA(n)
		for w in CA:
			ca = w.lower()
			if text.offsets(ca):
				if polarity =='negative':
					for z in NP:
						if w == z:
							detection='Negative polarity, NP marker '
							caEval(nid,str(o['text']),w,detection,polarity)
							proposeCA(n)
					for z in C:
						if w == z:
							detection='Negative polarity, casual marker'
							caEval(nid,str(o['text']),w,detection,polarity)
							proposeCA(n)
					for z in V:
						if w == z:
							detection='Negative polarity, veridical marker'
							caEval(nid,str(o['text']),w,detection,polarity)
							proposeCA(n)
					for z in NV:
						if w == z:
							detection='Positive polarity, non-veridical marker'
							caEval(nid,str(o['text']),w,detection,polarity)
							proposeA(n)
					for z in T:
						if w == z:
							detection='Positive polarity, temporal marker'
							caEval(nid,str(o['text']),w,detection,polarity)
							proposeCA(n)
	ns=int(nid)
	if proposedRA:
		nodeType='RA'
		es=eid
		topNode=nodeCount(nid,ns)
		topEdge=edgeCount(es,eid)
		targetNode = createNode(rObject,topNode,nodeType)
		for i in proposedRA:
			connections=0
			if connections < 4:
				topEdge=createEdge(rObject,topEdge,targetNode,i)
				connections=+1
	if proposedCA:
		for i in proposedCA:
			nodeType='RA'
			es=eid
			topNode=nodeCount(nid,ns)
			topEdge=edgeCount(es,eid)
			targetNode = createNode(rObject,topNode,nodeType)
			connections=0
			if connections < 4:
				topEdge=createEdge(rObject,topEdge,targetNode,i)
				connections=+1
	countAll(resp)
	return rObject

#
#All Araucaria Nodesets
#
createDataSet() 
for d in dataset:
	nObject=counterSearch(d)
#print(len(proposedCA),'CAs proposed')
#print(len(proposedRA),'RAs proposed')
print(len(RANode),'RA nodes found')
print(len(CANode),'CA nodes found')
#
#Create Evaluation Dataset
#
#with open('radata.json', 'w') as o:
#    json.dump(raEvalData, o)
#with open('cadata.json', 'w') as o:
#    json.dump(caEvalData, o)

#
#Create Established Dataset
#
with open('estradata.json', 'w') as o:
    json.dump(RANode, o)
with open('estcadata.json', 'w') as o:
    json.dump(CANode, o)


#
#Single Nodeset
#
#key=7
#chooseNodeSet(key)
#counterSearch(rObject)

#
#Start API service
#
#@app.route("/")
#def hello():
#	key=input("Enter the key you want to use: ")
#	rObject = chooseNodeSet(key)
#	nObject = counterSearch(rObject)
#	return jsonify(nObject)
#if __name__ == '__main__':
#	app.run(debug=True)
