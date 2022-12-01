import setuptools

setuptools.setup(name='desim-tool',
version='0.3.1',
description='A discrete event simulator',
url='https://github.com/sed-group/desim',
author='Erik',
install_requires=['simpy', 'numpy'],
author_email='erik.00.berg@gmail.com',
packages=setuptools.find_packages())