
from colomoto_jupyter import IN_IPYTHON, jupyter_setup

if IN_IPYTHON:
    from colomoto_jupyter.ipylab import ipylab_insert_snippet, \
        ipylab_upload_and_process_filename

    def upload(model):
        def callback(filename:str):
            ipylab_insert_snippet(f"{model} = biolqm.load('{filename}')",
                                  run_it = True)
        ipylab_upload_and_process_filename(callback)

    def export_entry(d, f, e=None):
        if e is None:
            e = f
        return {"name": "{} (.{})".format(d, e),
            "snippet": ['biolqm.save(lqm, "mymodel.{}", "{}")'.format(e, f)]}

    menu = [
        {"name": "Upload model",
            "snippet": ["biolqm.upload('lqm')"]},
        {"name": "Load model",
            "snippet": ["lqm = biolqm.load(\"model.sbml\")"]},
        "---",
        {"name": "Export to file",
         "sub-menu": [
             export_entry("SBML-qual v1.0", "sbml"),
             {"name": "Functions formats",
              "sub-menu": [
                  export_entry("BoolNet", "bnet"),
                  export_entry("BooleanNet", "booleannet"),
                  export_entry("BoolSim", "boolsim"),
                  export_entry("Raw Boolean functions", "boolfunctions"),
                  export_entry("Truth table", "tt")]},
             {"name": "Petri net formats",
              "sub-menu": [
                  export_entry("APNN", "apnn"),
                  export_entry("INA", "ina"),
                  export_entry("PNML", "pnml")
              ]
              },
             {"name": "Dedicated formats",
              "sub-menu": [
                  export_entry("GINML", "ginml"),
                  export_entry("GNA non-xml", "gna"),
                  export_entry("MaBoSS", "bnd"),
                  export_entry("Pint", "an"),
              ]}
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
            {"name": "Sanitize",
                "snippet": ["lqm_san = biolqm.sanitize(lqm)"]},
        ]},
     "---",
     {"name": "Documentation",
        "external-link": "http://ginsim.naldi.info/biolqm/site/doc/index.html"}
    ]
    toolbar = [
        {"name": "upload", "setup": {
            "icon": "fa fa-upload",
            "label" : "bioLQM",
            "help": "Upload bioLQM model",
            "handler": ipylab_insert_snippet,
            "args" : { "snippet" : "biolqm.upload('lqm')" }
        }},
    ]

    js_api = {
    }

    jupyter_setup("biolqm",
        label="bioLQM",
        color="#00007f", # for menu and toolbar
        menu=menu,
        toolbar=toolbar,
        js_api=js_api)

else:
    def upload():
        raise NotImplementedError

