from setuptools import find_packages
from setuptools import setup

setup(
    name='frs_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('frs_interfaces', 'frs_interfaces.*')),
)
