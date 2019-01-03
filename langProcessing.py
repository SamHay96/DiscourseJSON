from flask import Flask
import nltk
import requests
import parser
import datetime
import json
from flask_restful import Api, Resource, reqparse
from nltk.corpus import treebank
from nltk import CFG
from nltk.corpus import stopwords

##TODO
##RESTFUL API
##Machine learning framework
##edgeBuilder


RA = ['Moreover', 'In addition', 'Additionally', 'Further', 'Further to this', 'Also', 'Besides','What is more','Because', 'Since', 'As', 'Insofar as','Therefore','Consequently','In consequence', 'As a result', 'Accordingly', 'Hence', 'Thus', 'For this reason', 'Because of this','If', 'In the event of', 'As long as', 'So long as', 'Provided that', 'Assuming that', 'Given that','On the contrary', 'As a matter of fact', 'In fact', 'Indeed', 'moreover', 'furthermore', 'in addition', 'also', 'further', 'alternatively', 'instead'
'besides', 'too', 'what is more', 'on top of this', 'on top of that', 'similarly', 'likewise', 'equally']
CA = ['Although', 'Even though', 'Despite the fact that', 'In spite of the fact that', 'Regardless of the fact that','However', 'On the other hand', 'In contrast', 'Yet']
r = requests.get("http://www.aifdb.org/json/7")

match = ""
targetNode=0
topNode=0
topEdge=0
nodeType=""
fromID=[]
app = Flask(__name__)
api = Api(app)

@app.route("/")
def hello():
	return "Hello, API"
if __name__ == '__main__':
	app.run(debug=True)

#createNode
#node ID and type
#Create new node to be linked with edges
def createNode(topNode,nodeType):
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
def createEdge(topEdge,nodeFrom,nodeTo):
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
	print("edgeID pre increment:",edgeCounter)
	eCounter =int(edgeCounter)
	if eCounter > topEdge:
		topEdge = eCounter
		return topEdge
	else:
		return topEdge


#counterSearch 
#JSON object from AIFB or in AIF format.	
#returns RA or CA based on discourse markers present in node and checks proposed node against existing discourse in AIFDB.
def counterSearch(rObject):
	rType=0
	cType=0
	for o in rObject['nodes']:
		nid = o['nodeID']
		n = int(nid)
		ntype = o["type"]
		text = nltk.ConcordanceIndex(nltk.word_tokenize(o['text']))
		for w in RA:
			ra = w.lower()
			if text.offsets(ra):
				print("\n")
				text.print_concordance(ra,0,0)
				fromID.append(n)
				rType=1
				print('\nMatch on nodeID:',n,"type:",ntype,"with word:",ra)
				for e in rObject['edges']:#check the node connections from finished product
							eid = e['edgeID']
							etid = e['toID']
							efid = e['fromID']
							if etid == n or efid == n and ntype == "RA":
								print("\n !! RA confirmed on edge:", eid,efid,etid,ntype)
							es=int(eid)	
		for x in CA:
			ca = x.lower()
			if text.offsets(ca):
				text.print_concordance(ca)
				print("CA")
				print(ca)
				for e in rObject['edges']:#check the node connections from finished product
							eid = e['edgeID']
							etid = e['toID']
							efid = e['fromID']
							if nid == etid or nid == efid and ntype == "CA":
								print("\nCA confirmed on edge:", eid)								
	ns=int(nid)
	if rType == 1:
		nodeType="RA"
		topNode=nodeCount(nid,ns)	
		topEdge=edgeCount(es,eid)
		targetNode = createNode(topNode,nodeType)
		for x in fromID:
			topEdge=createEdge(topEdge,x,targetNode)
	if cType == 1:
		nodeType="CA"
		topNode=nodeCount(n,e)	
		createNode(topNode,nodeType)
	return rObject



rObject = json.loads(r.text)
counterSearch(rObject)
print (rObject)





#print(rObject["edges"])
#print(rObject["nodes"])

