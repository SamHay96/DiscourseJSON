# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify
import nltk
import requests
import parser
import datetime
import json
from flask_restful import Api, Resource, reqparse
from nltk.corpus import treebank
from nltk.corpus import sentiwordnet as swn
from nltk import CFG
from nltk.corpus import stopwords

##TODO
##RESTFUL API
##Machine learning framework


RA = ["Above all", "additionally", "again", "also"," as well as", "at the same time", "besides", "equally important", "furthermore", "in addition", "least of all", "likewise", "moreover", "more importantly", "most of all", "too", "not only", "what’s more", "as", "as a consequence of", "as a result"," as it is", "as it was", "because", "consequently", "due to ","hence", "in response", "so", "since", "therefore", "thus", "equally", "exactly", "identically", "in much the same way"," in relation to", "like", "matching", "of little difference", "resembling", "same as", "similar to", "similarly"," as illustrated by", "as revealed by", "for example", "for instance", "in other words", "in particular"]
CA = ["A striking difference", "accepting that", "admittedly", "after all, against", "allowing that", "although", "and yet", "but", "by contrast", "despite", "doubtless", "even so", "for all that", "fortunately", "granted that", "however", "in another way", "in contrast", "in one way", "in opposition to", "in spite of", "instead", "it is true that", "it may well be", "naturally", "nevertheless", "nonetheless", "on one hand", "on the other hand", "on the contrary","otherwise", "to differ from", "to oppose", "unlike", "until", "versus"," while it is true", "yet", "against", "although", "be that as it may", "besides", "despite this fact", "in one way", "instead", "nonetheless"]


CANode=[]
RANode=[]
fromID=[]
proposedRA=[]
proposedCA=[]
establishedRA=[]
establishedCA=[]
dataset=[]

resultSetRAMarker=[]
resultSetCAMarker=[]

rObject=None
match = ""
targetNode=0
topNode=0
topEdge=0
nodeType=""
app = Flask(__name__)
api = Api(app)
#r = requests.get("http://www.aifdb.org/json/7")
#rObject = json.loads(r.text)

#def printDataSets():
	#for i in proposedRA:
	#	print("proposed RA:",i)
	#for i in proposedCA:
	#	print("Proposed RA:",i)
	#for i in establishedRA:
	#	print("Established RA:",i)
	#for i in establishedCA:
	#	print("Established CA:",i)
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

def sentAnalysis():
	breakdown = swn.senti_synset('breakdown.n.03')
	print(breakdown)
		
def createDataSet():
	header="araucaria/"
	numerator=8
	footer=".json"
	while numerator <= 100:
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

def proposeRA(nid,text,marker):
	raNid = str(nid)
	raText=str(text)
	raMarker=str(marker)
	raData = raNid + '|' + raText + '|' + raMarker
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
#safe bet = new RA node for every 2 matches
#counterSearch 
#JSON object from AIFB or in AIF format.	
#returns RA or CA based on discourse markers present in node and checks proposed node against existing discourse in AIFDB.
def counterSearch(resp):
	rObject=resp
	#print("Pre-search:")
	#countAll(resp)
	#print(rObject)
	rType=0
	cType=0
	for n in rObject['nodes']:
		nid = str(n['nodeID'])
		ntype = str(n["type"])
		detectNodeType(nid,ntype)
	for o in rObject['nodes']:
		nid = str(o['nodeID'])
		n = int(nid)
		ntype = str(o["type"])
		token = nltk.word_tokenize(o['text'])
		text = nltk.ConcordanceIndex(nltk.word_tokenize(o['text']))
		print(token)
		for w in RA:
			ra = w.lower()
			#print(n,"RA:",ra)
			if text.offsets(ra):
				print("\n")
				#text.print_concordance(ra,0,0)
				fromID.append(n)
				rType=1
				#print('\nMatch on nodeID:',n,"type:",ntype,"with word:",ra)
				t = str(o['text'])
				proposeRA(n,t,ra)
				for e in rObject['edges']:#check the node connections from finished product
					eid = str(e['edgeID'])
					etid = str(e['toID'])
					efid = str(e['fromID'])
					es=int(eid)
					for f in RANode:
						if etid==nid or efid==nid:
							if etid == f or efid == f:
								#print("\n !! RA confirmed on edge:", eid,efid,etid,ntype)
								detectRA(n,t,ra)
								es=int(eid)	
		for x in CA:
			ca = x.lower()
			#print(n,"CA:",ca)
			if text.offsets(ca):
				#text.print_concordance(ca)
				fromID.append(n)
				cType=1
				#print('\nMatch on nodeID:',n,"type:",ntype,"with word:",ca)
				t = str(o['text'])
				proposeCA(n,t,ca)
				for e in rObject['edges']:#check the node connections from finished product
					eid = e['edgeID']
					etid = e['toID']
					efid = e['fromID']
					es=int(eid)
					for f in CANode:
						if etid==nid or efid==nid:
							if etid == f or efid == f:
								#print("\n !! RA confirmed on edge:", eid,efid,etid,ntype)
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


#@app.route("/")
#def hello():
	#try:
	#key=input("\nEnter the key you want to use: \n")
	#key=7
	#rObject = chooseNodeSet(key)
	#nObject = counterSearch(rObject)
	#print("CounterSearch pass")
#	return jsonify(nObject)
	#except:
	#	print("Counter search failed")
		#return "This isnt working"
#if __name__ == '__main__':
#	app.run(debug=True)


createDataSet()
key=7
rObject = chooseNodeSet(key)
#counterSearch(rObject)

#for d in dataset:
#	nObject = counterSearch(d)
	#printDataSets()
resultsFilter(proposedRA,proposedCA)
sentAnalysis()
#print("\nResult set RA length: " + str(len(resultSetRAMarker)))
#print("Result set CA length: " + str(len(resultSetCAMarker)))


raCount = nltk.FreqDist(resultSetRAMarker)
caCount = nltk.FreqDist(resultSetCAMarker)

#print("\nMost frequent RA markers")
#for w, f in raCount.most_common(50):
#    print(u'{}:{}'.format(w, f))
#print("\nMost frequent CA markers")
#for w, f in caCount.most_common(50):
#    print(u'{}:{}'.format(w, f))
#print(rObject["edges"])
#print(rObject)

