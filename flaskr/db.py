import mysql.connector
	
class DB(): 
    def connect(self, buffered=False):
        self.cnx = mysql.connector.connect(user='fabian',password='fabsen123', host='127.0.0.1', database='depot')
        self.cursor = self.cnx.cursor(buffered=buffered)


    def close(self):
        self.cursor.close()
        self.cnx.close()
