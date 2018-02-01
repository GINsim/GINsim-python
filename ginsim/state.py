from colomoto import ModelState

import ginsim
import py4j

import sys
import biolqm

from ginsim.gateway import register


def get_ginsim_state(lrg, state):
    order = lrg.getNodeOrder()
    l = len(order)
    gw = ginsim.japi.java
    int_class = gw.jvm.int
    int_array = gw.new_array(int_class, l)
    i = 0
    for node in order:
        uid = node.getId()
        if uid in state:
            int_array[i] = state[uid]
        i += 1
    
    return int_array

def get_model_state(nodes, state):
    mstate = ModelState()
    l = len(nodes)
    for i in range(l):
        mstate[ nodes[i].getNodeID() ] = state[i]
    
    return mstate


def convert_fixpoints(stables):
    if stables == None or len(stables) < 1:
        return []
    return [ get_model_state(stables.nodes, state) for state in stables ]

def convert_trapspace(traps):
    if traps == None or len(traps) < 1:
        return []
    return [ get_model_state(traps.nodes, state.pattern) for state in traps ]

biolqm._japi_converters['fixpoints'] = convert_fixpoints
biolqm._japi_converters['stable'] = convert_fixpoints
biolqm._japi_converters['trapspace'] = convert_trapspace

