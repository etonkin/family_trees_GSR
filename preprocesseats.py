# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from xml.dom import minidom
from datetime import datetime;
import time
import sqlite3
from sqlite3 import Error
 
 
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    print("Trying to connect to file");
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn;
    except Error as e:
        print(e)
    #finally:
    #    if conn:
    #        conn.close()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# create a database connection
conn=create_connection("eatsdata.db");

sql_create_authorityrecord_table= """ CREATE TABLE IF NOT EXISTS authorityrecord (
                                        id integer PRIMARY KEY,
                                        eatsid text NOT NULL,
                                        eatsrecord text,
                                        xmlid text,
                                        shorteatsid text
                                    ); """

sql_create_nameassertion_table= """ CREATE TABLE IF NOT EXISTS  nameassertion(
                                        id integer PRIMARY KEY,
                                        authrecord text NOT NULL,
                                        authpref text,
                                        displayform text
                                    ); """
 
def add_authority_record(conn, eatsid,eatsrecord,xmlid,shorteatsid):
    sql = ''' INSERT INTO authorityrecord(eatsid, eatsrecord,xmlid, shorteatsid)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql,(eatsid, eatsrecord,xmlid, shorteatsid))
    conn.commit()
    return cur.lastrowid

def add_nameassertion(conn, authrecord,authpref,displayform):
    sql = ''' INSERT INTO nameassertion(authrecord,authpref,displayform)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql,(authrecord,authpref,displayform))
    print(authrecord+","+authpref+","+displayform);
    conn.commit()
    return cur.lastrowid
# create tables
if conn is not None:
    # create projects table
    create_table(conn, sql_create_authorityrecord_table)
 
    # create tasks table
    create_table(conn, sql_create_nameassertion_table)
else:
    print("Error! cannot create the database connection.")
print("Node names from EATS");
nodenamesfromeats={}
nodedisplaynamesfromeats={}
# https://data.kdl.kcl.ac.uk/dataset/gsr/resource/5e6ca1c7-d620-4ef7-80a1-eeb66ac97d63
curtime=time.time()
print("Starting at "+str(curtime));
mydoc=minidom.parse("eatsml.xml");
differ=time.time()-curtime;
print("Ending. Time taken: "+str(differ));
#for i in G.nodes():
#    nodenamesfromeats[i]="unknown";
#print(nodenamesfromeats);
for j in mydoc.getElementsByTagName('authority_record'):
    eatsid=j.getAttribute('eats_id');
    eatsrecord=j.getElementsByTagName('authority_system_id')[0].firstChild.nodeValue;
    xmlid=j.getAttribute('xml:id')
    #print(xmlid);
    #print(eatsrecord)
    shorteatsrecord=eatsrecord.lstrip('entity-');
    add_authority_record(conn,eatsid, eatsrecord, xmlid, shorteatsrecord)

    #print(shorteatsrecord)
    #if shorteatsrecord in nodenamesfromeats.keys():
        # we need this info
    #    print("This is in keys");
    #    displayformtext=shorteatsrecord;
    #    nodenamesfromeats[shorteatsrecord]=xmlid;
     #   # now find the preferred name
for auth in mydoc.getElementsByTagName('name_assertion'):
         #  <name_assertion authority_record="authority_record-22210" is_preferred="false" xml:id="name_assertion-90126" eats_id="90126" type="name_type-2" language="language-1" script="script-1">
    authrecord=auth.getAttribute('authority_record');
    authpref=auth.getAttribute('is_preferred');
    displayform=auth.getElementsByTagName('display_form') #firstChild.nodeValue;
    for ix in displayform:
        if(ix.firstChild!=None):
            print("Trying to add name assertion");
            displayformtext=ix.firstChild.nodeValue;
            add_nameassertion(conn,authrecord,authpref,displayformtext);
        #if(displayform!=None):
        #    if(displayform[0].firstChild!=None):
        #            displayformtext=displayform[0].firstChild.nodeValue;
        #nodedisplaynamesfromeats[shorteatsrecord]=displayformtext;
