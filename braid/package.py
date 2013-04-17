from fabric.api import sudo


def install(package):
    sudo('apt-get --yes --quiet install {}'.format(package))
