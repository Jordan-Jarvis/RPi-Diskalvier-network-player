import psycopg2
import pandas

connection = psycopg2.connect(
    host = 'database',
    # database = 'rpimidi',
    user = 'test',
    password = 'keystore',
    port='5432'
)
connection.autocommit = True
title="JAKEJAKE"
rating=3
filelocation="dev/null"
BPM=120
len=134.4
numplays=3
tmp = connection.cursor()
sql= f"""INSERT INTO Song (title, rating, filelocation, BPM, len, numplays)
VALUES ('{title}', {rating}, '{filelocation}', {BPM}, {len}, {numplays});"""
tmp.execute(sql)
connection.commit()
tmp.close()