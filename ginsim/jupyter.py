
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    from colomoto_jupyter.ipylab import ipylab_insert_snippet, \
        ipylab_upload_and_process_filename

    def upload(model):
        def callback(filename:str):
            ipylab_insert_snippet(f"{model} = ginsim.load('{filename}')", True)
        ipylab_upload_and_process_filename(callback)

    menu = [
        {"name": "Upload model",
            "snippet": ["ginsim.upload('lrg')"]},
        {"name": "Load model",
            "snippet": ["lrg = ginsim.load(\"model.zginml\")"]},
        "---",
        {"name":"Export to file",
            "sub-menu": [
            {"name": "MaBoSS (.bnd, .cfg)",
                "snippet":['ginsim.service("maboss").export(lrg, "mymodel.bnd")']},
            ]},
        {"name":"Convert to tool",
            "sub-menu": [
            {"name": "bioLQM",
                "snippet":['lqm = ginsim.to_biolqm(lrg)']},
            {"name": "MaBoSS",
                "snippet":['masim = ginsim.to_maboss(lrg)']},
            {"name": "NuSMV",
                "snippet":['smv = ginsim.to_nusmv(lrg)']},
            {"name": "Pint",
                "snippet":['an = ginsim.to_pint(lrg)']},
            ]},
        "---",
        {"name": " Display regulatory graph",
            "snippet": ["ginsim.show(lrg)"]},
    ]
    toolbar = [
        {"name": "upload", "setup": {
            "icon": "fa fa-upload",
            "label" : "GINsim",
            "help": "Upload GINsim model",
            "handler": ipylab_insert_snippet,
            "args" : { 'snippet': "ginsim.upload('lrg')" },
            "after" : "biolqm_upload"
        }},
    ]
    js_api = {
    }
    jupyter_setup("ginsim",
        label="GINsim",
        color="blue", # for menu and toolbar
        menu=menu,
        toolbar=toolbar,
        js_api=js_api)

else:
    def upload():
        raise NotImplementedError

