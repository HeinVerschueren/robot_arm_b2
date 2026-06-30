import os
from setuptools import find_packages, setup
from glob import glob

package_name = 'testfile'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
        glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='F.landsman@student.avans.nl',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'controller = testfile.controller:main',
            'HMI = testfile.HMI:main',
            'vision_node = testfile.vision_node:main',
            'manipulatorCodeB2 = testfile.manipulatorCodeB2:main',
        ],
    },
)
