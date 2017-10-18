
import atexit
import subprocess
from subprocess import PIPE

from py4j.java_gateway import JavaGateway, GatewayParameters

__env = {}

class LQMProxy(object):
    gs = None
    lqm = None
    def clear(self):
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
    japi.gs = __env["gw"].entry_point
    japi.lqm = japi.gs.LQM()

def stop():
    global japi
    japi.clear()
    __env["gw"].shutdown()
    __env["proc"].terminate()
    __env.clear()

def restart():
    stop()
    start()

start()
atexit.register(stop)

