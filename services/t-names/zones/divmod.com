from twisted.names.authority import getSerial
from twisted.names.dns import Name

subs = ['mail.']
name = 'divmod.com'

zone = [
    SOA(
        # For whom we are the authority
        name,

        # This nameserver's name
        mname = "ns1.twistedmatrix.com",

        # Mailbox of individual who handles this
        rname = "glyph.twistedmatrix.com",

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

    MX(name, 10, 'mxa.mailgun.org', ttl=5 * 60),
    MX(name, 10, 'mxb.mailgun.org', ttl=5 * 60),

    TXT(name, 'v=spf1 include:mailgun.org ~all'),
    TXT("k1._domainkey.divmod.com",
        "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBsY8EdNjMjSv5dl1ZO8r9"
        "txFo76pf9/IoDIQVGvJ+xq5XAMbJ0X9ByiKrygyxZvnoKvsFjpF4Rt0boU/F3HGJMfG3P"
        "64dhVvOaGFfFF7W83co950Uo3Vb3l2bhfgVaIHXyDYYCcn3KKPmWlSipJv2dWWt1KnDQ5"
        "3eO7nYyIol7wIDAQAB"),
    CNAME("email.divmod.com", "mailgun.org"),
]
