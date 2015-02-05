"""
Default configuration settings.
"""

dornkirk = 'dornkirk.twistedmatrix.com'

vagrant_address = '172.16.255.140'

ENVIRONMENTS = {
    'production': {
        'hosts': [dornkirk],
        'roledefs': {
            'nameserver': [dornkirk],
        },
        'user': 'root',
        'installPrivateData': True,
    },
    'vagrant': {
        'hosts': [vagrant_address],
        'roledefs': {
            'nameserver': [vagrant_address],
        },
        'user': 'vagrant',
        'installPrivateData': False,
    }
}
