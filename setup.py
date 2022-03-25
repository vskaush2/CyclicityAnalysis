from setuptools import setup
setup(
    name='CyclicityAnalysis',
    version='1.0.0',
    url='https://github.com/vskaush2/CyclicityAnalysis',
    packages=['CyclicityAnalysis'],
    license='License :: OSI Approved :: MIT License',
    author='Vivek Kaushik',
    author_email='vskaush2@illinois.edu',
    description='Runs the Cyclicity Analysis procedure on a Collection of Time Series',
    install_requires=['numpy','pandas','plotly','matplotlib'],
    python_requires=">=3.7"
)
