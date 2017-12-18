
import sys

from .jupyter import upload

from .gateway import japi, restart

from colomoto_jupyter import *
from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile

def open(filename, *args):
    filename = ensure_localfile(filename)
    return japi.gs.open(filename, *args)

def service(name):
    return japi.gs.service(name)

if IN_IPYTHON:
    def show(lrg):
        data = japi.gs.service("image").rawPNG(lrg)
        return show_image(data)

def to_maboss(lrg, simulation_name="master"):
    import maboss
    maboss_file = new_output_file("bnd")
    service("maboss").export(lrg, maboss_file)
    return maboss.load_file(maboss_file, simulation_name=simulation_name)

