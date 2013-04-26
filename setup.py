from distutils.core import setup

setup(
    name='braid',
    version='0.0',
    description='Tools for adminstering twisted labs machines',
    author='Twisted Matrix Laboratories',
    author_email='jonathan@stoppani.name',
    packages=['braid', 'braid.twisted'],
    install_requires=[
        'fabric',
        'twisted >= 12.3.0',
        'requests',
    ],
    zip_safe=False,
)
