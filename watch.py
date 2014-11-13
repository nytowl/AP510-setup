#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array
import kiss
import AX25
import sys

done = False
debug = True

def usage( name ) :
    print "%s : [port[ baud]]" % name
    print "\tport - serial port to listen to \"/dev/rfcomm0\", \"/dev/ttyUSB0\"\n"
    print "\tbaud - port baud rate\n"

if len( sys.argv ) > 3 :
    usage( sys.argv[0] )
    sys.exit()

if len( sys.argv ) >= 2 :
    port = sys.argv[1]
else :
    port = '/dev/rfcomm0'

if len( sys.argv ) == 3 :
    baud = int( sys.argv[2] )
else :
    baud = 9600

print "Opening %s at %d baud" % ( port, baud )
ser = serial.Serial( port, baud, timeout=0.5)

remainder = ''

while not done :
    s = ser.read( 100 )
    if len( remainder ) > 0 :
        s = remainder + s

    if debug and len( s ) > 0 :
        print "String: ", s
        print "AX:", AX25.deAX25( s )

    if s is not None and len( s ) > 0 :
        ( frame, remainder ) = kiss.deKiss( s ) 
        frame_str = AX25.deAX25( frame )
        
        if len( frame_str ) > 0 :
            print "Frame: ", frame_str



