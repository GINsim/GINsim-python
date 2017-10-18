
import sys

from .jupyter import upload

from .gateway import japi, restart

class GINsim(object):
    def restart(self):
        restart()

    def upload(self):
        upload()

    def __getattr__(self, name):
        return getattr(japi.gs, name)

sys.modules[__name__] = GINsim()



