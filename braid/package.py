from fabric.api import sudo


def install(packages):
    """
    Install a list of packages.
    """
    sudo('/usr/bin/apt-get --yes --quiet install {}'.format(" ".join(packages)))
