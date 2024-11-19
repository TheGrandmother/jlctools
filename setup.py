from setuptools import setup, find_packages

setup(
    name="jlctools",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "jlcsearch = tools.jlcsearch:run",
            "jlcbomcheck = tools.part_checker:run",
        ],
    },
)
