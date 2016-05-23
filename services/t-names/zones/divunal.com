
from twisted.names.authority import getSerial

name = 'divunal.com'

from hosts import dornkirk, nameservers, addSubdomains

subs = {
    dornkirk: [''],
}

zone = [
    SOA(
        # For whom we are the authority
        name,

        # This nameserver's name
        mname = "ns1.twistedmatrix.com",

        # Mailbox of individual who handles this
        rname = "radix.twistedmatrix.com",

        # Unique serial identifying this SOA data
        # <4-year> <2-month> <2-day> <2-counter>
        serial = getSerial(),

        # Time interval before zone should be refreshed
        refresh = "15M",

        # Interval before failed refresh should be retried
        retry = "1H",

        # Upper limit on time interval before expiry
        expire = "1H",

        # Minimum TTL
        minimum = "1H"
    ),

    MX(name, 10, 'mail.twistedmatrix.com'),
] + nameservers(name)

addSubdomains(name, zone, subs)
