"""
Default configuration settings.
"""

dornkirk = 'dornkirk.twistedmatrix.com'
buildbot = 'buildbot.twistedmatrix.com'
twisted_vm = 'twisted-vm.centralus.cloudapp.azure.com'

vagrant_address = '172.16.255.140'
staging_address = '162.242.246.197'

# For available options see http://docs.fabfile.org/en/latest/usage/env.html
ENVIRONMENTS = {
    'production': {
        'hosts': [twisted_vm],
        'roledefs': {
            'nameserver': [twisted_vm],
            'buildbot': [twisted_vm],
        },
        'user': 'root',
        'installPrivateData': True,
    },
    'dornkirk': {
        'hosts': [dornkirk],
        'roledefs': {
            'nameserver': [dornkirk],
            'buildbot': [dornkirk],
        },
        'user': 'root',
        'installPrivateData': True,
    },
    'staging': {
        'hosts': [staging_address],
        'roledefs': {
            'nameserver': [staging_address],
        },
        'user': 'root',
        'key_filename': (
            '.vagrant/machines/dornkirk-staging/virtualbox/private_key'),
        'installPrivateData': False,
    },
    'vagrant': {
        'hosts': [vagrant_address],
        'roledefs': {
            'nameserver': [vagrant_address],
            'buildbot': [vagrant_address],
        },
        'user': 'root',
        'installPrivateData': False,
    }
}
