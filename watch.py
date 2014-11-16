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
debug = False
max_timeout = 10

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
timeout = 0

while not done :
    s = ser.read( 100 )

    if len( s ) == 0 and len( remainder ) == 0 :
        timeout = 0 
    else :
        timeout += 1

    if timeout > max_timeout and len( s ) == 0 and len( remainder ) > 0:
        # timeout waiting for the reset of the packet
        print "timeout wating for FEND"
        timeout = 0
        remainder =''
    else :
        print "Got chars %d %d %d" % ( timeout, len(s), len( remainder))

    if len( remainder ) > 0 :
        s = remainder + s
        remainder = ''

    if debug and len( s ) > 0 :
        print "Hexdump: " + ":".join("{:02x}".format(ord(c)) for c in s)

    if s is not None and len( s ) > 0 :
        ( frame, remainder ) = kiss.deKiss( s ) 

        if debug :
            print "Frame: " + ":".join("{:02x}".format(ord(c)) for c in frame)
            print "Reaminder: " + ":".join("{:02x}".format(ord(c)) for c in remainder)

        frame_str = AX25.deAX25( frame )
        
        if len( frame_str ) > 0 :
            print "Frame: ", frame_str
            timeout = 0
    else :
        remainder = s
    

