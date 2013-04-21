"""
Default configuration settings.
"""

ENVIRONMENTS = {
    'production': {
        'hosts': ['10.2.1.118'] or
        ['dornkirk.twistedmatrix.com'],
        'user': 'root'
    },
}
