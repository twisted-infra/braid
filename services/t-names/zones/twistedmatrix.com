
from twisted.names.authority import getSerial

name = 'twistedmatrix.com'
lists = 'lists.' + name

from hosts import cube, dornkirk, jeb, wolfwood, xpdev, planet, nameservers, addSubdomains, googleHosting, buildbot

subs = {
    cube: ['cube.'],
    wolfwood: ['cvs.', 'wolfwood.', 'svn.', 'git.', 'code.'],
    dornkirk: ['dornkirk.', '', 'projects.', 'ftp.', 'www.', 'speed.',
               'reality.', 'irc.',
               'java.', 'smtp.', 'mail.'],
    xpdev: ['xpdev.'],
    jeb: ['staging.'],
    buildbot: ['buildbot.'],
}

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
        refresh = "5M",

        # Interval before failed refresh should be retried
        retry = "15M",

        # Upper limit on time interval before expiry
        expire = "1H",

        # Minimum TTL
        minimum = "5M",

        ttl="5M",
    ),

    # mailman.* points at mailman instance, which is a smarthost; although
    # dornkirk still has forwarding rules scattered around, they should no
    # longer be necessary.
    MX("mailman." + name, 5, 'dornkirk.' + name, ttl='1H'),
    CNAME("email." + name, "mailgun.org", ttl="1H"),
    MX(name, 10, 'mxa.mailgun.org', ttl=5 * 60),
    MX(name, 10, 'mxb.mailgun.org', ttl=5 * 60),
    TXT(name, 'v=spf1 include:mailgun.org ~all'),
    TXT("smtp._domainkey.twistedmatrix.com",
        "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDpLlSOhHfqnfRUYKDlx/rw"
        "NcgUyZf8/XurHCpfCQD2ByWNwpOLkS4KWpc7FQlfuu8sCyDbWoc0foZPqhiyUKhDGvrOA"
        "I+e5zuiR6X/Bg9ZXr0zAsxX3UpxV1yBrur/SOS+uw5YslR5pOqI20OzSio0CUXcEXTbD1"
        "29GE4xiMbXfwIDAQAB"),

    CNAME('planet.twistedmatrix.com', planet, ttl='1D'),
    CNAME('docs.twistedmatrix.com', 'readthedocs.io', ttl='1D'),
    CNAME('glyph.twistedmatrix.com', 'writing.glyph.im', ttl='1D'),
    CNAME('secret.glyph.twistedmatrix.com', googleHosting, ttl='1D'),
    CNAME('labs.twistedmatrix.com', googleHosting, ttl='1D'),

    A(lists, '148.62.12.12'),
    AAAA(lists, '2001:4800:7823:103:be76:4eff:fe04:3c4d'),

    TXT(lists, 'v=spf1 include:mailgun.org ~all'),
    TXT('k1._domainkey.lists.twistedmatrix.com',
        "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDogNXfdPbfqy8IEeB4wClK"
        "YIQyLy/BAn8SMDj7byepgpQGIHkviT4uJ61u1oTEEF5Wow/20Q/G1FlKk8sIANmJU7v/R"
        "8r8ZMw6Rfs+/CKjxCtG6l2f+6cVsVWE8VmEA6DeUfjNt1ToMUYSyo0R0dRMhEFRucVN0r"
        "9aV51ztuq6zQIDAQAB"),
    CNAME('email.' + lists, 'mailgun.org'),

    MX(lists, 10, 'mxa.mailgun.org', ttl=5 * 60),
    MX(lists, 10, 'mxb.mailgun.org', ttl=5 * 60),

] + nameservers(name)

addSubdomains(name, zone, subs)
