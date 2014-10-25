#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial

port = '/dev/ttyUSB0'
baud = 9600
callsign = '      '
icon = '6'
freq = '144.3900'
update_rate = '0900'
ptt_delay = '6'
path = '3'
tx_mode = '1'
beep = '0'
comment = "Comment"
status =  "Status"

ser = serial.Serial( port, baud, timeout=0.5)

done = False

while not done :
    ser.write( "@SETUP" )
    s = ser.read( 100 )
    if s is not None :
        print "Read: ", s
        if not s.startswith( '@' ) and "SETUP" in s:
            done = True
    else :
        print "Wrote @SETUP"

print "Got setup"

ser.timeout=2

def display():
    ser.write( "@DISP" )
    s = ser.read( 500 )
    print "Display :", s

data = [
    "@01" + callsign + icon,
    "@02" + ptt_delay,
    "@05" + path,
    "@07" + tx_mode,
    "@08" + update_rate,
    "@09" + comment + "\n",
    "@10" + status + "\n",
    "@16" + freq,
    "@17" + beep,
]

display()

for line in data:
    print "Writing: ", line
    ser.write(line)
    s = ser.read(500)
    print "Return :", s

display()

print "exit"
ser.write( "@EXIT" )

ser.baud=9600

while True :
    s = ser.read( 500 )

    print "Position :", s


