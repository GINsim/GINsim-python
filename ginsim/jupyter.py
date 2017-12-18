
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    menu = [
        {"name": "Upload model",
            "snippet": ["lrg = ginsim.upload()"]},
        {"name": "Load model",
            "snippet": ["lrg = ginsim.open(\"model.zginml\")"]},
        "---",
        {"name":"Export to file",
            "sub-menu": [
            {"name": "MaBoSS (.bnd, .cfg)",
                "snippet":['ginsim.service("maboss").export(lrg, "mymodel.bnd")']},
            ]},
        {"name":"Convert to tool",
            "sub-menu": [
            {"name": "BioLQM",
                "snippet":['lqm = lrg.getModel()']},
            {"name": "MaBoSS",
                "snippet":[
                    'ginsim.service("maboss").export(lrg, "mymodel.bnd")',
                    'master_simulation = maboss.load_file("mymodel.bnd", simulation_name="master")']},
            ]},
    ]
    jupyter_setup("ginsim",
        label="GINsim",
        color="blue", # for menu and toolbar
        menu=menu)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "open")

else:
    def upload():
        raise NotImplementedError

