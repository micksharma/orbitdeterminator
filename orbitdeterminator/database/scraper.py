"""
This code populates the database with tle entries.

There are 2 codes for database: init_database.py and scraper.py

Important: Run init_database.py before scraper.py

Note: Password filed is empty during database connection. Insert password for
      mysql authentication.
"""

import time
import hashlib
import MySQLdb
import requests
from bs4 import BeautifulSoup

def database_connect():
    """
    Initializes database connection and selects corresponding database

    Args:
        NIL

    Return:
        db : database object
        d : connection flag (0: success)
    """

    db = MySQLdb.connect(host="localhost", user="root", passwd="mysql")
    cursor = db.cursor()
    d = cursor.execute('use cubesat')
    # print('Database selected')
    return db, d

def string_to_hash(tle):
    """
    Converts satellite name to its corresponding md5 hexadecimal hash

    Args:
        tle : satellite name

    Return:
        sat_hash : md5 hexadecimal hash
    """

    md5_hash = hashlib.md5(tle.encode())
    sat_hash = md5_hash.hexdigest()
    return sat_hash

def update_tables(db):
    """
    Updating tables with new TLE values.

    There are 3 attributes in the tables are: time, line1, line2

    Args:
        db : database object

    Return:
        NIL
    """
    page = requests.get("https://www.celestrak.com/NORAD/elements/cubesat.txt")
    soup = BeautifulSoup(page.content, 'html.parser')
    tle = list(soup.children)
    tle = tle[0].splitlines()

    success = 0
    error = 0
    ts = time.time()
    cursor = db.cursor()
    for i in range(0, len(tle), 3):
        sat_hash = string_to_hash(tle[i])

        try:
            sql = 'INSERT INTO %s values(\'%s,\', \'%s,\', \'%s,\');\
            ' %(str(sat_hash), str(ts), tle[i+1], tle[i+2])
            cursor.execute(sql)
            d = db.commit()
        except Exception:
            error = error + 1
            # print(tle[i] + ' - Error: Table not found')
        else:
            success = success + 1

    print('Tables updated : ' + str(success))
    # print('Error/Total : ' + str(error) + '/' + str(error+success))
    db.close()

if __name__ == "__main__":
    db,_ = database_connect()
    update_tables(db)
