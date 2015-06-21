from twisted.names.authority import getSerial

from hosts import tmtl

subs = ['mail.']
name = 'divmod.com'

zone = [
    SOA(
        # For whom we are the authority
        name,

        # This nameserver's name
        mname = "ns1.twistedmatrix.com",

        # Mailbox of individual who handles this
        rname = "exarkun.twistedmatrix.com",

        # Unique serial identifying this SOA data
        # <4-year> <2-month> <2-day> <2-counter>
        serial = getSerial(),

        # Time interval before zone should be refreshed
        refresh = "1H",

        # Interval before failed refresh should be retried
        retry = "15M",

        # Upper limit on time interval before expiry
        expire = "1H",

        # Minimum TTL
        minimum = "1H",

        # Default TTL for records in this zone
        ttl="1H",
    ),

    NS(name, 'ns1.twistedmatrix.com'),
    NS(name, 'ns2.twistedmatrix.com'),

    MX(name, 100, 'mail.divmod.com', ttl=5 * 60),
]

for sub in subs:
    zone.append(A(sub + name, tmtl, ttl="1H"))
