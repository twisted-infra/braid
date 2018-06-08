from distutils.core import setup
import setuptools

setup(
    name='braid',
    version='0.0',
    description='Tools for adminstering twisted labs machines',
    author='Twisted Matrix Laboratories',
    author_email='jonathan@stoppani.name',
    packages=['braid', 'braid.twisted'],
    install_requires=[
        'fabric >= 1.6.0, < 2.0',
        'twisted >= 12.3.0',
        'requests >= 1.2.0',
    ],
    zip_safe=False,
)
