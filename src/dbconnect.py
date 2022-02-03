import psycopg2
import pandas

connection = psycopg2.connect(
    host = 'database',
    database = '...',
    user = '...',
    password = '...',
    port='5432'
)
users = pandas.read_sql('SELECT * FROM users', connection)
