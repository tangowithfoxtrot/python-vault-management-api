import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="vault_management_api",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required
)
