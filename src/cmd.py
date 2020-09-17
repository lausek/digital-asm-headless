import os
import os.path
import socket
import struct
import subprocess

try:
    from .debugger import *
    from .default import *
    from .util import *
except ImportError:
    from debugger import *
    from default import *
    from util import *

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

    with tempfile.NamedTemporaryFile(suffix='.asm') as f:
        f.write(code.encode('utf8'))
        f.flush()

        hexname = hexup(f.name)
        trigger('debug', hexname)
        Debugger(f.name).run()

def start(args):
    hexname = hexup(args.file)
    trigger('start', hexname)
