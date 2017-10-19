
import sys

from .jupyter import upload

from .gateway import japi, restart

import colomoto_jupyter

class GINsim(object):
    def restart(self):
        restart()

    def upload(self):
        upload()

    def __getattr__(self, name):
        return getattr(japi.gs, name)

    if colomoto_jupyter.IN_IPYTHON:
        def show(self, lrg):
            b64 = japi.gs.service("image").base64PNG(lrg)
            return colomoto_jupyter.show_image(b64)

sys.modules[__name__] = GINsim()



