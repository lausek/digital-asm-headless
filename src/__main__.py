#!/usr/bin/python3

import argparse
import os

try:
    from .cmd import *
    from .debugger import *
    from .default import *
except ImportError:
    from cmd import *
    from debugger import *
    from default import *

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
