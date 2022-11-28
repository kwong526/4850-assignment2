import mysql.connector

# establishing the connection
conn = mysql.connector.connect(
    user="clinton",
    password="clintonwong!",
    host="acit3855-kafkalab.westus3.cloudapp.azure.com",
    database="kafka",
)

cursor = conn.cursor()

# Creating table as per requirement
sql = """DROP TABLE buy_event, price_event"""
cursor.execute(sql)

conn.commit()
conn.close()
