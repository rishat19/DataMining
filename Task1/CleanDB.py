import sys
import psycopg2

connection = psycopg2.connect(
    database='',
    user='postgres',
    password='aws48916011',
    host='dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com',
    port='5432',
)

delete_query = "TRUNCATE  vk_words"
connection.autocommit = True
cursor = connection.cursor()
cursor.execute(delete_query)
connection.commit()
connection.close()
