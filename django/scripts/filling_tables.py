from psycopg2 import connect
from dotenv import load_dotenv
from os import getenv
from faker import Faker


load_dotenv()
credentials = {
    'host' : getenv('PG_HOST'),
    'port' : int(getenv('PG_PORT')),
    'user' : getenv('PG_USER'),
    'password' : getenv('PG_PASSWORD'),
    'dbname' : getenv('PG_DBNAME')
}

connection = connect(**credentials)
cursor = connection.cursor()
request = "INSERT INTO library.author (full_name) VALUES ('{0}')"
fake = Faker()
for _ in range(2000):
    full_name: str = str(fake.name())
    cursor.execute(request.format(full_name))

connection.commit()
cursor.close()
connection.close()

