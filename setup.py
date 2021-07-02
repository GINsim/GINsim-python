
from distutils.command.install import install
from setuptools import setup, find_packages

NAME = 'ginsim'

class post_install(install):
    def run(self):
        super().run()
        from colomoto.setup_helper import setup as colomoto_setup
        colomoto_setup({"pkg": "colomoto/ginsim",
                "check_progs": ["GINsim"]},
            {"pkg": "potassco/clingo",
                "check_progs": ["clingo"]}, force=True, parse_args=False)

setup(name=NAME,
    version='9999',
    author = "Aurélien Naldi",
    author_email = "aurelien.naldi@gmail.com",
    url = "https://github.com/GINsim/GINsim-python",
    description = "Python interface to GINsim and BioLQM API",
    long_description = """
Provides interface to Java API of GINsim and BioLQM
""",
    install_requires = [
        "py4j",
        "colomoto_jupyter >= 0.6.3",
    ],
    py_modules = ["ginsim_setup"],
    packages = find_packages(),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    keywords="computational systems biology",
    cmdclass = {
        "install": post_install,
    }
)

