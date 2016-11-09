"""Identity service setup.py"""

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def readme():
    """Long form readme for the identity service."""
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='identity',
    version='1.4.2',
    description='The identity service for Ocelot, as a Python package.',
    long_description=readme(),
    keywords='ocelot-saas identity service rest api',
    url='http://github.com/ocelot-saas/identity',
    author='Horia Coman',
    author_email='horia141@gmail.com',
    license='All right reserved',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=[
        # Duplicated from requirements.txt.
        'auth0-python>=2,<3',
        'clock==0.0.5',
        'falcon>=1,<2',
        'falcon-cors>=1,<2',
        'gunicorn>=19,<20',
        'jsonschema>=2,<3',
        'pytz==2016.4',
        'requests>=2,<3',
        'retry>=0,<1',
        'sqlalchemy>=1,<2',
        'startup-migrations==0.0.2'
        ],
    test_suite='tests',
    tests_require=[
        # Duplicated from requirements.txt.
        'coverage>=4,<5',
        'coveralls>=1,<2',
        'mockito>=0,<1',
    ],
    include_package_data=True,
    zip_safe=False
)
