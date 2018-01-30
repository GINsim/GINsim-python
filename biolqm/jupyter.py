
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:

    def export_entry(d, f, e=None):
        if e is None:
            e = f
        return {"name": "{} (.{})".format(d, e),
            "snippet": ['biolqm.saveModel(lqm, "mymodel.{}", "{}")'.format(e, f)]}

    menu = [
        {"name": "Upload model",
            "snippet": ["lqm = biolqm.upload()"]},
        {"name": "Load model",
            "snippet": ["lqm = biolqm.load(\"model.sbml\")"]},
        "---",
        {"name":"Export to file",
            "sub-menu": [
                export_entry("SBML-qual v1.0", "sbml"),
                "Functions formats",
                export_entry("BoolNet", "bnet"),
                export_entry("BooleanNet", "booleannet"),
                export_entry("BoolSim", "boolsim"),
                export_entry("Raw Boolean functions", "boolfunctions"),
                export_entry("Truth table", "tt"),
                "Petri net formats",
                export_entry("APNN", "apnn"),
                export_entry("INA", "ina"),
                export_entry("PNML", "pnml"),
                "Dedicated formats",
                export_entry("GINML", "ginml"),
                export_entry("GNA non-xml", "gna"),
                export_entry("MaBoSS", "bnd"),
                export_entry("Pint", "an"),
            ]},
        {"name":"Convert to tool",
            "sub-menu": [
            {"name": "MaBoSS", "snippet": [
                'masim = biolqm.to_maboss(lqm)']},
            {"name": "Pint", "snippet": [
                'an = biolqm.to_pint(lqm)']},
            ]},
    ]
    jupyter_setup("biolqm",
        label="bioLQM",
        color="#00007f", # for menu and toolbar
        menu=menu)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "load")

else:
    def upload():
        raise NotImplementedError

