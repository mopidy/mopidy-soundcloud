from __future__ import unicode_literals

import re
from setuptools import setup, find_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']

print(find_packages(exclude=['tests', 'tests.*']))

setup(
    name='Mopidy-SoundCloud',
    version=get_version('mopidy_soundcloud/__init__.py'),
    url='http://github.com/dz0ny/mopidy-soundcloud/',
    license='MIT',
    author='dz0ny',
    author_email='dz0ny@shortmail.com',
    description='SoundCloud extension for Mopidy',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy',
        'requests',
    ],
    entry_points={
        b'mopidy.extension': [
            'soundcloud = mopidy_soundcloud:SoundCloudExtension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
