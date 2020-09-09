#!/usr/bin/python3

import argparse
import socket
import struct

HOST, PORT = 'localhost', 41114

def pack(msg):
    buf = msg.encode('utf8')
    print(len(buf))
    n = struct.pack('>H', len(buf))
    print(n)
    return n + buf

def main():
    for fam, ty, proto, flags, host in socket.getaddrinfo(HOST, PORT):
        with socket.socket(fam, ty) as s:
            s.connect(host[:2])

            msg = 'start:<path>'
            msg = pack(msg)

            if s.sendall(msg) is None:
                break

if __name__ == '__main__':
    main()
