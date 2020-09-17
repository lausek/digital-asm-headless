import os.path

def patch_extension(fname, ext):
    fname = os.path.realpath(fname)
    return os.path.splitext(fname)[0] + ext
