import setuptools

setuptools.setup(name='desim-tool',
version='0.4.8',
description='A discrete event simulator',
url='https://github.com/sed-group/desim',
author='Erik Berg, Oscar Bennet',
install_requires=['simpy', 'numpy'],
author_email='erik.00.berg@gmail.com, oscar.bennet@outlook.com',
packages=setuptools.find_packages())
