import serial
import string
import time
import math
import numpy as np

def port_init():
   ser = serial.Serial('COM4',9600, timeout=0)  # open serial port
   if not (ser.is_open):
      ser.open()

   return ser


def setvolt(ser, channel, volt):
#voltage within +/-10 V
   if volt > 10:
      volt = 10.0
   elif volt < -10:
      volt = -10.0

#channel switch
   if channel==1:
      n1 = 19
      n2=0
      m1=1
      m2=0
   elif channel==2:
      n1 = 18
      n2=0
      m1=1
      m2=0
   elif channel==3:
      n1 = 17
      n2=0
      m1=1
      m2=0
   elif channel==4:
      n1 = 16;
      n2=0;
      m1=1;
      m2=0;
   elif channel==5:
      n1 = 0;
      n2=19;
      m1=0;
      m2=1;
   elif channel==6:
      n1 = 0;
      n2=18;
      m1=0;
      m2=1;
   elif channel== 7:
      n1 = 0;
      n2=17;
      m1=0;
      m2=1;
   elif channel==8:
      n1 = 0;
      n2=16;
      m1=0;
      m2=1;
   else:
      print('INVALID CHANNEL')

#binary signal conversion
   #Decimal equivalent of 16 bit data
   if volt >= 0:
      dec16 = round((math.pow(2,15)-1)*volt/10);
   else:
      dec16 = round(math.pow(2,16) - abs(volt)/10.0 * math.pow(2,15));
      #print 'aaa'
      #print dec16
   #print dec16

   #Checking for negative zero (seekat can't handle it)
   if dec16 == math.pow(2,16):
	  dec16 = 0.0
   time.sleep(1)

   bin16 = str(bin(int(dec16))[2:]).zfill(16); #16 bit binary
   d1=int(bin16[:8], 2)  # first 8 bits
   #print bin16[:8]
   d2=int(bin16[8:17], 2) #second 8 bits
   #print bin16[8:17]

   time.sleep(0.005)

   ser.write([255,254,253,n1,d1*m1,d2*m1,n2,d1*m2,d2*m2]);
   #print [255,254,253,n1,d1*m1,d2*m1,n2,d1*m2,d2*m2]

   ser.flush()
   return

def getvolt(ser,channel):

   ser.flushInput()
   #channel switch
   if channel==1:
      n1 = 19+128
      n2=0
      m1=1
      m2=0
   elif channel==2:
      n1 = 18+128
      n2=0
      m1=1
      m2=0
   elif channel==3:
      n1 = 17+128
      n2=0
      m1=1
      m2=0
   elif channel==4:
      n1 = 16+128
      n2=0;
      m1=1;
      m2=0;
   elif channel==5:
      n1 = 0;
      n2=19+128;
      m1=0;
      m2=1;
   elif channel==6:
      n1 = 0;
      n2=18+128;
      m1=0;
      m2=1;
   elif channel== 7:
      n1 = 0;
      n2=17+128;
      m1=0;
      m2=1;
   elif channel==8:
      n1 = 0;
      n2=16+128;
      m1=0;
      m2=1;
   else:
      print('INVALID CHANNEL')

   time.sleep(0.1)
   ser.write([255,254,253,n1,0,0,n2,0,0])
   time.sleep(0.1)
   ser.write([255,254,253,n1,0,0,n2,0,0])

   time.sleep(0.1)

   ser.flush()


   time.sleep(0.1)
   ser.write([255,254,253,0,0,0,0,0,0])

   time.sleep(0.1)

   bdata=np.zeros(13)

   for i in range(0,12):
      #print i
      a = ser.readline()
      #print a
      bdata[i]=int(a)

   bdata2=max(bdata[6+1]*math.pow(2,8)+bdata[6+2],bdata[6+4]*math.pow(2,8)+bdata[6+5]);


   #print bdata[6+1]
   #print bdata[6+2]
   #print bdata2
   if bdata2 < pow(2,15):
      bdata3=10.0*bdata2/(math.pow(2,15)-1)
   else:
      bdata3=-10.0*(math.pow(2,16)-bdata2)/math.pow(2,15)

   ser.flushInput()
   return bdata3
