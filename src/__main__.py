#!/usr/bin/python3

import argparse
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

    def _load_lines(self, fname):
        lines = []
        with open(fname, 'r') as fin:
            for line in fin.readlines():
                cleaned = line.strip()
                if not cleaned or cleaned[0] in ['.', ';'] or cleaned[-1] in [':']:
                    continue
                lines.append(line)
        return lines

    """
    def _inx_to_skip(self, line):
        keyword = line.split(' ')[0]
        if 'i' in keyword:
            return 2
        return 1
    """

    def step(self):
        _, ln = trigger('step')
        ln = int(ln)
        nextline = self._lines[ln]
        print(ln, ':', nextline)

        """
        ln, nextline = next(self._lines)
        for _ in range(self._inx_to_skip(nextline)):
            trigger('step')
        print(ln, ':', nextline)
        """

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

def hexup(fname):
    fname = os.path.realpath(fname)

    try:
        jar_location = os.environ[JAR_ENVVAR]
        subprocess.run(['java', '-jar', jar_location, fname], check=True)
    except subprocess.CalledProcessError:
        exit()

    hexname = os.path.splitext(fname)[0] + '.hex'
    return hexname

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
    except AttributeError:
        parser.print_help()

if __name__ == '__main__':
    main()
