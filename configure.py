#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import string 

port = '/dev/ttyUSB0'
baud = 9600
callsign = ''
icon = '6'
freq = '144.3900'
update_rate = '0900'
ptt_delay = '6'
path = '3'
tx_mode = '1'
beep = '0'

ser = serial.Serial( port, baud, timeout=0.5)

done = False

while not done :
    ser.write( "@SETUP" )
    s = ser.read( 100 )
    if s is not None :
        print "Read: ", s
        if not s.startswith( '@' ) and -1 != string.find( s, "SETUP" ):
            done = True
    else :
        print "Wrote @SETUP"

print "Got setup"

ser.timeout=2

ser.write( "@DISP" )
s = ser.read( 500 )
print "Display :", s

ser.write( "@01" + callsign + icon )
s = ser.read( 500 )
print "Return :", s

ser.write( "@02" + ptt_delay )
s = ser.read( 500 )
print "Return :", s

ser.write( "@05" + path )
s = ser.read( 500 )
print "Return :", s

ser.write( "@07" + tx_mode )
s = ser.read( 500 )
print "Return :", s

ser.write( "@16" + freq )
s = ser.read( 500 )
print "Return :", s

ser.write( "@17" + beep )
s = ser.read( 500 )
print "Return :", s

ser.write( "@08" + update_rate )
s = ser.read( 500 )
print "Return :", s

ser.write( "@DISP" )
s = ser.read( 500 )
print "Display :", s

#ser.write( "@HELP" )
#s = ser.read( 500 )
#print "Display :", s

ser.write( "@EXIT" )

ser.baud=1200

while True :
    s = ser.read( 500 )

    print "Position :", s


