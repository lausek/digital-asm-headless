import json

try:
    from .util import *
except ImportError:
    from util import *

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
        try:
            from .cmd import trigger
        except ImportError:
            from cmd import trigger
        _, addr = trigger('run')
        self.print_line(int(addr, 16))

    def step(self):
        try:
            from .cmd import trigger
        except ImportError:
            from cmd import trigger
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
