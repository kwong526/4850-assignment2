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
sql = """CREATE TABLE buy_event
    (id INT PRIMARY KEY AUTO_INCREMENT,
    purchase_id VARCHAR(250) NOT NULL,
    traceId VARCHAR(250) NOT NULL, 
    stockTicker VARCHAR(10) NOT NULL,
    sellVolume INT NOT NULL,
    buyPrice FLOAT(15,2) NOT NULL,
    buyDate VARCHAR(100) NOT NULL,
    date_created VARCHAR(100) NOT NULL)
    """
cursor.execute(sql)

# Creating table as per requirement
sql = """CREATE TABLE price_event
    (id INT PRIMARY KEY AUTO_INCREMENT,
    traceId VARCHAR(250) NOT NULL,
    stockTicker VARCHAR(10) NOT NULL,
    timespanUnit VARCHAR(25) NOT NULL,
    timespanLen INT NOT NULL,
    dateStartMonth INT NOT NULL,
    dateStartDay INT NOT NULL,
    dateSort VARCHAR(10) NOT NULL,
    date_created VARCHAR(100) NOT NULL)
    """
cursor.execute(sql)

conn.commit()
conn.close()
