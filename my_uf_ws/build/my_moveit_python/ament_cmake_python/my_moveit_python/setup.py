from setuptools import find_packages
from setuptools import setup

setup(
    name='my_moveit_python',
    version='4.0.0',
    packages=find_packages(
        include=('my_moveit_python', 'my_moveit_python.*')),
)
