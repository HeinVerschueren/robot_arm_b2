from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_arm_b2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/model', ['vision_node/model/best.pt']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='hbl.verschueren@student.avans.nl',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'HMI_node = controller_code.HMI:main',
            'controller = controller_code.controller:main',
            'manipulator_code = manipulatorCodeB2:main',
            'vision_node = vision_node.vision_node.vision_node:main',

            
        ],
    },
)
