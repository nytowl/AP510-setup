#!/usr/bin/python
#
# Copyright 2014 Angus Ainslie <angus@akkea.ca>
# This software is licensed GPL V2
#
import serial
import array
import argparse
import sys

parser = argparse.ArgumentParser(description='Configure the ap510 aprs device.')
parser.add_argument('-p', '--port',  dest='port',
        help='serial port for the ap510', default='/dev/ttyUSB0' )
parser.add_argument('-b', '--baud', type=int, dest='baud',
        help='baud rate for ap510', default=9600)
parser.add_argument('-v', '--verbose', type=int, dest='verbose',
        help='debug level', default=0)
parser.add_argument('-c', '--callsign', dest='callsign',
        help='call sign for outgoing aprs messages', default='      ')
parser.add_argument('-s', '--ssid', type=int, dest='ssid',
        help='SSID to append to callsign', default=0)
parser.add_argument('-i', '--icon', type=int, dest='icon',
        help='aprs icon', default=6)
parser.add_argument('-f', '--freq', dest='freq',
        help='aprs frequency', default='144.3900')
parser.add_argument('-u', '--update', dest='update_rate', type=int,
        help='time between automatic aprs TX', default=900)
parser.add_argument('-d', '--delay', dest='ptt_delay', choices=range(1,8),
        help='time to assert PTT before TX    1 - 60 ms, 2 - 120 ms, 3 - 180 ms,\
                 4 - 300 ms, 5 - 480 ms, 6 - 600 ms, 7 - 1000 ms', default=6)
parser.add_argument('-S', '--show', dest='show',
        help='print the current config', default=False, action='store_true')
parser.add_argument('-e', '--exit', dest='exit',
        help='exit after config', default=False, action='store_true')
parser.add_argument('-P', '--path', dest='path', type=int, choices=range(0,7),
        help='0 - none, 1 - "WIDE 1-1", 2 - "WINE 1-1 WIDE 2-1", 3 - "WINE 1-1 WIDE 2-2", \
        4 - "TEMP 1-1", 5 - "TEMP 1-1 WIDE 2-1", 6 - "WIDE 2-1"', default=1 )
parser.add_argument('-t', '--txmode', dest='tx_mode', type=int, choices=range(1,6),
        help='1 manual, 2 auto, 3 manual + auto, 4 smartbeacon, 5 smartbeacon + manual'
        , default=1 )
parser.add_argument('-B', '--beep', dest='beep', type=int, choices=range(0,2),
        help='0 - off, 1 - on ', default=0 )
parser.add_argument('-D', '--digi', dest='digi', choices=[ '00','11','12','13' ],
        help='00 - no digipeat, 11 - wide 1, 12 - wide 2, 13 - wide 1 + wide 2', default='00' )
parser.add_argument('-C', '--comment', dest='comment',
        help='comment field for the aprs packet', default="Comment" )
parser.add_argument( '--status', dest='status',
        help='status field for the aprs packet', default="Status" )
parser.add_argument( '--bls', dest='bls', type=int,
        help='SMARTBeacon low speed', default=50 )
parser.add_argument( '--bhs', dest='bhs', type=int,
        help='SMARTBeacon high speed', default=100 )
parser.add_argument( '--bsr', dest='bsr', type=int,
        help='SMARTBeacon slow rate', default=180 )
parser.add_argument( '--bfr', dest='bfr', type=int,
        help='SMARTBeacon fast rate', default=180 )
parser.add_argument( '--bts', dest='bts', type=int,
        help='SMARTBeacon turn slope', default=45 )
parser.add_argument( '--bta', dest='bta', type=int,
        help='SMARTBeacon turn angle', default=45 )
parser.add_argument( '--btt', dest='btt', type=int,
        help='SMARTBeacon turn time', default=15 )

args = parser.parse_args()
if args.verbose > 0 :
    print args

def usage() :
    parser.print_help()
    sys.exit()

if len( args.callsign ) > 6 :
    usage()

callsign = args.callsign + "{:1x}".format( args.ssid ) + "{:1x}".format( args.icon )
update_rate = "{:04d}".format( args.update_rate )
ptt_delay = "{:1d}".format( args.ptt_delay )
path = "{:1d}".format( args.path )
tx_mode = "{:1d}".format( args.tx_mode )
beep = "{:1d}".format( args.beep )
digi = args.digi
comment = args.comment
status = args.status

lowSpeed = args.bls
hispeed = args.bhs
slowRate = args.bsr
fastRate = args.bfr
turnSlope = args.bts
turnAngle = args.bta
turnTime = args.btt

ser = serial.Serial( args.port, args.baud, timeout=0.5)

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

if len ( args.freq ) < 8 :
    usage()

data = [
    ( "Callsign", "@01" + callsign ),
    ( "PTT delay", "@02" + ptt_delay),
    ( "Path", "@05" + path),
    ( "TX mode", "@07" + tx_mode),
    ( "Update rate", "@08" + update_rate),
    ( "Comment", "@09" + comment + "\n"),
    ( "Status", "@10" + status + "\n"),
    ( "Digipeat", "@12" + digi + "\n"),
    ( "Frequency", "@16" + args.freq),
    ( "beep", "@17" + beep ),
    ( "Smart Beacon", "@18" + smartEnc() ),
]

if args.show :
    display()

for line in data:
    print "Writing %d : %s %s  " %( len( line[1] ), line[0], line[1] )
    ser.write(line[1])
    s = ser.read(500)
    print "Return :", s

print "New Config"
display()

if args.exit :
    print "exit"
    ser.write( "@EXIT" )
