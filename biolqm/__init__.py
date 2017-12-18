
import sys

from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload

from ginsim.gateway import japi, restart

def loadModel(filename, *args):
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

