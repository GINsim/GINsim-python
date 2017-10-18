
import sys

from .jupyter import upload

from ginsim.gateway import japi, restart

class BioLQM(object):
    def restart(self):
        restart()

    def upload(self):
        upload()

    def __getattr__(self, name):
        return getattr(japi.lqm, name)

sys.modules[__name__] = BioLQM()


