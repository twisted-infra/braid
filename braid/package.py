from fabric.api import with_settings, run


@with_settings(user='root')
def install(package):
    run('apt-get --yes --quiet install {}'.format(package))
