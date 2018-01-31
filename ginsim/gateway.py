
import atexit
import subprocess
from subprocess import PIPE

from py4j.java_gateway import JavaGateway, GatewayParameters

__env = {}
__registered = []

class LQMProxy(object):
    java = None
    gs = None
    lqm = None
    def clear(self):
        self.java = None
        self.gs = None
        self.lqm = None

japi = LQMProxy()

def start():
    assert (not __env)
    __env["proc"] = subprocess.Popen(["GINsim", "-py"], \
                        stdout=PIPE, stdin=PIPE, stderr=PIPE)
    port = int(__env["proc"].stdout.readline().strip())

    # start the gateway and return the entry point (GINsim's ScriptLauncher)
    param = GatewayParameters(port=port, auto_convert=True, auto_field=True)
    __env["gw"] = JavaGateway(gateway_parameters=param)

    global japi
    japi.java = __env["gw"]
    japi.gs = __env["gw"].entry_point
    japi.lqm = japi.gs.LQM()
    for module in __registered:
        module._japi_start()

def stop():
    if not __env:
        return
    global japi
    japi.clear()
    __env["gw"].shutdown()
    __env["proc"].terminate()
    __env.clear()
    for module in __registered:
        module._japi_stop()

def restart():
    stop()
    start()

def register(module):
    __registered.append(module)
    if __env:
        module._japi_start()

start()
atexit.register(stop)

