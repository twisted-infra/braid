"""
Default configuration settings.
"""

dornkirk = 'dornkirk.twistedmatrix.com'
buildbot = 'buildbot.twistedmatrix.com'

vagrant_address = '172.16.255.140'

ENVIRONMENTS = {
    'production': {
        'hosts': [dornkirk],
        'roledefs': {
            'nameserver': [dornkirk],
            'buildbot': [buildbot],
        },
        'user': 'root',
        'installPrivateData': True,
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
