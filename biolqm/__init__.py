
import sys

from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload

from ginsim.gateway import japi, restart

def load(filename, *args):
    filename = ensure_localfile(filename)
    return japi.lqm.loadModel(filename, *args)

def saveModel(model, filename, format=None):
    return japi.lqm.saveModel(model, filename, format)

def modifyModel(model, modifier, *args):
    return japi.lqm.modifyModel(model, modifier, *args)

def getFormat(name):
    return japi.lqm.getFormat(name)

def getModifier(name):
    return japi.lqm.getModifier(name)

def getTool(name):
    return japi.lqm.getTool(name)

def to_maboss(model, simulation_name="master"):
    import maboss
    maboss_file = new_output_file("bnd")
    assert saveModel(model, maboss_file, "bnd")
    return maboss.load_file(maboss_file, "%s.cfg" % maboss_file,
                simulation_name=simulation_name)

def to_pint(model, simplify=True):
    anfile = new_output_file("an")
    assert saveModel(model, anfile, "an")
    import pypint
    an = pypint.load(anfile)
    if simplify:
        an = an.simplify()
    return an
