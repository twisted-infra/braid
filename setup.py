from distutils.core import setup

setup(
    name='braid',
    version='0.0',
    description='Tools for adminstering twisted labs machines',
    author='Jonathan Stoppani',
    author_email='jonathan.stoppani@wsfcomp.com',
    packages=['braid', 'braid.twisted'],
    install_requires=[
        'fabric',
        'twisted >= 12.3.0',
    ],
    zip_safe=False,
)
