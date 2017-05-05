#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

# load the requirements.txt for additional requirements
from bob.extension.utils import find_packages

setup(
    name='bob.db.swan',
    version=open("version.txt").read().rstrip(),
    description='SWAN Database Access API for Bob',

    url='',
    license='BSD',
    author='Amir Mohammadi',
    author_email='amir.mohammadi@idiap.ch',
    keywords='bob',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    # It will find all package-data inside the 'bob' directory.
    packages=find_packages('bob'),
    include_package_data=True,

    install_requires=['bob.extension',
                      'bob.blitz',
                      'bob.io.base',
                      'bob.io.image',
                      'bob.io.video',
                      'bob.db.base'],

    entry_points={

        'bob.db': ['swan = bob.db.swan.driver:Interface'],
        'console_scripts': [
            'bob_db_swan_generate_filelist = '
            'bob.db.swan.script.generate_filelist:main',
        ],
    },

    classifiers=[
        'Framework :: Bob',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
