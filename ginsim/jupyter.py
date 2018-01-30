
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
                "snippet":['lqm = ginsim.to_biolqm()']},
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
    jupyter_setup("ginsim",
        label="GINsim",
        color="blue", # for menu and toolbar
        menu=menu)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "load")

else:
    def upload():
        raise NotImplementedError

