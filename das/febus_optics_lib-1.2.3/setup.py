#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: robin.guerry
python setup.py sdist
"""
from setuptools import setup, find_packages

with open("README.md", "r") as r_file:
    description = r_file.read()

setup(
    name="febus_optics_lib",
    version="1.2.3",
    url='-',
    author="robin guerry",
    author_email="robin.guerry@febus-optics.com",
    packages=find_packages(),
    include_package_data=True, 
    python_requires=">=3.6",
    install_requires=[
        'h5py>=3.1',
        'numpy>=1.19.5',
        'scipy>=1.5.4',
        'matplotlib>=3.3.4',
        'psutil>=6.1.1'
    ],
    description="A FEBUS Optics package",
    long_description=description,
    long_description_content_type="text/markdown",
)