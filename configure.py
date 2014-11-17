#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array

port = '/dev/ttyUSB0'
baud = 9600
callsign = '      1'
icon = '6'
freq = '144.3900'
update_rate = '0900'
ptt_delay = '6'
path = '2'
tx_mode = '5'
beep = '0'
digi = '11'
comment = "Comment"
status =  "Status"

lowSpeed = 50
hispeed = 100
slowRate = 180
fastRate = 60
turnSlope = 45
turnAngle = 45
turnTime = 15

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

def smartEnc() :
    arr = array.array( 'B' )
    arr.append( lowSpeed >> 8 )
    arr.append( lowSpeed )
    arr.append( hispeed >> 8 )
    arr.append( hispeed )
    arr.append( slowRate >> 8 )
    arr.append( slowRate )
    arr.append( fastRate >> 8 )
    arr.append( fastRate )
    arr.append( turnSlope >> 8 )
    arr.append( turnSlope )
    arr.append( turnAngle >> 8 )
    arr.append( turnAngle )
    arr.append( turnTime >> 8 )
    arr.append( turnTime )

    return ''.join( chr(x) for x in arr )

def display():
    ser.write( "@DISP" )
    while True :
        line = ser.readline()
        if not line :
            break
        print "line %d : %s" % ( len( line ), line ) , 
        if '18=' in line :
            print "hex: " + ":".join("{:02x}".format( ord( c )) for c in line )

data = [
    ( "Callsign", "@01" + callsign + icon),
    ( "PTT delay", "@02" + ptt_delay),
    ( "Path", "@05" + path),
    ( "TX mode", "@07" + tx_mode),
    ( "Update rate", "@08" + update_rate),
    ( "Comment", "@09" + comment + "\n"),
    ( "Status", "@10" + status + "\n"),
    ( "Digipeat", "@12" + digi + "\n"),
    ( "Frequency", "@16" + freq),
    ( "beep", "@17" + beep ),
    ( "Smart Beacon", "@18" + smartEnc() ),
]

display()

for line in data:
    print "Writing %d : %s %s  " %( len( line[1] ), line[0], line[1] )
    ser.write(line[1])
    s = ser.read(500)
    print "Return :", s

display()

print "exit"
ser.write( "@EXIT" )
