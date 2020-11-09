import spidev

class MCP23S17:
    def __init__(self, slave_address, busnumber, chipnumber):
        assert busnumber in [0, 1]  #prüft ob busnumber in [0 und 1] vorhanden ist
        assert chipnumber in [0, 1] #prüft ob chipnumber in [0 und 1] vorhanden ist
        self.controlbyte_write = slave_address<<1 #slave-addresse wird beschrieben
        self.controlbyte_read = (slave_address<<1)+1 # slave-addresse wird gelesen
        self.spi = spidev.SpiDev() # Spi.dev wird verwenden und in spi gespeichert
        self.spi.open(busnumber, chipnumber) # spi wird mit busnumber und chipnumber verbunden
        self.spi.max_speed_hz = 10000000 #  der max speed wird in 10000000 gesetzt
        self._regs = {'conf': {'A': 0x00, 'B': 0x01}, #configure default register
                      'input': {'A': 0x12, 'B': 0x13},
                      'output': {'A': 0x14, 'B': 0x15}}

    def write_config(self, portab, value):
        assert portab in ['A', 'B'] #Es wird geprüft, ob portab in A und B ist
        reg = self._regs['conf'][portab] # die conf und portab werden in regs gespeichert
        self.spi.xfer([self.controlbyte_write, reg, value])

    def read_config(self, portab):
        assert portab in ['A', 'B'] #Es wird geprüft, ob portab in A und B ist
        reg = self._regs['conf'][portab] # die conf und reg werden in regs gespeichert 
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2] ### es wird 3 bytes an den spi.xfer geschickt und dann wird das 3.byte genommen

    def write_output(self, portab, value):
        assert portab in ['A', 'B'] #Hier wird geprüft, ob portab in A und B ist
        reg = self._regs['output'][portab] # output wird geschrieben und dann überschrieben
        self.spi.xfer([self.controlbyte_write, reg, value])

    def read_output(self, portab):
        assert portab in ['A', 'B'] #Hier wird geprüft, ob portab in A und B ist
        reg = self._regs['output'][portab] # output wird geschrieben und dann überschrieben
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2]

    def read_input(self, portab):
        assert portab in ['A', 'B'] #Hier wird geprüft, ob portab in A und B ist
        reg = self._regs['input'][portab] # input wird geschrieben und dann überschrieben
        return self.spi.xfer([self.controlbyte_read, reg, 0])[2]