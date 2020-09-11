#!/usr/bin/python3

import argparse
import json
import io
import os
import os.path
import socket
import struct
import subprocess

JAR_ENVVAR = 'DIGASMJAR'
HOST, PORT = 'localhost', 41114

class Debugger:
    def __init__(self, fname):
        self._lines = self._load_lines(fname)
        self._addr_map = self._load_addr_map(fname)

    def _load_lines(self, fname):
        with open(fname, 'r') as fin:
            return [line for line in fin.readlines()]

    def _load_addr_map(self, fname):
        addr_map = {}
        addr_prev, line_prev = 0, None
        fname = patch_extension(fname, '.map')

        with open(fname, 'r') as fin:
            for entry in json.load(fin):
                addr, line = entry['addr'], entry['line']

                # TODO: does this have the correct order?
                if 1 < addr - addr_prev:
                    for i in range(addr_prev + 1, addr):
                        addr_map[i] = line_prev

                addr_map[addr] = line
                addr_prev, line_prev = addr, line

        return addr_map

    def step(self):
        _, addr = trigger('step')

        addr = int(addr, 16)
        if addr in self._addr_map:
            ln = self._addr_map[addr]
            nextline = self._lines[ln - 1]
            print(ln, ':', nextline)

    def run(self):
        while True:
            t = input('> ')
            if t.lower() in ['s', 'step']:
                self.step()

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
                res = s.recv(1024).decode('utf8').split(':')
                if len(res) < 2:
                    return res[0], None
                return res[:2]
    return None, None

def patch_extension(fname, ext):
    fname = os.path.realpath(fname)
    return os.path.splitext(fname)[0] + ext

def hexup(fname):
    fname = os.path.realpath(fname)

    try:
        jar_location = os.environ[JAR_ENVVAR]
        subprocess.run(['java', '-jar', jar_location, fname], check=True)
    except subprocess.CalledProcessError:
        exit()

    return patch_extension(fname, '.hex')

def measure(args):
    trigger('measure')

def run(args):
    trigger('run')

def step(args):
    _, rarg = trigger('step')

def stop(args):
    trigger('stop')

def debug(args):
    hexname = hexup(args.file)
    trigger('debug', hexname)
    Debugger(args.file).run()

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
    except AttributeError as e:
        parser.print_help()

if __name__ == '__main__':
    main()
