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
    version='0.0.26',
    description='The identity service for Ocelot, as a Python package.',
    long_description=readme(),
    keywords='ocelot identity service rest api',
    url='http://github.com/ocelot/identity',
    author='Horia Coman',
    author_email='horia141@gmail.com',
    license='All right reserved',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=[
        # Duplicated from requirements.txt.
        'auth0-python>=2,<3',
        'clock==0.0.3',
        'falcon>=1,<2',
        'gunicorn>=19,<20',
        'jsonschema>=2,<3',
        'psycopg2>=2,<3',
        'pytz==2016.4',
        'sqlalchemy>=1,<2',
        'yoyo-migrations>=5,<6'
        ],
    test_suite='tests',
    tests_require=[],
    include_package_data=True,
    zip_safe=False
)
