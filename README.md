# digital-asm-headless

A python script to control [Digital](https://github.com/hneemann/Digital).

**Requirements**

- [Assembler](https://github.com/hneemann/Assembler) for compiling code
- &gt;Java 9

## Setup

```
git clone https://github.com/lausek/digital-asm-headless
cd digital-asm-headless

pip3 install .
export DIGASMJAR=<path_to_assembler_jar>
```

## Usage

```
$ digasm
usage: digasm [-h] {start,debug,measure,run,step,stop} ...

positional arguments:
  {start,debug,measure,run,step,stop}

optional arguments:
  -h, --help            show this help message and exit
```
