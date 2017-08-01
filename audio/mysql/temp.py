#!/usr/bin/python
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

def select(conn):
    cur = conn.cursor()
    sql = "select * from music where name='hello'"
    ret =cur.execute(sql)
    


if __name__ == '__main__':
    conn = getHandleforDb("skytv")
    select(conn)
