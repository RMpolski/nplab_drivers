from instrument import Instrument
import qtlab_visa as visa
import types
import logging
import numpy
import serial
import qt
import DAC_ADC 
class do_DAC_ADC(Instrument):

	def __init__(self, name, address, reset=False):
	    
			logging.debug('Initializing instrument ADCDAC')
			Instrument.__init__(self, name, tags=['physical'])
                
			# Set parameters
			self._address = address
		
			# Set functions
			self.add_function('reset')
			self.add_function('get_all')
			self.add_function('set_voltage')
			self.add_function('get_voltage')
			self.add_function('close_DACADC')
			self._open_serial_connection()
		
		
			if reset:
				self.reset()
			#else:
			#	self.get_all()
			
		
	def _open_serial_connection(self):
		logging.debug('Opening serial connection')
		print self._address
		#ser = serial.Serial(self._address,9600, timeout=0)  # open serial port
		ser = serial.Serial(self._address, 115200)
		print ser.isOpen()
		if not (ser.isOpen()):
			ser.open()
		self._ser = ser
		
	def close_DACADC(self):
		logging.debug('Close serial connection')
		ser = self._ser
		ser.close()
		
	
		
	def reset(self):
			
			logging.debug('Resetting instrument')
			self.set_voltage('A',0)
			self.set_voltage('B',0)
			self.set_voltage('C',0)
			self.set_voltage('D',0)
			
		
	def get_all(self):
		logging.debug('Reading the voltage on each channel')
		self.get_voltage(0)
		self.get_voltage(1)	
		self.get_voltage(2)
		self.get_voltage(3)

		
	def get_voltage(self, channel):
		logging.debug('Reading voltage from channel %s' %channel)
		v = DAC_ADC.ADC_getvolt(self._ser, channel)
		print v
		
	def set_voltage(self, channel, voltage):
		logging.debug('Writing ' + str(voltage) + ' volts to channel ' + str(channel))
		DAC_ADC.DAC_setvolt(self._ser, channel, voltage)
		