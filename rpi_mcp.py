from spidev import SpiDev
from typing import Union
import logging

class MCP23S17:
	def __assert__(self, portab : str, pin : int = -1):
		assert portab in ['A', 'B'], "Es wurde kein Eintrag für den Portab %s gefunden." % (portab) ## der portab muss entweder A oder B sein
		if pin != -1:
			assert pin < 8 and pin >= 0, "Der Pin darf nicht größer oder gleich 8 sein."

	def __init__(self, slave_address, busnumber, chipnumber):
		assert busnumber in [0, 1]  # Hier wird überprüft ob die Bus Nummer 0 oder 1 ist (wir benutzen bei uns 0)
		assert chipnumber in [0, 1] # In erster Line wird überprüft ob die chipnumber 0 oder 1 ist (wir benutzen bei uns 0)
		self.controlbyte_write = slave_address<<1 # Setzen vom Kontroll Byte zum schreiben (das byte zum schreiben ist die Adresse mit den letzten Bit auf 0)
		self.controlbyte_read = (slave_address<<1)+1  # Setzen vom Kontroll Byte zum lesen (das byte zum lesen ist die Adresse mit den letzten Bit auf 1)
		self.spi = SpiDev() # erstellen der SpiDev instance um auf die spi schnittstelle zuzugreiffen können
		self.spi.open(busnumber, chipnumber) # öffnen der vom SPI Verbindung mit der gegeben Busnumber & chipnummer
		self.spi.max_speed_hz = 10000000 # Setzen der maximalen Frequenz
		# configure default registers erstellen von einen Dictionary welche alle Passenden Registernummer enthält zu den GPA & GPB
		# die register die unten aufgelistet sind 8 bit groß
		self._regs = {'conf': {'A': 0x00, 'B': 0x01}, # Config register bei den einzelnen (hier werden die Pins festgelegt also welcher ein Input & Output ist (für A und B)
					'input': {'A': 0x12, 'B': 0x13}, # Eingabe registe hier stehen die Registernummer um von den input pin die eingabe zu lesen (für A und B) wenn es gesetzt ist es immer jeweils einer der bits gesetzt
					'output': {'A': 0x14, 'B': 0x15}} # Output register hier stehen die Register um jeweils von einen Pin strom an/aus zu machen

	# Hier wird ein Wert in die Konfiguration geschrieben geschrieben
	# portab muss entweder A oder B sein
	# value wird gesetzt achtung die alten Konfiguration werden hier nicht mit übernommen!
	def write_config(self, portab, value):
		self.__assert__(portab)
		reg = self._regs['conf'][portab]
		self.spi.xfer([self.controlbyte_write, reg, value]) # schreiben mit den controlbyte und setzen der Value (der alte Wert wird überschrieben)

	def read_config(self, portab): # Die Funktion dient dazu um aus den Config Register die einzelnen Werte zu lesen
		self.__assert__(portab)
		reg = self._regs['conf'][portab] # Lese der Registernummer um zu wissen welcher gsesetzt werden muss
		return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Lesen der config einstellungen, es wird ein Liste zurückgegebn von der Liste wird der 2. Wert benutzt

	def write_output(self, portab, value):
		self.__assert__(portab)
		reg = self._regs['output'][portab] # Lese der Registernummer um zu wissen welcher gsesetzt werden muss 
		self.spi.xfer([self.controlbyte_write, reg, value]) # Setzen vom output (hier wird das controlbyte zum schreiben benutzt) der neue wert überschreibt den alten!

	def read_output(self, portab : str):
		self.__assert__(portab)
		reg = self._regs['output'][portab]# Lese der Registernummer um zu wissen welcher gsesetzt werden muss 
		return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Lesen vom output (der Wert liefert von jeden Pin 8(bit))

	def read_input(self, portab : str): # lesen vom einen Eingabe-Pin
		self.__assert__(portab)
		reg = self._regs['input'][portab]# Lese der Registernummer um zu wissen welcher gsesetzt werden muss (in den Falle zum lesen der eingabe)
		return self.spi.xfer([self.controlbyte_read, reg, 0])[2] # Gebe den Wert zurück (benutzt wird hir der controlbyte zum lesen) NOTE: Es werden alle zuständen zurückgegebn also von jedem Pin

	def set_output_pin(self, portab : str, pin, value):
		self.__assert__(portab, pin)
		v = self.read_output(portab)
		mask = 1 << pin
		if not value:
			v &= ~(mask)
		else:
			v |= mask
		self.write_output(portab, v)

	def get_output_pin(self, portab : str, pin : int):
		self.__assert__(portab, pin)
		return bool(self.read_output(portab) & (1 << pin))

	def get_input_pin(self, portab : str, pin : int):
		self.__assert__(portab, pin)
		return bool(self.read_input(portab) & (1 << pin))

class mcp(object):
	instance = MCP23S17(0b0100000, 0, 0)
	OUTPUT = 0
	INPUT = 1
	LOW = 0
	HIGH = 1
	@staticmethod
	def set_log_level(level = logging.INFO):
		logging.getLogger().setLevel(level)

	@staticmethod
	def __assert__(pin):
		assert type(pin) in [int, list], "Der Pin kann nur eine Liste oder ein Integer sein. Kein gültiger Typ: " + str(type(pin))

	@staticmethod
	def output(portab : str, pin : Union[int, list], value : Union[int, bool, list]):
		mcp.__assert__(pin)
		if type(pin) is list:
			if type(value) is list:
				for i, _pin in enumerate(pin):
					assert i < len(value), "Der Pin wurde in der Liste nicht definiert. (Index: %d, Pin: %d)" % (i, _pin)
					mcp.instance.set_output_pin(portab, _pin, value[i])
					logging.debug("Setzen vom Output Pin (%s, %d) -> %d " % (portab, _pin, mcp.instance.get_output_pin(portab, _pin)))
			elif type(value) in [int, bool]:
				for _pin in pin:
					mcp.instance.set_output_pin(portab, _pin, value)
					logging.debug("Setzen vom Output Pin (%s, %d) -> %d " % (portab, _pin, mcp.instance.get_output_pin(portab, _pin)))

		elif type(pin) is int:
			assert type(value) in [int, bool], "Gebe einen gütigen Wert an für den Pin %d!" % pin
			mcp.instance.set_output_pin(portab, pin, value)

	### Raw functions start
	@staticmethod
	def raw_output(portab : str, value : int):
		assert mcp.instance.write_output(portab, value) == value, "Beim schreiben ist etwas schief gegangen Portab (%s) Wert (%d)." % (portab, value)

	@staticmethod
	def raw_input(portab : str):
		return mcp.instance.read_input(portab)

	@staticmethod
	def raw_write_config(portab : str, value : int):
		mcp.instance.write_config(portab, value)

	@staticmethod
	def raw_read_config(portab : str):
		return mcp.instance.read_config(portab)
	### Raw functions end

	@staticmethod
	def read_output(portab : str, pin : Union[int, list]):
		mcp.__assert__(pin)
		if type(pin) is list:
			stateDict = {}
			for _pin in pin:
				stateDict.update({_pin : mcp.instance.get_output_pin(portab, _pin)})
			return stateDict
		elif type(pin) is int: 
			return mcp.instance.get_output_pin(portab, pin)

	@staticmethod
	def input(portab : str, pin : Union[int, list]):
		mcp.__assert__(pin)
		if type(pin) is list:

			stateDict = {}
			for _pin in pin:
				logging.debug("Lese vom Pin (%s, %d) -> %d " % (portab, _pin, mcp.instance.get_input_pin(portab, _pin)))
				stateDict.update({_pin : mcp.instance.get_input_pin(portab, _pin)})
			return stateDict
		elif type(pin) is int: 
			logging.debug("Lese vom Pin (%s, %d) -> %d " % (portab, pin, mcp.instance.get_input_pin(portab, pin)))
			return mcp.instance.get_input_pin(portab, pin)

	@staticmethod
	def setup(portab : str, pin : Union[int, list], value : Union[int, bool]):
		mcp.__assert__(pin)
		v = mcp.instance.read_config(portab)
		if type(pin) is list:
			for _pin in pin:
				mask = 1 << _pin
				if value == mcp.OUTPUT:
					v &= ~(mask)
					logging.info("Der Pin %d wurde als Ausgabe / Output definiert. " % (_pin))
				elif value == mcp.INPUT:
					v |= mask
					logging.info("Der Pin %d wurde als Eingabe / Input definiert. " % (_pin))
		elif type(pin) is int:
			mask = 1 << pin
			conf = "Eingabe / Input"
			if value == mcp.OUTPUT:
				v &= ~(mask)
				conf = "Ausgabe / Output"
			elif value == mcp.INPUT:
				v |= mask
			logging.info("Der Pin %d wurde als %s definiert. " % (pin, conf))
			logging.debug("v is %d" % (v))
		mcp.instance.write_config(portab, v)
		assert mcp.instance.read_config(portab) == v, "Bei den Konfigurationen ist etwas schief gelaufen."

	@staticmethod
	def cleanup():
		for portab in ['A', 'B']:
			mcp.instance.write_output(portab, 0)
			mcp.instance.write_config(portab, 255)

	@staticmethod
	def test(block = True):
		mcp.set_log_level(logging.DEBUG) # Setting to debug
		pin = ('A', 0)
		mcp.setup(*pin, mcp.OUTPUT)
		mcp.output(*pin, mcp.HIGH)
		print(mcp.read_output(*pin))
		assert mcp.read_output(*pin) == mcp.HIGH, "Bitte überprüfe deine Schaltung.\nTipps:\n(1) Ziehe dein Reset Pin raus und wieder rein.\n(2) Zähle alle Pins wieder ab.\n(3) Pass auf das du + nicht mit - vertauscht.\n(4) Wenn dein MCP heiß wird, vertausch plus mit minus."
		logging.info("Test erfoglreich bestanden!")
		if block:
			input("Drücke eine Taste zum beenden.")
		mcp.cleanup()


if __name__ == "__main__":
	mcp.test()