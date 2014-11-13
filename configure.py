#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial

port = '/dev/ttyUSB0'
baud = 9600
callsign = '      1'
icon = '6'
freq = '144.3900'
update_rate = '0900'
ptt_delay = '6'
path = '2'
tx_mode = '3'
beep = '0'
digi = '11'
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
    ( "Callsign", "@01" + callsign + icon),
    ( "PTT delay", "@02" + ptt_delay),
    ( "Path", "@05" + path),
    ( "TX mode", "@07" + tx_mode),
    ( "Update rate", "@08" + update_rate),
    ( "Comment", "@09" + comment + "\n"),
    ( "Status", "@10" + status + "\n"),
    ( "Digipeat", "@12" + digi + "\n"),
    ( "Frequenxy", "@16" + freq),
    ( "beep", "@17" + beep ),
]

display()

for line in data:
    print "Writing: ", line[0], line[1]
    ser.write(line[1])
    s = ser.read(500)
    print "Return :", s

display()

print "exit"
ser.write( "@EXIT" )

ser.baud=9600

while True :
    s = ser.read( 500 )

    print "Position :", s


