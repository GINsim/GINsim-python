
import sys

from colomoto_jupyter import *
from colomoto_jupyter.sessionfiles import new_output_file
from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload
from .gateway import japi, restart

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
    return maboss.load_file(maboss_file, "%s.cfg" % maboss_file,
            simulation_name=simulation_name)

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

