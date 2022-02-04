import psycopg2
import pandas

connection = psycopg2.connect(
    host = 'database',
    # database = 'rpimidi',
    user = 'test',
    password = 'keystore',
    port='5432'
)
