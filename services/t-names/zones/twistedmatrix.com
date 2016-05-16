
from twisted.names.authority import getSerial

name = 'twistedmatrix.com'
lists = 'lists.' + name

from hosts import cube, dornkirk, jeb, wolfwood, xpdev, planet, nameservers, addSubdomains, googleHosting, buildbot

subs = {
    cube: ['cube.'],
    wolfwood: ['cvs.', 'wolfwood.', 'svn.', 'git.', 'code.'],
    dornkirk: ['dornkirk.', '', 'projects.', 'ftp.', 'www.', 'speed.',
               'reality.', 'irc.', 'saph.',
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
        rname = "radix.twistedmatrix.com",

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

    MX(name, 5, 'mail.' + name, ttl='1H'),

    CNAME('planet.twistedmatrix.com', planet, ttl='1D'),
    CNAME('radix.twistedmatrix.com', 'wordeology.com', ttl='1D'),
    CNAME('washort.twistedmatrix.com', googleHosting, ttl='1D'),
    CNAME('glyph.twistedmatrix.com', 'writing.glyph.im', ttl='1D'),
    CNAME('secret.glyph.twistedmatrix.com', googleHosting, ttl='1D'),
    CNAME('labs.twistedmatrix.com', googleHosting, ttl='1D'),

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
