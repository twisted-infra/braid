"""
Default configuration settings.
"""

dornkirk = 'dornkirk.twistedmatrix.com'

ENVIRONMENTS = {
    'production': {
        'hosts': [dornkirk],
        'roledefs': {
            'nameserver': [dornkirk],
        },
        'user': 'root',
        'installPrivateData': True,
    },
}
