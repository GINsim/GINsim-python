
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:

    def export_entry(d, f, e=None):
        if e is None:
            e = f
        return {"name": "{} (.{})".format(d, e),
            "snippet": ['biolqm.save(lqm, "mymodel.{}", "{}")'.format(e, f)]}

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
            {"name": "GINsim", "snippet": [
                'lrg = biolqm.to_ginsim(lqm)']},
            {"name": "MaBoSS", "snippet": [
                'masim = biolqm.to_maboss(lqm)']},
            {"name": "Pint", "snippet": [
                'an = biolqm.to_pint(lqm)']},
            ]},
    "---",
    {"name": "Compute fixpoints",
    #{"name": "Compute fixpoints (MDD method)",
        "snippet": ["fps = biolqm.fixpoints(lqm)"]},
    #{"name": "Compute fixpoints (ASP method)",
    #    "snippet": ["fps = biolqm.fixpoints(lqm, 'asp')"]},
    {"name": "Compute trap spaces",
        "snippet": ["traps = biolqm.trapspace(lqm)"]},
    "---",
    {"name":"Model modifications",
        "sub-menu": [
            {"name": "Perturbation",
                "snippet": ["lqm_mod = biolqm.perturbation(lqm, \"node%0\")"]},
            {"name": "Booleanization",
                "snippet": ["lqm_bool = biolqm.booleanize(lqm)"]},
            {"name": "Reduction",
                "snippet": ["lqm_red = biolqm.reduce(lqm, \"fixed,output,duplicate\")"]},
            {"name": "Reversal",
                "snippet": ["lqm_rev = biolqm.reverse(lqm)"]},
        ]},
     "---",
     {"name": "Documentation",
        "external-link": "http://ginsim.naldi.info/biolqm/site/doc/index.html"}
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
        cell.set_text('lqm = '+biolqm_jsapi.module_alias+'.upload()');
        cell.focus_editor();
    }""",
    }
    jupyter_setup("biolqm",
        label="bioLQM",
        color="#00007f", # for menu and toolbar
        menu=menu,
        toolbar=toolbar,
        js_api=js_api)


    from colomoto_jupyter.upload import jupyter_upload
    def upload():
        return jupyter_upload("upload", "load")

else:
    def upload():
        raise NotImplementedError

