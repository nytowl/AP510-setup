#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array

port = '/dev/rfcomm0'
baud = 9600

ser = serial.Serial( port, baud, timeout=0.5)

done = False
debug = False

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

def deAX25( s ) :
    frame_str = ''
    last = False
    arr = array.array( 'B', s )

    if len( arr ) <= 0 :
        return ''

    flag = arr[0]

    if debug :
        print "flag %c %x" % ( chr( arr[0] ), arr[0] )

    arr = arr[1:]

    while not last :
        if len( arr ) < 7 :
            print "missing last address" 
            return frame_str 

        call_sign = ''

        for i in range( 0, 6 ) :
            call_sign += str( chr( arr[i] >> 1 ))

        if arr[6] & 0x01 :
            last = True

        if debug and arr[6] & 0x80 :
            print "repeated"

        ssid = str( chr( (( arr[6] >> 1 ) & 0x0F ) + ord( '0' )) )

        frame_str += call_sign + '-' + ssid + ' '
        
        arr = arr[7:]

    control =  arr[0]
   
    if debug :
        if control & 0x01 :
            if control & 0x02 :
                print "U frame"
                m = control & 0xEF
                print "UI frame type:", 
                if m == 3 :
                    print "Unnumbered Information"
                if m == 0x87 :
                    print "Frame Reject"
                if m == 0x63 :
                    print "Unnumbered Acknowledge"
                if m == 0x0F :
                    print "Disconnected Mode"
                if m == 0x43 :
                    print "Disconnect"
                if m == 0x2F :
                    print "Set Asynchronous Balanced Mode"
            else :
                print "S frame"
        else :
            print "I frame"

    pid = arr[1]

    pid_test = pid & 0x30

    if debug :
        if pid_test == 0x10 or pid_test == 0x20 :
            print "AX25 frame"
        else :
            print "X25 frame type %x" % pid 

        if debug :
            print "Control %x PID %x" % ( control, pid )

    arr = arr[2:]

    frame_str += ''.join( chr(x) for x in arr )

    return frame_str

remainder = ''

while not done :
    s = ser.readline( 0xC0 )
    if len( remainder ) > 0 :
        s = remainder + s
    if s is not None and len( s ) > 0 :
        ( frame, remainder ) = deKiss( s ) 
        frame_str = deAX25( frame )
        
        if len( frame_str ) > 0 :
            print "Frame: ", frame_str



