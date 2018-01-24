import serial

'''ser=serial.Serial('COM4', 115200)'''

def ch_convert(DAC_ADC, ch):
    con_ch = 'aaaa'
    if DAC_ADC == 'DAC':
        if ch == 'C':
            con_ch = '0'
        elif ch == 'A':
            con_ch = '1'
        elif ch == 'D':
            con_ch = '2'
        elif ch == 'B':
            con_ch = '3'
    elif DAC_ADC == 'ADC':
        if ch == 0:
            con_ch = '2'
        elif ch == 1:
            con_ch = '0'
        elif ch == 2:
            con_ch = '3'
        elif ch == 3:
            con_ch = '1'
    else:
        print 'ADCDAC error'
    return con_ch


def DAC_setvolt(ser, ch, volt):
    con_ch = ch_convert('DAC', ch)
    ser.write('SET,'+ con_ch +','+str(volt) +'\r')
    mes = ser.readline()
    print mes
    set_ch = mes.split(' ')[1]
    set_volt = mes.split(' ')[4].split('V')[0]
    return set_ch, float(set_volt)
    
def ADC_getvolt(ser, ch):
    con_ch = ch_convert('ADC', ch)
    ser.write('GET_ADC,'+ con_ch + '\r')
    mes = ser.readline()
    return float(mes)

'''not sure about which parse'''
    
def if_ready(ser):
    ser.write('*RDY?\r')
    if ser.readline() == 'READY\r\n':
        return True
    else:
        return False
