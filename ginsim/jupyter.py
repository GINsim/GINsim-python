
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    menu = [
        {"name": "Upload model",
            "snippet": ["ginsim.upload()"]},
        {"name": "Load model",
            "snippet": ["ginsim.open(\"model.zginml\")"]},
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

