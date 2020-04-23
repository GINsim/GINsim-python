
import sys

import biolqm

from colomoto_jupyter import *
from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile

from colomoto import ModelState

from .jupyter import upload
from .gateway import japi, restart

import pandas as pd

import ginsim.state

from py4j.java_gateway import JavaObject

def load(filename, *args):
    filename = ensure_localfile(filename)
    obj = japi.gs.load(filename, *args)
    assert obj is not None, "Error while loading model"
    return obj

def service(name):
    return japi.gs.service(name)

def _get_image(lrg, state=None, style=None, fmt="png"):
    srv = japi.gs.service("image")
    
    if state and not style:
        if isinstance(state, dict):
            state = ginsim.state.get_ginsim_state(lrg, state)
        elif isinstance(state, pd.Series):
            # FIXME: here we assume that the Series is using the proper order
            # Fixing the index could be done with:
            # state = state.reindex( ["Proper", "Node", "Order"], fill_value=-1 )
            state = state.values.tobytes()
        
        style = srv.getStyle(lrg, state)
    
    if fmt == "svg":
        if style:
            return srv.getSVG(lrg, style)
        return srv.getSVG(lrg)
    
    if style:
        return srv.rawPNG(lrg, style)
    return srv.rawPNG(lrg)

def lrg_style(lrg):
    return japi.gs.service("image").customStyleProvider(lrg)

def is_ginsim_object(obj):
    """
    Returns true if argument is a GINsim object
    """
    return isinstance(obj, JavaObject) \
        and obj.getClass().getPackage().getName() == "org.ginsim.core.graph.regulatorygraph"

def show(lrg, state=None, style=None, fmt=None, save=None, show=True):
    # Guess format or fix file extension when saving the image
    _supported_formats = set(('svg', 'png'))
    if fmt and fmt not in _supported_formats:
        fmt = None
    sfmt = save and save.split(".")[-1]
    if sfmt not in _supported_formats: sfmt = None
    fmt = fmt or sfmt
    if fmt not in _supported_formats:
        if fmt: print("Unsupported format, revert to default")
        fmt = "png"
    
    img = _get_image(lrg, state, style, fmt)

    if save:
        if sfmt != fmt:
            save = "%s.%s" % (save,fmt)
            print("Saving as %s" % save)
        if fmt == 'svg': mode = 'w'
        else: mode = 'wb'
        out = open(save, mode)
        out.write(img)
        out.close()

    if not show: return

    if not IN_IPYTHON: return img

    return show_image(img, is_svg=(fmt=='svg'))

def to_biolqm(lrg):
    return lrg.getModel()

def to_maboss(lrg):
    return biolqm.to_maboss(lrg.getModel())

def to_pint(lrg, simplify=True):
    return biolqm.to_pint(lrg.getModel(), simplify)

def to_minibn(lrg, **opts):
    return biolqm.to_minibn(lrg.getModel(), **opts)

__nusmvReserved = [ "MODULE", "DEFINE", "MDEFINE",
    "CONSTANTS", "VAR", "IVAR", "FROZENVAR", "INIT", "TRANS", "INVAR",
    "SPEC", "CTLSPEC", "LTLSPEC", "PSLSPEC", "COMPUTE", "NAME",
    "INVARSPEC", "FAIRNESS", "JUSTICE", "COMPASSION", "ISA", "ASSIGN",
    "CONSTRAINT", "SIMPWFF", "CTLWFF", "LTLWFF", "PSLWFF", "COMPWFF",
    "IN", "MIN", "MAX", "MIRROR", "PRED", "PREDICATES", "process",
    "array", "of", "boolean", "integer", "real", "word", "word1",
    "bool", "signed", "unsigned", "extend", "resize", "sizeof",
    "uwconst", "swconst", "EX", "AX", "EF", "AF", "EG", "AG", "E", "F",
    "O", "G", "H", "X", "Y", "Z", "A", "U", "S", "V", "T", "BU", "EBF",
    "ABF", "EBG", "ABG", "case", "esac", "mod", "next", "init",
    "union", "in", "xor", "xnor", "self", "TRUE", "FALSE", "count"]
__nusmvReserved = [k.lower() for k in __nusmvReserved]

def nusmv_var_state(ai):
    a, i = ai
    if len(a) == 1 or a.lower() in __nusmvReserved:
        a = "_%s" % a
    return "%s=%s" % (a,i)

def to_nusmv(lrg, update_mode="async"):
    assert update_mode in ["async", "sync", "complete"], "Unknown update mode"

    serv = service("NuSMV")
    cfg = serv.getConfig(lrg.getModel())

    ## configure update mode
    d_update = {
        "async": cfg.CFG_ASYNC,
        "sync": cfg.CFG_SYNC,
        "complete": cfg.CFG_COMPLETE,
    }
    cfg.setUpdatePolicy(d_update[update_mode])

    ## configure input nodes
    sinit = japi.gs.associated(lrg, "initialState", True)
    for inputNode in sinit.getInputNodes():
        cfg.addFixedInput(str(inputNode))

    smvfile = new_output_file("smv")
    serv.run(cfg, smvfile)
    from colomoto.modelchecking import ColomotoNuSMV
    return ColomotoNuSMV(smvfile, nusmv_var_state)

