
import sys

from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile
from colomoto_jupyter import import_colomoto_tool

from .jupyter import upload

import pandas as pd
import numpy as np

from ginsim.gateway import japi, restart
from ginsim.state import *

from py4j.java_gateway import JavaObject

class LQMTool:
    def __init__(self, tool):
        self._uid = tool.getID()
        self._tool = tool

    def getTask(self, model, parameters=None):
        if parameters:
            task = self._tool.getTask(model, parameters)
        else:
            task = self._tool.getTask(model)
        
        if self._uid in _japi_converters:
            return LQMTask(task, _japi_converters[self._uid])
        
        return LQMTask(task)

    def __call__(self, model, parameters=None, autoconvert=True):
        return self.getTask(model, parameters)(autoconvert)

    def __getattr__(self, name):
        return self._tool.__getattr__(name)

class LQMTask:
    def __init__(self, task, convert=None):
        self._task = task
        self._convert = convert

    def __call__(self, autoconvert=True):
        result = self._task.call()
        
        if autoconvert and self._convert:
            return self._convert(result)
        
        return result

    def __getattr__(self, name):
        return self._task.__getattr__(name)

class LQMModifier:
    def __init__(self, modifier):
        self._modifier = modifier

    def getModifier(self, model, parameters=None):
        if parameters:
            mod = self._modifier.getModifier(model, parameters)
        else:
            mod = self._modifier.getModifier(model)
        return mod

    def __call__(self, model, parameters=None):
        return self.getModifier(model, parameters).call()
    
    def __getattr__(self, name):
        return self._modifier.__getattr__(name)


def states_to_dataframe(states):
    if states == None or len(states) < 1:
        return []
    
    ids = [str(n) for n in states.getComponents()]
    data = [ np.frombuffer(states.fillState(None,idx), dtype=np.byte) for idx in range(len(states)) ]
    data = np.concatenate(data)
    data = data.reshape( (states.size(), len(ids)) )
    ids = [n.getNodeID() for n in states.getComponents()]
    return pd.DataFrame(data, columns=ids)


def convert_fixpoints(stables):
    if stables == None or len(stables) < 1:
        return []
    return [ get_model_state(stables.getComponents(), state) for state in stables ]

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
    "trapspaces": convert_trapspace,
    "trace": convert_trace,
    "random": convert_trace,
}

def _japi_start():
    current_module = __import__(__name__)
    
    for tool in japi.java.jvm.org.colomoto.biolqm.service.LQMServiceManager.getTools():
        name = tool.getID()
        wrapper = LQMTool(tool)
        setattr(current_module, name, wrapper)
        _japi_wrappers.add(name)
        aliases = tool.getAliases()
        if aliases:
            for alias in aliases:
                setattr(current_module, alias, wrapper)

    for mod in japi.java.jvm.org.colomoto.biolqm.service.LQMServiceManager.getModifiers():
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
    obj = japi.lqm.load(filename, *args)
    assert obj is not None, "Error while loading model"
    return obj

def save(model, filename, format=None):
    assert japi.lqm.save(model, filename, format)
    return filename

def modify(model, modifier, *args):
    return japi.lqm.modify(model, modifier, *args)

def getFormat(name):
    return japi.lqm.getFormat(name)

def getModifier(name):
    return japi.lqm.getModifier(name)

def getTool(name):
    return japi.lqm.getTool(name)

def is_biolqm_object(obj):
    """
    Returns true if argument is a bioLQM object
    """
    return isinstance(obj, JavaObject) \
        and obj.getClass().getPackage().getName() == "org.colomoto.biolqm"

def influence_graph(model):
    import networkx
    matrix = japi.java.jvm.org.colomoto.biolqm.ConnectivityMatrix(model)
    cnodes = model.getComponents()
    enodes = model.getExtraComponents()
    edges = []
    for (nodes, extra) in [(cnodes, False), (enodes, True)]:
        for idx in range(len(nodes)):
            a  = nodes.get(idx).getNodeID()
            regulators = matrix.getRegulators(idx, extra)
            if not regulators:
                continue
            effects = matrix.getRegulatorEffects(idx, extra)
            for i in range(len(regulators)):
                reg = regulators[i]
                b = nodes.get(reg).getNodeID()
                curEffects = effects[i]
                for v in range(len(curEffects)):
                    e = curEffects[v]
                    if e == e.NONE:
                        continue
                    elif e == e.POSITIVE:
                        sign = 1
                    elif e == e.NEGATIVE:
                        sign = -1
                    else:
                        sign = 0
                    edges.append((b,sign,a))
    ig = networkx.MultiDiGraph()
    labels = {1: "+", -1: "-", 0: "?"}
    for (b, sign, a) in edges:
        ig.add_edge(b, a, sign=sign, label=labels[sign])
    return ig

default_layout = "neato"

def autolayout(model, method=default_layout, scale="auto"):
    from colomoto.helpers import layout_graph
    if scale == "auto":
        default = 1
        scales = {
            "dot": 0.25,
            "circo": 0.4,
            "neato": 0.55,
        }
        scale = scales.get(method, default)
    ig = influence_graph(model)
    layout = layout_graph(ig, method=method, scale=scale*200)
    add_layout(model, layout)

def to_ginsim(model, ensure_layout=True,
        layout_method=default_layout, layout_scale="auto"):
    """
    Convert a bioLQM model into an equivalent GINsim model using the
    :py:mod:`ginsim` Python module.
    """
    if ensure_layout and not model.hasLayout():
        autolayout(model, method=layout_method, scale=layout_scale)
    return japi.gs.load(model)

def to_maboss(model):
    maboss = import_colomoto_tool("maboss")
    maboss_file = new_output_file("bnd")
    assert save(model, maboss_file, "bnd")
    return maboss.load(maboss_file, "%s.cfg" % maboss_file)

def to_pint(model, simplify=False):
    anfile = new_output_file("an")
    assert save(model, anfile, "an")
    pypint = import_colomoto_tool("pypint")
    an = pypint.load(anfile)
    if simplify:
        an = an.simplify()
    return an

def to_minibn(model):
    from colomoto import minibn
    if model.isBoolean():
        fmt = "bnet"
        cls = minibn.BooleanNetwork
    else:
        fmt = "mnet"
        cls = minibn.MultiValuedNetwork
    bnfile = new_output_file(fmt)
    assert save(model, bnfile, fmt)
    with open(bnfile) as data:
        return cls(data)


def add_layout(model, layout):
    """
    Add layout information to a model
    The layout object should be a dict of dicts in which the 'nodes' entry is
    a dict giving the (x, y) position of all nodes, identified by their uid.
    """
    inner = model.getLayout()
    for uid, values in layout['nodes'].items():
        ni = model.getComponent(uid)
        if ni:
            inner.setPosition(ni, int(values['x']), int(values['y']))
        else:
            print("no such node: ", uid)


from ginsim.gateway import register
register(sys.modules[__name__])
del(register)

