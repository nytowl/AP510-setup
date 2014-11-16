#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array
import sys
from kiss import KISS
from AX25 import AX25

debug = False

def usage( name ) :
    print "%s : <to> <from> <path1,path2,..> <text> [port[ baud]]" % name
    print "\tto - call sign 1-6 chars \"-\" SSID"
    print "\tfrom - call sign 1-6 chars \"-\" SSID"
    print "\tpath - comma separated list of call signs 1-6 chars \"-\" SSID"
    print "\ttext - string"
    print "\tport - serial port to listen to \"/dev/rfcomm0\", \"/dev/ttyUSB0\"\n"
    print "\tbaud - port baud rate\n"
    print "\nex: %s DSTSGN SRCSGN-1 WIDE1-1,WIDE2-1 \":EMAIL-2  :email@example.com test aprs message{2\"" % name

if len( sys.argv ) < 5 or len( sys.argv ) > 7 :
    usage( sys.argv[0] )
    sys.exit()

if len( sys.argv ) >= 6 :
    port = sys.argv[5]
else :
    port = '/dev/ttyUSB0'

if len( sys.argv ) == 7 :
    baud = int( sys.argv[6] )
else :
    baud = 4800

print "Opening %s at %d baud" % ( port, baud )
ser = serial.Serial( port, baud, timeout=0.5)

to = sys.argv[1]
frm = sys.argv[2]
path = []
path = sys.argv[3].split(",")
text = sys.argv[4]

ax = AX25( to, frm, path, text )

if debug : 
    print "ax:", ax

kiss = KISS( ax )

ser.write( kiss )

done = False

while not done :
    s = ser.readline( 0xC0 )
    if debug :
        print "line", s
    if "OK" in s : 
        done = True

