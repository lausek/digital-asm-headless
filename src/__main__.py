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

                if 1 < addr - addr_prev:
                    for i in range(addr_prev + 1, addr):
                        addr_map[i] = line_prev

                addr_map[addr] = line
                addr_prev, line_prev = addr, line

        return addr_map

    def print_line(self, addr):
        if addr in self._addr_map:
            ln = self._addr_map[addr]
            nextline = self._lines[ln - 1]
            print('0x{:X}: {}'.format(ln, nextline))

    def run_to_break(self):
        _, addr = trigger('run')
        self.print_line(int(addr, 16))

    def step(self):
        _, addr = trigger('step')
        self.print_line(int(addr, 16))

    def run(self):
        self.print_line(0)
        while True:
            t = input('> ').lower()
            if t in ['h', 'help']:
                print('h - help')
                print('q - quit')
                print('r - run to next breakpoint')
                print('s - do a single instruction step')

            elif t in ['q', 'quit']:
                break

            elif t in ['r', 'run']:
                self.run_to_break()

            elif t in ['s', 'step']:
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

def eval_code(args):
    import tempfile
    code = args.code.replace(';', '\n')

    # add breakpoint at end of script
    code += '\nbrk'

    with tempfile.NamedTemporaryFile(suffix='.asm', delete=False) as f:
        f.write(code.encode('utf8'))
        f.flush()

        hexname = hexup(f.name)
        trigger('debug', hexname)
        Debugger(f.name).run()

def start(args):
    hexname = hexup(args.file)
    trigger('start', hexname)

def main():
    if not JAR_ENVVAR in os.environ:
        print('environment variable', JAR_ENVVAR, 'not set')
        exit()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    debug_parser = subparsers.add_parser('debug', help='start an interactive debug session. press h for help.')
    debug_parser.add_argument('file', type=str)
    debug_parser.set_defaults(func=debug)

    eval_parser = subparsers.add_parser('eval', help='run code as a temporary program. use ; to separate lines. automatically adds a breakpoint at the end of the script.')
    eval_parser.add_argument('code', type=str)
    eval_parser.set_defaults(func=eval_code)

    start_parser = subparsers.add_parser('start', help='start an .asm file in the simulator.')
    start_parser.add_argument('file', type=str)
    start_parser.set_defaults(func=start)

    subparsers.add_parser('measure').set_defaults(func=measure)
    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('step').set_defaults(func=step)
    subparsers.add_parser('stop').set_defaults(func=stop)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
