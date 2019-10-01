import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import glob
import random
import string

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
G=nx.Graph()

# Get big list of all entities (by looking at filesystem)

fileset=glob.glob("*.xml")

for i in fileset:
    iname=i.rstrip('.xml');

    # iname is the name without the extension of the entity
    # now add this as a node
    G.add_node(iname);

from xml.dom import minidom


def scandown( elements, indent ):
    for el in elements:
        print("   " * indent + "nodeName: " + str(el.nodeName) )
        print("   " * indent + "nodeValue: " + str(el.nodeValue) )
        print("   " * indent + "childNodes: " + str(el.childNodes) )
        scandown(el.childNodes, indent + 1)

edgelabelset={};
tupleedgelabelset={};
# Now, open each of the files and see if there are any family relationships in there
identifierlist={}
for i in fileset:
    # open file
    #print("Trying to parse "+i);
    thisentity=i.rstrip('.xml').lstrip('entity-');
    try:
        mydoc=minidom.parse(i);    
        identifierset=mydoc.getElementsByTagName('crm:P131F.is_identified_by');
        for ident in identifierset:
            if ident.getAttribute('rdf:datatype').rstrip('/')=="http://www.cidoc-crm.org/rdfs/cidoc-crm-english-label#E82.Actor_Appellation":
                identifierlist[thisentity]=ident.firstChild.nodeValue.decode('utf-8').strip();
        test=mydoc.getElementsByTagName('crm:P107B.is_brother_in');
        for bro in test:
            thetest=bro.getElementsByTagName('crm:P107F.has_brother');
            for abro in thetest:
                bname=abro.getAttribute('rdf:resource').rstrip('/').lstrip('entity-');
                G.add_edge(thisentity,bname,brother=1);
                edgelabelset[thisentity+bname]='brother';
                edgelabelset[bname+thisentity]='brother';
        test=mydoc.getElementsByTagName('crm:P107F.has_sister');
        for asis in test:
            sname=asis.getAttribute('rdf:resource').rstrip('/').lstrip('entity-');
            G.add_edge(thisentity,sname,sister=1);
            edgelabelset[thisentity+sname]='sister';
            edgelabelset[sname+thisentity]='sister';
        test=mydoc.getElementsByTagName('crm:P97F.from_father');
        for afather in test:
            fname=afather.getAttribute('rdf:resource').rstrip('/').lstrip('entity-');
            G.add_edge(thisentity,fname,father=1);
            edgelabelset[fname+thisentity]='child';
            edgelabelset[thisentity+fname]='father';
        test=mydoc.getElementsByTagName('crm:P96F.by_mother');
        for amother in test:
            fname=amother.getAttribute('rdf:resource').rstrip('/').lstrip('entity-');
            G.add_edge(thisentity,fname,mother=1);
            edgelabelset[fname+thisentity]='child';
            edgelabelset[thisentity+fname]='mother';
        test=mydoc.getElementsByTagName('crm:P107F.has_nephew');
        for anephew in test:
            fname=anephew.getAttribute('rdf:resource').rstrip('/').lstrip('entity-');
            G.add_edge(thisentity,fname,nephew=1);
            edgelabelset[fname+thisentity]='uncle';
            edgelabelset[thisentity+fname]='nephew';
    except:
        print("Couldn't parse");
    #for j in test: 
        #textval=" ".join(t.nodeValue for t in j[0].childNodes if t.nodeType == t.TEXT_NODE)
        #print(textval);
    #scandown(test,0);
        #print(j.firstChild.nodeValue);

# remove isolate (nodes with no edges);
#isolatelist=nx.isolates(G);
G2=G.copy();
G.remove_nodes_from(nx.isolates(G2));
print("Nodes left in G (contains only nodes with edges)")
print(G.number_of_nodes())
print("nodes left in G2");
print(G2.number_of_nodes())
#print(count(G2.nodes()))
#print(G.edges())

#print(type(G.nodes()))
#print(type(G.edges()))
orderedsubgraphs=sorted(nx.connected_component_subgraphs(G), key=len, reverse=True);
counter=0;
for i in orderedsubgraphs:
    print(i.edges());
    counter=counter+1;
    iedgelabels={};
    edgelabelident="";
    for edge in i.edges():
        (a,b)=edge;
        print(a+b)
        print(edgelabelset[a+b]);
        iedgelabels[(a,b)]=edgelabelset[a+b];
        edgelabelident=edgelabelident+"('"+a+"','"+b+"'):'"+edgelabelset[a+b]+"',";
        print(edgelabelident);
    fil=open("familytree-rank"+str(counter)+".dot","w+b")
    fil.write("digraph D {\n");
    fil.write("\
    edge [dir=none];\
    node [shape=box];\
    ")
    print(len(i));
    f = plt.figure()
    #nx.draw(i,ax=f.add_subplot(111));
    #nx.draw_networkx_labels(i,ax=f.add_subplot(111),pos=nx.spring_layout(i));
    pos=nx.spring_layout(i);
    fig=plt.figure(figsize=(10,10))    
    nx.draw(i,pos,font_size='8',edge_color='black',width=1,linewidths=1,\
node_size=100,node_color='pink',alpha=0.9,\
labels={node:node for node in i.nodes()})
    nx.draw_networkx_edge_labels(i,pos,edge_labels=iedgelabels,font_color='red');
    fig.savefig("graph2.png")
    # now what we really need to do is give each one a level
    # the nodeset in i is i.nodes
    # for every node seek out siblings (brother, sister)
    print("Individual nodes");
    nodelevels={};
    for nn in i.nodes():
        levelid=randomString(stringLength=10);
        for ee in i.edges(nn):
            strvers=ee[0]+ee[1];
            if strvers in  edgelabelset.keys():
                relation=edgelabelset[strvers];
                print(strvers+","+relation);
                if relation=="sister" or relation=="brother":
                    if ee[1] not in nodelevels.keys():
                        nodelevels[ee[1]]=levelid;
                        nodelevels[ee[0]]=levelid;

    for nn in i.nodes():
        nnlabel=str(nn);
        if nn in identifierlist.keys():
            if identifierlist[nn]!=None:
                nnlabel=identifierlist[nn];
        fil.write("\""+nn+"\"   [label=\""+nnlabel+"\", shape=box, regular=1, color=\"blue\"] ;\n")
    inv = {}
    for key, val in nodelevels.iteritems():
        inv[val] = inv.get(val, []) + [key]
    for kk in inv.keys():
        print("Values for "+kk);
        print(inv[kk]);
        samerankstr="->".join(inv[kk]);
        fil.write("{rank=same; "+samerankstr+"};\n");# same rank
    # now for parenthood
    for nn in i.nodes():
        for ee in i.edges(nn):
            strvers=ee[0]+ee[1];
            if strvers in edgelabelset.keys():
                relation=edgelabelset[strvers];
                if(relation=="mother"): # or relation=="uncle"):
                    fil.write(ee[1]+"->"+ee[0]+" [label=\"mother\",arrowsize=0.0]; \n");
                if(relation=="father"): # or relation=="uncle"):
                    fil.write(ee[1]+"->"+ee[0]+" [label=\"father\",arrowsize=0.0]; \n");
                if(relation=="nephew"):
                    fil.write(ee[0]+"->"+ee[1]+" [label=\"nephew\", arrowsize=0.0]; \n");
    print(nodelevels);
    fil.write("}");
    fil.close();
