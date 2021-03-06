#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import array

debug = False

def AXsign( s ) :
    arr = array.array( "B" );
    display_s = ''    

    signEnd = False

    if len( s ) >= 6 :
        sLen = 6
    else :
        sLen = len( s )

    for i in range( 0, sLen ) :
        if s[i] == '-' :
            signEnd = True
        if signEnd :
            arr.append( ord( ' ' ) << 1 )
            display_s += "_"
        else :
            arr.append( ord( s[i] ) << 1 )
            display_s += s[i]

    if signEnd or ( len( s ) == 8 and s[7] == '-' ) :
        arr.append( ord( s[-1] ) << 1 )
        display_s += "-" + s[-1] + " "
    else :
        arr.append( ord( '0' ) << 1 )
        display_s += " "

    return ( arr, display_s )

def AX25( to, frm, path, s ) :
    arr = array.array( "B" );
    display_s = ''    

    toArr , toS = AXsign( to )
    
    arr += toArr
    display_s += toS

    frmArr , frmS = AXsign( frm )
    
    arr += frmArr 
    display_s += frmS

    for item in path :
        if debug :
            print "item: ", item, len( item )

        itemArr, itemS = AXsign( item )

        arr += itemArr
        display_s += itemS

    if debug :
        print "frame: ", display_s + " " + s

    arr[-1] = arr[-1] | 0x01;
    arr.append( 0x03 )# control
    arr.append( 0xF0 ) # pid

    frame_str = ''.join( chr(x) for x in arr )
    frame_str += s

    return frame_str

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

    if len( arr ) < 2 :
        return ''

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

