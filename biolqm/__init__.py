
import sys

from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile
from colomoto_jupyter import import_colomoto_tool

from .jupyter import upload

from ginsim.gateway import japi, restart

_japi_wrappers = set()

class LQMTool:
    def __init__(self, tool):
        self.tool = tool
    
    def setup(self, model, parameters=''):
        return self.tool.getSettings(model, parameters)
    
    def get(self, settings):
        return self.tool.getResult(settings)
    
    def __call__(self, model, parameters=''):
        settings = self.setup(model, parameters)
        return self.get(settings)
    
    def __getattr__(self, name):
        return self.tool.__getattr__(name)

class LQMModifier:
    def __init__(self, modifier):
        self.modifier = modifier
    
    def __call__(self, model, parameters=None):
        return self.modifier.getModifiedModel(model, parameters)
    
    def __getattr__(self, name):
        return self.modifier.__getattr__(name)

def _japi_start():
    current_module = __import__(__name__)
    
    for tool in japi.java.jvm.org.colomoto.biolqm.LQMServiceManager.getTools():
        name = tool.getID()
        wrapper = LQMTool(tool)
        setattr(current_module, name, wrapper)
        _japi_wrappers.add(name)

    for mod in japi.java.jvm.org.colomoto.biolqm.LQMServiceManager.getModifiers():
        name = mod.getID()
        wrapper = LQMModifier(mod)
        setattr(current_module, name, wrapper)
        _japi_wrappers.add(name)

def _japi_stop():
    current_module = __import__(__name__)
    for name in _japi_wrappers:
        delattr(current_module, name)
    _japi_wrappers.clear()

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
