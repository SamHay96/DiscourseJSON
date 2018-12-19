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


#createNode
#node ID and type
#Create new node to be linked with edges
def createNode(topNode,nodeType):
	nid=topNode
	nid+=1
	time = str(datetime.datetime.now())
	nType=nodeType
	rObject["nodes"].append({'nodeID':nid})
	rObject["nodes"].append({'text':''})
	rObject["nodes"].append({'type':nType})
	rObject["nodes"].append({'timestamp':time})
	print("Created node at:",nid,"with type",nType)
	#print(rObject["nodes"])
	return nid
#
#
#
def createEdge(topEdge,nodeFrom,nodeTo):
	eid=int(topEdge)
	eid+1
	edgeFrom = nodeFrom
	edgeTo = nodeTo
	rObject["edges"].append({'edgeID':eid,'fromID':edgeFrom,'toID':edgeTo,'formEdgeID':'null'})
	#print("Created edge with ID:",eid,"from node:",edgeFrom,"toID",edgeTo)
	#print(rObject["edges"])

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
	raCounter = 0
	rType=0
	cType=0
	caCounter = 0

	for o in rObject['nodes']:
		nid = o['nodeID']
		n = int(nid)
		ntype = o["type"]
		text = nltk.ConcordanceIndex(nltk.word_tokenize(o['text']))
		#print(o['text'])
		#text = o['text']	
		for w in RA:
			ra = w.lower()
			if text.offsets(ra):
				print("\n")
				text.print_concordance(ra,0,0)
				#print("RA")
				#print(ra)
				node=nid
				fromID.append(node)
				rType=1
				print('\nMatch on nodeID:',node,"type:",ntype,"with word:",ra)
				for e in rObject['edges']:#check the node connections from finished product
							eid = e['edgeID']
							etid = e['toID']
							efid = e['fromID']
							#print("checking assumed RA edgeID: ", eid, "going from node:",efid,"to node: ",etid)
							if etid == node or efid == node and ntype == "RA":
								print("\n !! RA confirmed on edge:", eid,efid,etid,ntype)
								#raCounter += 1
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
							#print('\nMatch on nodeID:',node,"type:",ntype,"with word:",ca)
							if nid == etid or nid == efid and ntype == "CA":
								print("\nCA confirmed on edge:", eid)
								#caCounter += 1				
	ns=int(nid)
	if rType == 1:
		nodeType="RA"
		topNode=nodeCount(nid,ns)	
		topEdge=edgeCount(es,eid)

		print(type(topEdge),topEdge)
		print("TopNode should be:",nid,"is",topNode)
		print("TopEdge should be:",eid,"is",topEdge)
		targetNode = createNode(topNode,nodeType)
		for x in fromID:
			#print("es",es)
			#print("top edge:",topEdge)
			#print("node to link:",targetNode,"to node:",x)
			createEdge(topEdge,x,targetNode)
			#print("topEdge:",topEdge)
	if cType == 1:
		nodeType="CA"
		topNode=nodeCount(n,e)	
		createNode(topNode,nodeType)


		#caCounter+=1
		#print(r.status_code)
	#print("Detected",raCounter,"RA link(s)")
	#print("Detected",caCounter,"CA link(s)")	


rObject = json.loads(r.text)
counterSearch(rObject)


