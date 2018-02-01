from instrument import Instrument
import qtlab_visa as visa
import types
import logging
import numpy
import serial
import qt
import Seekat as see
class SeekatVsource(Instrument):
	
	# Initializes seekat
	def __init__(self, name, address, reset=False):
	    
			logging.debug('Initializing instrument SeekatVsource')
			Instrument.__init__(self, name, tags=['physical'])
                
			# Set parameters
			self._address = address
		
			# Set functions
			self.add_function('reset')
			self.add_function('get_all')
			self.add_function('set_voltage')
			self.add_function('get_voltage')
			self.add_function('close_seekat')
			self._open_serial_connection()
		
		
			if reset:
				self.reset()
			#else:
			#	self.get_all()
			
	# Opens seekat serial connection	
	def _open_serial_connection(self):
		logging.debug('Opening serial connection')
		print self._address
		#ser = serial.Serial(self._address,9600, timeout=0)  # open serial port
		ser = serial.Serial(self._address)
		print ser.isOpen()
		if not (ser.isOpen()):
			ser.open()
		self._ser = ser
		
	# Closes seekat serial connection
	def close_seekat(self):
		logging.debug('Close seekat serial connection')
		ser = self._ser
		ser.close()
		
	
	# Sets all voltages on all channels to zero	
	def reset(self):
			logging.debug('Resetting instrument')
			self.set_voltage(1,0)
			self.set_voltage(2,0)
			self.set_voltage(3,0)
			self.set_voltage(4,0)
			self.set_voltage(5,0)
			self.set_voltage(6,0)
			self.set_voltage(7,0)
			self.set_voltage(8,0)
		
	# Returns a dictionary of voltages on all channels	
	def get_all(self):
		logging.debug('Reading the voltage on each channel')
		voltages = {}
		voltages['1'] = self.get_voltage(1)
		voltages['2'] = self.get_voltage(2)	
		voltages['3'] = self.get_voltage(3)
		voltages['4'] = self.get_voltage(4)
		voltages['5'] = self.get_voltage(5)
		voltages['6'] = self.get_voltage(6)	
		voltages['7'] = self.get_voltage(7)
		voltages['8'] = self.get_voltage(8)
		return voltages
	
	# Prints all voltages on all channels
	def print_all(self):
		logging.debug('Printing the voltages on all channels')
		print self.get_voltage(1)
		print self.get_voltage(2)
		print self.get_voltage(3)
		print self.get_voltage(4)
		print self.get_voltage(5)
		print self.get_voltage(6)
		print self.get_voltage(7)
		print self.get_voltage(8)
	
	# Returns voltage on specified channel
	def get_voltage(self, channel):
		logging.debug('Reading voltage from channel %s' %channel)
		v = see.getvolt(self._ser, channel)
		return v
	
	# Sets input voltage on specified channel
	def set_voltage(self, channel, voltage):
		logging.debug('Writing ' + str(voltage) + ' volts to channel ' + str(channel))
		see.setvolt(self._ser, channel, voltage)
		