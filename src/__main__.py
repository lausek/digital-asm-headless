#!/usr/bin/python3

import argparse
import os
import os.path
import socket
import struct
import subprocess

JAR_ENVVAR = 'DIGASMJAR'
HOST, PORT = 'localhost', 41114

def pack(msg):
    buf = msg.encode('utf8')
    n = struct.pack('>H', len(buf))
    return n + buf

def trigger(evt, arg=None):
    for fam, ty, proto, flags, host in socket.getaddrinfo(HOST, PORT):
        with socket.socket(fam, ty) as s:
            s.connect(host[:2])

            if arg is None:
                msg = str(evt)
            else:
                msg = '{}:{}'.format(evt, arg)
            msg = pack(msg)

            if s.sendall(msg) is None:
                break

def hexup(fname):
    fname = os.path.realpath(fname)

    jar_location = os.environ[JAR_ENVVAR]
    subprocess.run(['java', '-jar', jar_location, fname], check=True)

    hexname = os.path.splitext(fname)[0] + '.hex'
    return hexname

def measure(args):
    trigger('measure')

def run(args):
    trigger('run')

def step(args):
    trigger('step')

def stop(args):
    trigger('stop')

def debug(args):
    hexname = hexup(args.file)
    trigger('debug', hexname)

def start(args):
    hexname = hexup(args.file)
    trigger('start', hexname)

def main():
    if not JAR_ENVVAR in os.environ:
        print('environment variable', JAR_ENVVAR, 'not set')
        exit()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('file', type=str)
    start_parser.set_defaults(func=start)

    debug_parser = subparsers.add_parser('debug')
    debug_parser.add_argument('file', type=str)
    debug_parser.set_defaults(func=debug)

    subparsers.add_parser('measure').set_defaults(func=measure)
    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('step').set_defaults(func=step)
    subparsers.add_parser('stop').set_defaults(func=stop)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()

if __name__ == '__main__':
    main()
