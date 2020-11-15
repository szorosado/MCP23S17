
import sqlite3 ## Importieren der sqlite3 Library
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # fix für visual studio code
database = sqlite3.connect(os.path.join(BASE_DIR, "test-db.db")) # Verbinden der Datenbank (test-db)
cursor = database.cursor() # Ein Cursor erstellen um die Daten 

with open(os.path.join(BASE_DIR, "setup.sql"), 'r') as sql_file:
	cursor.executescript(sql_file.read()) # Inhalt der setup.sql ausführen
	database.commit() # die Datenbank mit den neuen Inhalt der Setup.sql synchronisieren

### Beispiel mit Klasse
"""
	class A:
		def __init__(self):
			BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # fix für visual studio code
			self.database = sqlite3.connect(os.path.join(BASE_DIR, "test-db.db")) # Verbinden der Datenbank (test-db)
			cursor = self.database.cursor() # Ein Cursor erstellen um die Daten 

			with open(os.path.join(BASE_DIR, "setup.sql"), 'r') as sql_file:
				cursor.executescript(sql_file.read()) # Inhalt der setup.sql ausführen
				self.database.commit() # die Datenbank mit den neuen Inhalt der Setup.sql synchronisieren
"""

## Ein Eintrag hinzufügen: 
cursor = database.cursor() # Ein Cursor erstellen um eine Anfrage zum Server zu schicken
cursor.execute("INSERT INTO highscore(player_name, score) VALUES(\"test\",  5);") # Hinzufügen eines neues Eintrags
database.commit() # Synchronisieren
## Ende

##
"""
	class A:
		def __init__(self):
			BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # fix für visual studio code
			self.database = sqlite3.connect(os.path.join(BASE_DIR, "test-db.db")) # Verbinden der Datenbank (test-db)
			cursor = self.database.cursor() # Ein Cursor erstellen um die Daten 

			with open(os.path.join(BASE_DIR, "setup.sql"), 'r') as sql_file:
				cursor.executescript(sql_file.read()) # Inhalt der setup.sql ausführen
				self.database.commit() # die Datenbank mit den neuen Inhalt der Setup.sql synchronisieren
		
		def eintrag(self):
			cursor = database.cursor() # Ein Cursor erstellen um eine Anfrage zum Server zu schicken
			cursor.execute("INSERT INTO highscore(player_name, score) VALUES(\"test\",  5);") # Hinzufügen eines neues Eintrags
			self.database.commit()
"""
### ALT
