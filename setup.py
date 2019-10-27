#!/usr/bin/env python3
"""Setup pattoo-shared package."""

# Import setup
import setuptools

# Read the description file
with open('README.rst', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    # Background information on PIP package
    name='PattooShared',
    url='https://github.com/PalisadoesFoundation/pattoo-shared',
    download_url='https://github.com/PalisadoesFoundation/pattoo-shared',

    # Who to call
    author='Peter Harrison',
    author_email='peter@palisadoes.org',
    maintainer='Peter Harrison',
    maintainer_email='peter@palisadoes.org',

    # The license can be anything you like
    license='MIT',

    # Automatically find the required package dependencies
    packages=setuptools.find_packages(),

    # Create a description of the package
    description='Shared libraries for Pattoo Servers and Agents.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',

    # Minium python version
    python_requires='>=3.6',

    # Set up the version
    version='0.0.9',
)
