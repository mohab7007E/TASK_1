from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'turtle_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohab14',
    maintainer_email='mohab14@todo.todo',
    description='Turtlesim control: goToPose, reset, speeds, square',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'goto_pose_node = turtle_control.goto_pose:main',
            'square_movement_node = turtle_control.square_movment:main',
        ],
    },
)
