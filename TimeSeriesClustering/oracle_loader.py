# -*- coding: utf-8 -*-
# Python 3.6.2 AMD64
# Required Package: cx_Oracle
# execute "pip install cx_Oracle" at CMD before running this script

import sys
import csv
import logging 
import gc
import cx_Oracle

logging.basicConfig(level=logging.DEBUG)
 
orcl = cx_Oracle.connect("system","ORACLEsh123","127.0.0.1:1521/orcl") # connect(user id,user password,database path/database id)
logging.info("oracle version: " + orcl.version)
curs = orcl.cursor()

printHeader = True
sql = "select * from tab" # get a list of all tables
curs.execute(sql)


for row_data in curs:
    if not row_data[0].startswith("BIN$"): # skip recycle bin tables
        tableName = row_data[0]
        logging.info("now loading table:" + tableName)
        csv_file_path = 'E:\\oracle_data\\' + tableName + '.csv'
        outputFile = open(csv_file_path,'w')
        output = csv.writer(outputFile)
        sql = "select * from " + tableName
        try:
            curs2 = orcl.cursor()
            curs2.execute(sql)
        except:
            logging.warning("sql execution failed on table %s, now start loading next table"%tableName)
            continue
            
        if printHeader: # add column headers if requested
            cols = []
            for col in curs2.description:
                cols.append(col[0])
            output.writerow(cols)
        rows_counter = 1
        for row_data in curs2: # add table rows
            logging.debug("read %sth row of %s"%(rows_counter,tableName))
            output.writerow(row_data)
            rows_counter += 1
        outputFile.close()
        logging.info("table %s loading complete"%tableName)
        
logging.info("data extraction complete")
orcl.close()





