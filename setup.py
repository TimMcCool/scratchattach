from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.3.9'
DESCRIPTION = 'An Scratch API Wrapper for scratch.mit.edu'
LONG_DESCRIPTION = DESCRIPTION

# Setting up
setup(
    name="scratchattach",
    version=VERSION,
    author="TimMcCool",
    author_email="timmccool.scratch@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="The package has been renamed to 'scratchattach', please install that instead! Link: https://pypi.org/project/scratchattach/",#open('README.md').read(),
    packages=find_packages(),
    install_requires=["websocket-client","numpy","requests"],
    keywords=['scratch api', 'scratchattach', 'scratch api python', 'scratch python', 'scratch for python', 'scratch', 'scratch cloud', 'scratch cloud variables', 'scratch bot'],
    url='https://github.com/TimMcCool/scratch3.py',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
