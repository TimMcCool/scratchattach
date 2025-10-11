from setuptools import setup, find_packages
import codecs
import os

VERSION = '2.1.13'  # consider updating the CLI version number too
DESCRIPTION = 'A Scratch API Wrapper'
with open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().strip().splitlines()

# Setting up
setup(
    name="scratchattach",
    version=VERSION,
    author="TimMcCool",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires='>=3.12',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            "scratch=scratchattach.__main__:main"
        ]
    },
    extras_require={
        "lark": ["lark"]
    },
    keywords=['scratch api', 'scratchattach', 'scratch api python', 'scratch python', 'scratch for python', 'scratch', 'scratch cloud', 'scratch cloud variables', 'scratch bot'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    project_urls={
        "Source": "https://github.com/timmccool/scratchattach",
        "Homepage": 'https://scratchattach.tim1de.net'
    }
)
