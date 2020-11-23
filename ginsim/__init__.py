
import base64
import re
import sys

import biolqm

from colomoto_jupyter import *
from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile

from colomoto import ModelState

from .jupyter import upload
from .gateway import japi, restart

import pandas as pd
import numpy as np

import ginsim.state

from py4j.java_gateway import JavaObject

if IN_IPYTHON:
    from IPython.display import display, FileLink, HTML

def load(filename, *args):
    filename = ensure_localfile(filename)
    obj = japi.gs.load(filename, *args)
    assert obj is not None, "Error while loading model"
    return obj

def service(name):
    return japi.gs.service(name)

_default_image_format = "svg"

def _get_image(lrg, state=None, style=None, fmt=None, checkorder=True):
    srv = japi.gs.service("image")
    
    if state is not None and style is None:
        if isinstance(state, dict):
            state = ginsim.state.get_ginsim_state(lrg, state)
        elif isinstance(state, pd.Series):
            if checkorder:
                state = state.reindex( [n.getId() for n in lrg.getNodeOrder() ], fill_value=-100 )
            state = state.astype(np.byte).values.tobytes()
        
        style = srv.getStyle(lrg, state)
    
    if fmt is None: fmt = _default_image_format
    
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


_re_undim = re.compile(r'(<svg [^>]*)(height|width)="[^"]*"')
def _svg_undim(data):
    for i in range(2):
        data = _re_undim.sub(r"\1", data, count=1)
    return data

def show(lrg, state=None, style=None, fmt=None, save=None,
        scale="auto", show=True, checkorder=True):

    # Guess format or fix file extension when saving the image
    _supported_formats = set(('svg', 'png'))
    if fmt and fmt not in _supported_formats:
        fmt = None
    sfmt = save and save.split(".")[-1]
    if sfmt not in _supported_formats: sfmt = None
    fmt = fmt or sfmt
    if fmt not in _supported_formats:
        if fmt: print("Unsupported format, revert to default")
        fmt = _default_image_format

    img = _get_image(lrg, state, style, fmt, checkorder)

    if save:
        if sfmt != fmt:
            save = "%s.%s" % (save,fmt)
            print("Saving as %s" % save)
        mode = "w" if fmt == "svg" else "wb"
        with open(save, mode) as out:
            out.write(img)
        if IN_IPYTHON:
            display(FileLink(save, result_html_prefix="Saved as "))
    if not show:
        return
    if not IN_IPYTHON:
        return img

    if fmt == "svg":
        dim = lrg.getDimension()
        width, height = None, None
        if scale.endswith("%"):
            scale = int(scale[:-1])/100
        if scale == "auto":
            width = f"{dim.width}px" if dim.width <= 800 else "100%"
        elif not isinstance(scale, str):
            width = f"{int(dim.width*scale)}px"
            height = f"{int(dim.height*scale)}px"
        else:
            width = scale
        if show == True or show == "img":
            svg64 = base64.b64encode(img.encode("utf-8")).decode()
            html = f'<img class="unconfined" width="{width}" src="data:image/svg+xml;base64,{svg64}">'
            return HTML(html)
        elif show == "inline":
            my_width = f'width="{width}"' if width is not None else ""
            my_height = f'height="{height}"' if height is not None else ""
            img = _svg_undim(img)
            img = img.replace("<svg ",
                f"<svg {my_width} {my_height} viewBox=\"0 0 {dim.width} {dim.height}\" ")
        else:
            raise TypeError("Invalid value for show parameter")

    return show_image(img, is_svg=(fmt=='svg'))

def to_biolqm(lrg):
    return lrg.getModel()

def to_maboss(lrg):
    return biolqm.to_maboss(lrg.getModel())

def to_pint(lrg, simplify=True):
    return biolqm.to_pint(lrg.getModel(), simplify)

def to_pyboolnet(lrg):
    return biolqm.to_pyboolnet(lrg.getModel())

def to_booleannet(model, mode='async'):
    return biolqm.to_booleannet(lrg.getModel(), mode)

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

    smvfile = new_output_file("smv")
    serv.run(cfg, smvfile)
    from colomoto.modelchecking import ColomotoNuSMV
    return ColomotoNuSMV(smvfile, nusmv_var_state)

