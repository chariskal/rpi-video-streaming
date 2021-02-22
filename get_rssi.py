import serial
import time

phone = serial.Serial("/dev/ttyS0", baudrate = 115200, timeout=2.0)
stri = 'AT+CSQ\r\n'
phone.write(stri.encode('utf-8'))
time.sleep(2)

t = phone.read(1000)
print(t)
t = t.decode('utf-8')
print(t)
idx = t.find(":")
print(t[idx+2:idx+4])
phone.close()

