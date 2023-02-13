import sys, os, sqlite3, string, json

def getme(dbname,sql):
    
    con = sqlite3.connect(dbname)

    cur = con.cursor()
    #print ("cursor",cur)
    qdir = os.getenv("SQL_QUERY_DIR")
    fname = os.path.join(qdir,sql)

    qf = open(fname,'r')
    qd = qf.readlines()
    clean = ""
    #print (qd)
    for q in qd:
        if "." not in q[0]:
            clean += q
    #print (clean)
    res = cur.execute(clean.strip())
    result = res.fetchall()
    dicto = {}
    #print (result)
    
    # translate the tuple into a dictionary
    for i in result:
        #print (i, type(i))
        name = i[0]
        
        if len(i) == 2:
            data = i[1]
        else:
            data = []
            for d in i[1:]:
                data.append(d)
        dicto[name]=data
    #print ("dicto",dicto)
    
   
     
    return dicto
        
if __name__ == "__main__":
    mem = getme("mem.db", "peak-summary.sql")
     
    time = getme("time.db", "event-summary.sql")
    
    print ("mem",mem,"\n")
    print ("time",time,"\n")
