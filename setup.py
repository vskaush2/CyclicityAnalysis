import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Cyclicity Analysis",
    version="1.0.0",
    author="Vivek Kaushik",
    author_email="vskaush2@illinois.edu",
    description="Performs Cyclicity Analysis on a Collection of Time-Series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vskaush2/CyclicityAnalysis",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)