import spidev
import random
import time

class MCP23S17:
    def __init__(self, slave_address, busnumber, chipnumber):
        assert busnumber in [0, 1]  # Hier wird überprüft ob die Bus Nummer 0 oder 1 ist (wir benutzen bei uns 0)
        assert chipnumber in [0, 1] # In erster Line wird überprüft ob die chipnumber 0 oder 1 ist (wir benutzen bei uns 0)
        self.controlbyte_write = slave_address<<1 # Setzen vom Kontroll Byte zum schreiben (das byte zum schreiben ist die Adresse mit den letzten Bit auf 0)
        self.controlbyte_read = (slave_address<<1)+1  # Setzen vom Kontroll Byte zum lesen (das byte zum lesen ist die Adresse mit den letzten Bit auf 1)
        self.spi = spidev.SpiDev() # erstellen der SpiDev instance um auf die spi schnittstelle zuzugreiffen können
        self.spi.open(busnumber, chipnumber) # öffnen der vom SPI Verbindung mit der gegeben Busnumber & chipnummer
        self.spi.max_speed_hz = 10000000 # Setzen der maximalen Frequenz
        # configure default registers erstellen von einen Dictionary welche alle Passenden Registernummer enthält zu den GPA & GPB
        # die register die unten aufgelistet sind 8 bit groß
        self._regs = {'conf': {'A': 0x00, 'B': 0x01}, # Config register bei den einzelnen (hier werden die Pins festgelegt also welcher ein Input & Output ist (für A und B)
                      'input': {'A': 0x12, 'B': 0x13}, # Eingabe registe hier stehen die Registernummer um von den input pin die eingabe zu lesen (für A und B) wenn es gesetzt ist es immer jeweils einer der bits gesetzt
                      'output': {'A': 0x14, 'B': 0x15}} # Output register hier stehen die Register um jeweils von einen Pin strom an/aus zu machen

    # Hier wird ein Wert in die Konfiguration geschrieben geschrieben
    # portab muss entweder A oder B sein
    # value wird gesetzt achtung die alten Konfiguration werden hier noch mit übernommen!
    def write_config(self, portab, value):
        assert portab in ['A', 'B']
        reg = self._regs['conf'][portab]
        self.spi.xfer([self.controlbyte_write, reg, value]) # schreiben mit den controlbyte und setzen der Value (der alte Wert wird überschrieben)

    def read_config(self, portab): # Die Funktion dient dazu um aus den Config Register die einzelnen Werte zu lesen
        assert portab in ['A', 'B'] # der portab muss entweder A oder B sein
        reg = self._regs['conf'][portab] # Lese der Registernummer um zu wissen welcher gsesetzt werden muss
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Lesen der config einstellungen, es wird ein Liste zurückgegebn von der Liste wird der 2. Wert benutzt

    def write_output(self, portab, value):
        assert portab in ['A', 'B'] ## der portab muss entweder A oder B sein
        reg = self._regs['output'][portab] # Lese der Registernummer um zu wissen welcher gsesetzt werden muss 
        self.spi.xfer([self.controlbyte_write, reg, value]) # Setzen vom output (hier wird das controlbyte zum schreiben benutzt) der neue wert überschreibnt den alten!

    def read_output(self, portab):
        assert portab in ['A', 'B']  ## der portab muss entweder A oder B sein
        reg = self._regs['output'][portab]# Lese der Registernummer um zu wissen welcher gsesetzt werden muss 
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Lesen vom output (der Wert liefert von jeden Pin 8(bit))

    def read_input(self, portab): # lesen vom einen Eingabe-Pin
        assert portab in ['A', 'B']  ## der portab muss entweder A oder B sein
        reg = self._regs['input'][portab]# Lese der Registernummer um zu wissen welcher gsesetzt werden muss (in den Falle zum lesen der eingabe)
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Gebe den Wert zurück (benutzt wird hir der controlbyte zum lesen) NOTE: Es werden alle zuständen zurückgegebn also von jedem Pin
        


    def __get_real_pin(self, pin):
        if pin < 9:
             pin = pin - 1
        elif pin < 29:
            pin = 28 - pin
        if pin < 0 or pin >= 8:
            return -1
        return pin

    def set_output_pin(self, portab, pin, value):
        pin = self.__get_real_pin(pin)
        if pin == -1:
            return
        v = self.read_output(portab)
        mask = 1 << pin
        if not value:
            v &= ~(mask)
        else:
            v |= mask
        self.write_output(portab, v)

    def get_output_pin(self, portab, pin):
        pin = self.__get_real_pin(pin)
        if pin == -1:
            return False
        return bool(self.read_output(portab) & (1 << pin))

    def get_input_pin(self, portab, pin):
        pin = self.__get_real_pin(pin)
        if pin == -1:
            return False
        return bool(self.read_input(portab) & (1 << pin))


if __name__ == "__main__":
    import time
    m = MCP23S17(0b0100000, 0, 0)
    print(" AT START: " + str(0b00000001))
    try:
        m.write_config('B', 0b11111001)
        led1=2
        led2=3
        tasterpin=1
        while True:
            #m.write_output('B', 0b00000001)
            #m.write_output('B', 0b0000000)
            tasterStatus = m.get_input_pin('B', tasterpin)
            print(m.get_output_pin('B', led1), m.get_output_pin('B', led2))
            m.set_output_pin('B', led1, tasterStatus)
            m.set_output_pin('B', led2, not tasterStatus)
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        m.write_output('B', 0b0000000)

