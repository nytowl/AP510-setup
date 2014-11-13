#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import array

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

def deKiss( s ) :
    arr = array.array( 'B', s )
    if debug :
        print "deKiss: ", s

    frame_data = ''
    escape = False
    command = False
    frame = False

    for i in range( 0, len(arr) ) :
        if command :
            # if there's a FEND still in command mode
            if arr[i] == 0xC0 :
                command = True
                continue
            cmd = arr[i] & 0xF
            port = ( arr[i] >> 4 ) & 0xF
            if cmd == 0 :
                cmd_str = "Data"
            if cmd == 1 :
                cmd_str = "TX delay"
            if cmd == 2 :
                cmd_str =  "Persistence"
            if cmd == 3 :
                cmd_str = "slot time"
            if cmd == 4 :
                cmd_str = "tx tail"
            if cmd == 5 :
                cmd_str = "full duplex"
            if cmd == 6 :
                cmd_str = "set hardware"
            if cmd == 0xf :
                cmd_str = "exit"
            if debug :
                print "Command %x %s port %x" %( cmd, cmd_str, port )
            command = False
        if escape :
            if arr[i] == 0xDC :
                if frame :
                    print "TFEND"
            elif arr[i] == 0xDD :
                if frame :
                    print "TFESC"
            else :
                print "invalid escaped char %x" % arr[i] 

            if frame :
                frame_data += chr( arr[i] )
            escape = False
        elif arr[i] == 0xC0 :
            if debug :
                print "FEND"
            command = True
            frame = True
            if ( len( arr ) - i ) >  1 :
                arr = arr[i:]
            else :
                arr = []
            if len( frame_data ) > 0 :
                if debug :
                    print "Frame: ", frame_data
                return ( frame_data, ''.join( chr(x) for x in arr ))
        elif arr[i] == 0xDB :
            if frame :
                print "FESC"
            escape = True
        else :
            if frame :
                frame_data += chr( arr[i] )
                # print "%x:" % ( arr[i] ) ,

    print "Possible incomplete frame - missing FEND"

    return ( frame_data, '' )
