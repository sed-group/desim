import setuptools

setuptools.setup(name='desim',
version='0.1.1',
description='A discrete event simulator',
url='https://github.com/EppChops/event-sim',
author='Erik',
install_requires=['simpy', 'numpy'],
author_email='ex',
packages=setuptools.find_packages())