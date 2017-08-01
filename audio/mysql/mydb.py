#coding:utf-8
import MySQLdb

def getHandleforDb(name):

    conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='root',
            db = name,
            charset='utf8'
            )
    return conn



def insert(conn,fsql):

    cur = conn.cursor()
    sql =''
    i = 0
    while True:

	try:
	    sql += fsql.next()
	    if sql[-2] == ';':
	#            print sql,
                try:
	            cur.execute(sql)
                    conn.commit()
                    i += 1
                except Exception as e:
#                    print e
                    pass
                sql = ''
        except StopIteration:
            print "insert the %d statement Successful" % i
            break


    cur.close()
    conn.close()

if __name__ == '__main__':
    fs = open("./0-9.txt")
#    print fs.read()
    conn = getHandleforDb('skytv')
    insert(conn,fs)
