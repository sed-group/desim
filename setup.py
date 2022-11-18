import setuptools

setuptools.setup(name='desim-tool',
version='0.2.2',
description='A discrete event simulator',
url='https://github.com/EppChops/event-sim',
author='Erik',
install_requires=['simpy', 'numpy'],
author_email='erik.00.berg@gmail.com',
packages=setuptools.find_packages())