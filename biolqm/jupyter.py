
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    menu = [
        {"name": "Upload model",
            "snippet": ["lqm = biolqm.upload()"]},
        {"name": "Load model",
            "snippet": ["lqm = biolqm.loadModel(\"model.sbml\")"]},
    ]
    jupyter_setup("biolqm",
        label="BioLQM",
        color="#00007f", # for menu and toolbar
        menu=menu)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "loadModel")

else:
    def upload():
        raise NotImplementedError

