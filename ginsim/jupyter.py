
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    menu = [
        {"name": "Upload model",
            "snippet": ["lrg = ginsim.upload()"]},
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
            "icon": "fa-upload",
            "help": "Upload model",
            "handler": "action_upload_model"}},
    ]
    js_api = {
    "action_upload_model": """function() {
        var cell = Jupyter.notebook.get_selected_cell();
        cell.set_text('lrg = '+ginsim_jsapi.module_alias+'.upload()');
        cell.focus_editor();
    }""",
    }
    jupyter_setup("ginsim",
        label="GINsim",
        color="blue", # for menu and toolbar
        menu=menu,
        toolbar=toolbar,
        js_api=js_api)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "load")

else:
    def upload():
        raise NotImplementedError

