from setuptools import setup
import os

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='CyclicityAnalysis',
    version='1.0.0',
    packages=[''],
    url='https://github.com/vskaush2/CyclicityAnalysis',
    license='',
    author='Vivek Kaushik',
    author_email='vskaush2@illinois.edu',
    description='Runs Cyclicity Analysis on a Collection of Time Series',
    install_requires=required,
)
