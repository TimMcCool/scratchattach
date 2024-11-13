from setuptools import setup, find_packages
import codecs
import os

VERSION = '2.1.6'
DESCRIPTION = 'A Scratch API Wrapper'
LONG_DESCRIPTION = DESCRIPTION

# Setting up
setup(
    name="scratchattach",
    version=VERSION,
    author="TimMcCool",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open('README.md', encoding='utf-8').read(),
    packages=find_packages(),
    install_requires=["websocket-client","requests","bs4","SimpleWebSocketServer"],
    keywords=['scratch api', 'scratchattach', 'scratch api python', 'scratch python', 'scratch for python', 'scratch', 'scratch cloud', 'scratch cloud variables', 'scratch bot'],
    url='https://scratchattach.tim1de.net',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
