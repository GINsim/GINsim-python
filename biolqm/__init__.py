
import sys

from colomoto_jupyter.io import ensure_localfile

from .jupyter import upload

from ginsim.gateway import japi, restart

class BioLQM(object):
    def restart(self):
        restart()

    def upload(self):
        upload()

    def loadModel(self, filename, *args):
        filename = ensure_localfile(filename)
        return japi.lqm.loadModel(filename, *args)

    def __getattr__(self, name):
        return getattr(japi.lqm, name)

sys.modules[__name__] = BioLQM()


