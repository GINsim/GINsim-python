
from setuptools import setup, find_packages

NAME = 'ginsim'

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
)

