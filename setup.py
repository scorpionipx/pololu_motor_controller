from setuptools import setup, find_packages


from pololu_motor_controller.version import __version__


setup(
    name='pololu_motor_controller',
    version=__version__,
    author='uidq6025',
    author_email='scorpionipx@gmail.com',
    packages=find_packages(exclude=['tests', ]),
    description='Pololu Motor Controller',
    long_description=open('README.md').read(),
    install_requires=[
        'pyserial',
    ],
)


# cmd: py setup.py sdist
