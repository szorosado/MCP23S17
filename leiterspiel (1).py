from rpi_mcp import mcp

class Buttongame:
    def __init__(self):
        mcp.raw_write_config('A', 0) # Alles auf Output
        # mcp.setup
        # Wenn du einen Pin konfigurieren willst 
        # Beispiel: mcp.setup('A', 3, mcp.INPUT) # Der Pin 3 wird als Input konfiguriert

    def __buttonStatus(self):
        return mcp.input('B', 7) # Taster Status auslesen

    def setAllLEDoff(self):
        mcp.raw_output('A', 0) # Alle Leds ausschalten

    def mainloop(self):
        while True:
            while not self.__buttonStatus(): # falls taster nicht gedrückt wird
                mcp.output("A", 0, True) # LED 0 (an)
                mcp.output("A", 1, False) # LED 1 (aus)

            while self.__buttonStatus(): # falls taster gedrückt wird
                mcp.output("A", 0, False) # LED 0 (aus)
                mcp.output("A", 1, True) # LED 1 (an)

        time.sleep(0.1)


class Database:
    def __init__(self):
        self.__cConnection = sqlite3.connect(os.path.join(os.path.dirname(__file__), "test-datenbank.sqlite3")) # Der Name wird vorgegeben
        self.cCursor = self.__cConnection.cursor() # Erstellen von einem cursor damit eine Query ausgeführt werden kann (Zeile. 40)

    def createTable(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.sql"), 'r') as sql_file: # Lesen der Date in die Variable (sql_file)
        	self.cCursor.executescript(sql_file.read()) # Inhalt der setup.sql ausführen
        	self.__cConnection.commit() # die Datenbank mit den neuen Inhalt der Setup.sql synchronisieren

    def saveState(self, sPlayername, iGameLevel):

        ## (Query = Anfrage die zum Server / Datei gehen )
        """
        Alles mit 
            INSERT INTO
            SELECT 
            DELETE FROM"""
        self.cCursor.execute("""
        INSERT INTO tblHighscore (Playername, Score) 
        VALUES('%s', %d);"""
                             % (sPlayername, iGameLevel))
        self.__cConnection.commit() # Synchronisieren der Datenbank 

    def closeConnection(self):
        self.__cConnection.close() # Schließen der Datenbank


class Laddergame:
    def __init__(self, pinButton, portabButton, portabLEDs):
        # Button = Taster
        self.iPinButton = pinButton # Der Pin vom Taster ()
        self.sPortButton = portabButton # Der Port
        self.sPortLED = portabLEDs # Portab der LED-Seite

        self.__oDB = Database() # erstellen der Datenbank Instanz
        mcp.raw_write_config(self.sPortLED, 0) # Alles zum Output definieren
        self.iGameLevel = 0 # Das aktuelle Level vom Spiel
        self.bWon = False # eine Hilfsvariable um der zu gucken ob der Spieler gewonnen hat

        self.__fLEDlastBlink = time.time() # die letzte Zeit wo die LED geblickt hat
        self.fLEDblinkInterval = random.randint(5, 8)/10 # Die Zeitspanne wie die LED blickt
        # self.fLEDblinkInterval = 1
        self.__bLEDStatus = False # Hilfsvariable um zu prüfen, ob der Led an/aus ist


    def setAllLEDoff(self):
        # Alle leds ausschalten
        mcp.raw_output(self.sPortLED, 0) 
        #self.__oMCP.write_output(self.sPortLED, 0b00000000)

    def blinkLED(self, iLEDPin): # Hier wird eine Led zum blinken gebracht
        fNow = time.time()
        if fNow - self.__fLEDlastBlink > self.fLEDblinkInterval: # Überprüfen ob die Differenz der aktuellen Zeit mit der letzten Blink Zeit den Blink Interval entspicht
            self.__bLEDStatus = not self.__bLEDStatus # aktuellen Status negieren 
            self.__fLEDlastBlink = fNow # Hier wird die letzte Zeit 
            mcp.output(self.sPortLED, iLEDPin, self.__bLEDStatus) # Aktivieren vom gegeben Parameter (iLEDPIN) mit den aktuellen Status

    def levelUp(self): # Hier wird das aktuelle Level vom Speieler erhöht. 
        if self.iGameLevel is not 7: # Überprüfung: ist das Spiel zuende? wenn ja ist das Level >= 7
            mcp.output(self.sPortLED, self.iGameLevel, True) # Hier wird die aktuelle Led angeschaltet. 
            #self.__oMCP.set_output_pin(self.sPortLED, self.iGameLevel, True)
            self.fLEDblinkInterval -= 0.07 # Blinkinterval wird um 0.07 gesenkt
            self.iGameLevel += 1 # Levelup 
        else:
            self.bWon = True # Spieler hat gewonnen gg

    def gameReset(self): # Hier wird das ganze Spiel neugestartet
        self.iGameLevel = 0 # Level wieder auf 0 gesetzt
        self.bWon = False # Hilfsvariable wird auf False gesetzt 
        self.fLEDblinkInterval = random.randint(5, 8)/10 # Blinkinterval wird wieder random gesetzt
        # self.fLEDblinkInterval = 1
        for iLEDPin in range(0, 8):
            mcp.output(self.sPortLED, iLEDPin, False)#self.__oMCP.set_output_pin(self.sPortLED, iLEDPin, False)
        self.mainloop() # Starten wieder die mainloop

    def gameOver(self): # Die Funktion wird ausgelöst wenn das Spiel zuende ist 
        iBlinkCounter = 4 
        iBlinkDelay = 0.3
        while iBlinkCounter:
            iBlinkCounter -= 1
            for iLEDPin in range(0, 8):
                #self.__oMCP.set_output_pin(self.sPortLED, iLEDPin, False)
                mcp.output(self.sPortLED, iLEDPin, False)
            time.sleep(iBlinkDelay)
            for iLEDPin in range(0, 8):
                mcp.output(self.sPortLED, iLEDPin, True)
            time.sleep(iBlinkDelay)

        # Hier wird gefragt ob das Spiel neugestartet wird
        sUserinput = input("HAHA! You lost!\nWanna try again?\nyes = again\neverything else = no\n ").lower()
        if sUserinput == "yes": #falls ya
            for iLEDPin in range(0,8):
                mcp.output(self.sPortLED, 8-iLEDPin, False)
                #self.__oMCP.set_output_pin(self.sPortLED, 8-iLEDPin, False)
                time.sleep(0.1)
            self.gameReset() # Spiel wird wieder resettet
        else: # falls nein, wird das programm beendet
            self.setAllLEDoff()
            self.__oDB.closeConnection()
            sys.exit(0)

    def gameWin(self): # Spieler hat gewonnen led werden zufällig an & aus geschaltet
        print("You won!")
        bRunner = True
        fNow = time.time()
        while bRunner == True:
            mcp.output(self.sPortLED, random.randint(0, 8), True)
            mcp.output(self.sPortLED, random.randint(0, 8), False)

            time.sleep(0.1)
            if time.time() >= fNow+random.randint(3, 6):
                self.setAllLEDoff()
                break

        sUserinput = input("Wanna continue?\nyes = continue\neverything else = no\n ").lower()
        if sUserinput == "yes":
            self.gameReset()
        else:
            self.setAllLEDoff()
            self.__oDB.closeConnection()
            sys.exit(0)

    def mainloop(self): # Hier werden alle Einzelteile an Funktionen zusammegefasst
        sUserinput = str(input("Please enter your Username: ")) 
        if len(sUserinput) >= 1:
            print("Game will start in some seconds, get ready!")
            #self.__oDB.createTable()
            time.sleep(random.randint(3, 6))

            while not self.bWon:
                bButtonState = mcp.input(self.sPortButton, self.iPinButton) #
                if bButtonState:
                    if self.__bLEDStatus:
                        self.levelUp()
                        time.sleep(0.2)
                    else:
                        self.__oDB.saveState(sPlayername=sUserinput, iGameLevel=self.iGameLevel)
                        self.gameOver()
                self.blinkLED(self.iGameLevel)
            self.gameWin()
        else:
            print("Du dulli")
            self.setAllLEDoff()
            self.__oDB.closeConnection()
            sys.exit(0)


# region Hilfe
# 1 byte = 8 bits
# 0bXXXXXXXX
#          | <- Letzer bit ist der 1. Pin
#          0 = output
#          1 = input

# Taster = 128
# endregion Hilfe

if __name__ == "__main__":

    # region Buttongame
    # oBG = Buttongame()
    # try:
    #     oBG.mainloop()
    # except KeyboardInterrupt:
    #     oBG.setAllLEDoff()
    # endregion Buttongame

    # region Laddergame
    oLG = Laddergame(pinButton=7, portabButton="B", portabLEDs="A")
    oDB = Database()
    try:
        oLG.mainloop()
    except KeyboardInterrupt:
        oDB.closeConnection()
        oLG.setAllLEDoff()
    # endregion Laddergame
