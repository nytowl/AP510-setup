#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array
import sys

port = '/dev/rfcomm0'
baud = 9600

ser = serial.Serial( port, baud, timeout=0.5)

debug = True

def KISS( s ) :
    arr = array.array( "B" );

    arr.append( 0xC0 ) # FEND
    arr.append( 0x00 ) # command and port

    for i in range( 0, len(s) ) :
	if ord( s[i] ) == 0xC0 :
 	    arr.append( 0xDB )
 	    arr.append( 0xDC )
	elif ord( s[i] ) == 0xDB :
 	    arr.append( 0xDB )
 	    arr.append( 0xDD )
	else :
	    arr.append( ord( s[i] ))

    arr.append( 0xC0 ) # FEND
                
    return ''.join( chr(x) for x in arr )

def AX25( to, frm, path, s ) :
    arr = array.array( "B" );
    display_s = ''    

    for i in range( 0, 6 ) :
        if i >= ( len( to ) - 1 ) :
            arr.append( ord( ' ' ) << 1 )
            dislay_s += "_"
        else :
            arr.append( ord( to[i] ) << 1 )
            display_s += to[i]

    arr.append( ord( to[-1] ) << 1 )
    display_s += to[-1]

    for i in range( 0, 6 ) :
        if i >= ( len( frm ) - 1 ) :
            arr.append( ord( ' ' ) << 1 )
            display_s += "_"
        else :
            arr.append( ord( frm[i] ) << 1 )
            display_s += frm[i]
    
    arr.append( ord( frm[-1] ) << 1 )
    display_s += frm[-1]

    for item in path :
        print "item: ", item, len( item )
        for i in range( 0, 6 ) :
            if i >= ( len( item ) - 1 ) :
                arr.append( ord( ' ' ) << 1 )
                display_s += "_"
            else :
                arr.append( ord( item[i] ) << 1 )
                display_s += item[i]

        arr.append( ord( item[-1] ) << 1 )
        display_s += item[-i]

    if debug :
        print "frame: ", display_s + " " + s

    arr[-1] = arr[-1] | 0x01;
    arr.append( 0x03 )# control
    arr.append( 0xF0 ) # pid

    frame_str = ''.join( chr(x) for x in arr )
    frame_str += s

    return frame_str

def usage( name ) :
    print "%s : <to> <from> <path1,path2,..> <text>"

if len( sys.argv ) != 5 :
    usage( sys.argv[0] )
    sys.exit()

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

