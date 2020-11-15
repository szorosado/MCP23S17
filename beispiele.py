


#Um mit einen Taster zu arbeiten (Beispiel 1)

from rpi_mcp import mcp
from time import sleep
from logging import DEBUG, INFO, info

if __name__ == "__main__":
    ### Wenn ihr loggen wollt...
    mcp.set_log_level(DEBUG)
    tasterPin = 0 # hier kommt der Pin (GPB0)
    mcp.setup('B', tasterPin, mcp.INPUT) # nicht nötig, weil alle Pins default Input sind 
    while True:
        info("Tasterwert: %d" % mcp.input('B', tasterPin))
        sleep(0.5)

# Um eine Led an/aus zu machen (Beispiel 2)

from rpi_mcp import mcp
from time import sleep
from logging import DEBUG, INFO

if __name__ == "__main__":
    ### Wenn ihr loggen wollt...
    mcp.set_log_level(DEBUG) # Aktivieren vom Log (um zu debuggen)
    ledPin = 0
    mcp.setup('A', ledPin, mcp.OUTPUT) #
    mcp.output('A', ledPin, mcp.HIGH)
    sleep(0.5)
    mcp.output('A', ledPin, mcp.LOW)


#Das ganze kombiniert :d (Beispiel 3)

from rpi_mcp import mcp
from time import sleep
from logging import DEBUG, INFO, info

if __name__ == "__main__":
    ### Wenn ihr loggen wollt...
    mcp.set_log_level(INFO)
    tasterPin = 0 # hier kommt der Pin für den Taster
    ledPin = 0 # hier kommt der Pin für die LED
    mcp.setup('B', tasterPin, mcp.INPUT) # nicht nötig, weil alle Pins default Input sind 
    mcp.setup('A', ledPin, mcp.OUTPUT)
    while True:
        tasterWert = mcp.input('B', tasterPin)
        info("Tasterwert: %d" % tasterWert)
        mcp.output('A', ledPin, tasterWert)
        sleep(0.5)