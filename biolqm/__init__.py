
import sys

from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile
from colomoto_jupyter import import_colomoto_tool

from .jupyter import upload


from ginsim.gateway import japi, restart
from ginsim.state import *


class LQMTool:
    def __init__(self, tool):
        self.uid = tool.getID()
        self.tool = tool
    
    def setup(self, model, parameters=''):
        return self.tool.getSettings(model, parameters)
    
    def get(self, settings):
        result = self.tool.getResult(settings)
        if self.uid in _japi_converters:
            return _japi_converters[self.uid](result)
        
        return result
    
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


def convert_fixpoints(stables):
    if stables == None or len(stables) < 1:
        return []
    return [ get_model_state(stables.nodes, state) for state in stables ]

def convert_trapspace(traps):
    if traps == None or len(traps) < 1:
        return []
    return [ get_model_state(traps.nodes, state.pattern) for state in traps ]


class SimulationIterable:
    def __init__(self, simulation):
        self.simulation = simulation
    
    def __iter__(self):
        return SimulationIterator(self.simulation)

class SimulationIterator:
    def __init__(self, simulation):
        self.iterator = simulation.iterator()
        self.nodes = simulation.getNodes()
    
    def __next__(self):
        if self.iterator.hasNext():
            return get_model_state(self.nodes, self.iterator.next())
        raise StopIteration()

def convert_trace(simulation):
    if simulation == None:
        return []
    return SimulationIterable(simulation)

_japi_wrappers = set()
_japi_converters = {
    "fixpoints": convert_fixpoints,
    "trapspace": convert_trapspace,
    "trace": convert_trace,
    "random": convert_trace,
}

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

def to_ginsim(model):
    """
    Convert a bioLQM model into an equivalent GINsim model using the
    :py:mod:`ginsim` Python module.
    Please note that no layout is set for the regulatory graph.
    """
    import_colomoto_tool("ginsim")
    ginml_file = new_output_file("ginml")
    assert saveModel(model, ginml_file, "ginml")
    return ginsim.load(ginml_file)

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

from ginsim.gateway import register
register(sys.modules[__name__])
del(register)

