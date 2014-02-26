#!/usr/bin/env python
'''
Build script.
'''
import os.path

from setuptools import setup, find_packages


setup(
    name='cacophony',
    version='0.0.1',
    author='Steve Milner',
    url='https://github.com/RHInception/cacophony',
    license='AGPLv3',
    zip_safe=False,
    package_dir={
        'cacophony': os.path.join('src', 'cacophony')
    },
    packages=find_packages('src'),
    install_requires=[
        'flask>=0.9',
        'pyOpenSSL',
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python'],

)
