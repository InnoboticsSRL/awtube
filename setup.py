from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'awtube'

setup(
    name=package_name,
    version='0.1.0',
    packages=[
        'awtube',
        'awtube.recievers',
        'awtube.builders',
        'awtube.commanders',
        'awtube.config',
        'awtube.cia402',
        'awtube.errors',
        'awtube.logging',
        'awtube.types',
    ],
    data_files=[
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob(
            os.path.join('src/awtube/*.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Armando Selvija',
    maintainer_email='selvija@automationware.it',
    description='Library to interact with the AutomationWare robot.',
    license='',
    tests_require=['pytest'],
    entry_points={},
    package_dir={'': 'src'},
)
