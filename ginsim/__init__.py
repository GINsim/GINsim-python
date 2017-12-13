
import sys

from .jupyter import upload

from .gateway import japi, restart

import colomoto_jupyter
from colomoto_jupyter.io import ensure_localfile

class GINsim(object):
    def restart(self):
        restart()

    def upload(self):
        upload()

    def __getattr__(self, name):
        return getattr(japi.gs, name)

    def open(self, filename, *args):
        filename = ensure_localfile(filename)
        return japi.gs.open(filename, *args)

    if colomoto_jupyter.IN_IPYTHON:
        def show(self, lrg):
            data = japi.gs.service("image").rawPNG(lrg)
            return colomoto_jupyter.show_image(data)

sys.modules[__name__] = GINsim()



