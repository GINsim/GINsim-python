
import sys

from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile
from colomoto_jupyter import import_colomoto_tool

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

def to_maboss(model):
    import_colomoto_tool("maboss")
    maboss_file = new_output_file("bnd")
    assert saveModel(model, maboss_file, "bnd")
    return maboss.load(maboss_file, "%s.cfg" % maboss_file)

def to_pint(model, simplify=True):
    anfile = new_output_file("an")
    assert saveModel(model, anfile, "an")
    import_colomoto_tool("pypint")
    an = pypint.load(anfile)
    if simplify:
        an = an.simplify()
    return an
