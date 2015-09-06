
import urlparse
import md5, sha

from twisted.web import client, http
from twisted.internet import reactor


class Token(str):
    __slots__=[]
    tokens = {}
    def __new__(self, char):
        token = Token.tokens.get(char)
        if token is None:
            Token.tokens[char] = token = str.__new__(self, char)
        return token

    def __repr__(self):
        return "Token(%s)" % str.__repr__(self)


http_tokens = " \t\"()<>@,;:\\/[]?={}"
http_ctls = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f"


def tokenize(header, foldCase=True):
    """Tokenize a string according to normal HTTP header parsing rules.

    In particular:
     - Whitespace is irrelevant and eaten next to special separator tokens.
       Its existance (but not amount) is important between character strings.
     - Quoted string support including embedded backslashes.
     - Case is insignificant (and thus lowercased), except in quoted strings.
        (unless foldCase=False)
     - Multiple headers are concatenated with ','

    NOTE: not all headers can be parsed with this function.

    Takes a raw header value (list of strings), and
    Returns a generator of strings and Token class instances.
    """
    tokens=http_tokens
    ctls=http_ctls

    string = ",".join(header)
    list = []
    start = 0
    cur = 0
    quoted = False
    qpair = False
    inSpaces = -1
    qstring = None

    for x in string:
        if quoted:
            if qpair:
                qpair = False
                qstring = qstring+string[start:cur-1]+x
                start = cur+1
            elif x == '\\':
                qpair = True
            elif x == '"':
                quoted = False
                yield qstring+string[start:cur]
                qstring=None
                start = cur+1
        elif x in tokens:
            if start != cur:
                if foldCase:
                    yield string[start:cur].lower()
                else:
                    yield string[start:cur]

            start = cur+1
            if x == '"':
                quoted = True
                qstring = ""
                inSpaces = False
            elif x in " \t":
                if inSpaces is False:
                    inSpaces = True
            else:
                inSpaces = -1
                yield Token(x)
        elif x in ctls:
            raise ValueError("Invalid control character: %d in header" % ord(x))
        else:
            if inSpaces is True:
                yield Token(' ')
                inSpaces = False

            inSpaces = False
        cur = cur+1

    if qpair:
        raise ValueError, "Missing character after '\\'"
    if quoted:
        raise ValueError, "Missing end quote"

    if start != cur:
        if foldCase:
            yield string[start:cur].lower()
        else:
            yield string[start:cur]


def parseWWWAuthenticate(tokenized):
    headers = []

    tokenList = list(tokenized)

    while tokenList:
        scheme = tokenList.pop(0)
        challenge = {}
        last = None
        kvChallenge = False

        while tokenList:
            token = tokenList.pop(0)
            if token == Token('='):
                kvChallenge = True
                challenge[last] = tokenList.pop(0)
                last = None

            elif token == Token(','):
                if kvChallenge:
                    if len(tokenList) > 1 and tokenList[1] != Token('='):
                        break

                else:
                    break

            else:
                last = token

        if last and scheme and not challenge and not kvChallenge:
            challenge = last
            last = None

        headers.append((scheme, challenge))

    if last and last not in (Token('='), Token(',')):
        if headers[-1] == (scheme, challenge):
            scheme = last
            challenge = {}
            headers.append((scheme, challenge))

    return headers


def parse(url, defaultPort=None):
    """
    Split the given URL into the scheme, host, port, and path.

    @type url: C{str}
    @param url: An URL to parse.

    @type defaultPort: C{int} or C{None}
    @param defaultPort: An alternate value to use as the port if the URL does
    not include one.

    @return: A four-tuple of the scheme, host, port, and path of the URL.  All
    of these are C{str} instances except for port, which is an C{int}.
    """
    url = url.strip()
    parsed = urlparse.urlparse(url)
    scheme = parsed[0]
    path = urlparse.urlunparse(('','')+parsed[2:])
    if defaultPort is None:
        if scheme == 'https':
            defaultPort = 443
        else:
            defaultPort = 80
    host, port = parsed[1], defaultPort
    if ':' in host:
        host, port = host.split(':')
        port = int(port)
    if path == "":
        path = "/"
    return scheme, host, port, path


def makeGetterFactory(url, factoryFactory, contextFactory=None,
                      *args, **kwargs):
    """
    Create and connect an HTTP page getting factory.

    Any additional positional or keyword arguments are used when calling
    C{factoryFactory}.

    @param factoryFactory: Factory factory that is called with C{url}, C{args}
        and C{kwargs} to produce the getter

    @param contextFactory: Context factory to use when creating a secure
        connection, defaulting to C{None}

    @return: The factory created by C{factoryFactory}
    """
    scheme, host, port, path = parse(url)
    factory = factoryFactory(url, *args, **kwargs)
    if scheme == 'https':
        from twisted.internet import ssl
        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory()
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory


def getPage(url, contextFactory=None, *args, **kwargs):
    """
    Download a web page as a string.

    Download a page. Return a deferred, which will callback with a
    page (as a string) or errback with a description of the error.

    See HTTPClientFactory to see what extra args can be passed.
    """
    return makeGetterFactory(
        url,
        client.HTTPClientFactory,
        contextFactory=contextFactory,
        *args, **kwargs)

algorithms = {
    'md5': md5.new,

    # md5-sess is more complicated than just another algorithm.  It requires
    # H(A1) state to be remembered from the first WWW-Authenticate challenge
    # issued and re-used to process any Authorization header in response to
    # that WWW-Authenticate challenge.  It is *not* correct to simply
    # recalculate H(A1) each time an Authorization header is received.  Read
    # RFC 2617, section 3.2.2.2 and do not try to make DigestCredentialFactory
    # support this unless you completely understand it. -exarkun
    'md5-sess': md5.new,

    'sha': sha.new,
}

# DigestCalcHA1
def calcHA1(pszAlg, pszUserName, pszRealm, pszPassword, pszNonce, pszCNonce,
            preHA1=None):
    """
    Compute H(A1) from RFC 2617.

    @param pszAlg: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param pszUserName: The username
    @param pszRealm: The realm
    @param pszPassword: The password
    @param pszNonce: The nonce
    @param pszCNonce: The cnonce

    @param preHA1: If available this is a str containing a previously
       calculated H(A1) as a hex string.  If this is given then the values for
       pszUserName, pszRealm, and pszPassword must be C{None} and are ignored.
    """

    if (preHA1 and (pszUserName or pszRealm or pszPassword)):
        raise TypeError(("preHA1 is incompatible with the pszUserName, "
                         "pszRealm, and pszPassword arguments"))

    if preHA1 is None:
        # We need to calculate the HA1 from the username:realm:password
        m = algorithms[pszAlg]()
        m.update(pszUserName)
        m.update(":")
        m.update(pszRealm)
        m.update(":")
        m.update(pszPassword)
        HA1 = m.digest()
    else:
        # We were given a username:realm:password
        HA1 = preHA1.decode('hex')

    if pszAlg == "md5-sess":
        m = algorithms[pszAlg]()
        m.update(HA1)
        m.update(":")
        m.update(pszNonce)
        m.update(":")
        m.update(pszCNonce)
        HA1 = m.digest()

    return HA1.encode('hex')


def calcHA2(algo, pszMethod, pszDigestUri, pszQop, pszHEntity):
    """
    Compute H(A2) from RFC 2617.

    @param pszAlg: The name of the algorithm to use to calculate the digest.
        Currently supported are md5, md5-sess, and sha.
    @param pszMethod: The request method.
    @param pszDigestUri: The request URI.
    @param pszQop: The Quality-of-Protection value.
    @param pszHEntity: The hash of the entity body or C{None} if C{pszQop} is
        not C{'auth-int'}.
    @return: The hash of the A2 value for the calculation of the response
        digest.
    """
    m = algorithms[algo]()
    m.update(pszMethod)
    m.update(":")
    m.update(pszDigestUri)
    if pszQop == "auth-int":
        m.update(":")
        m.update(pszHEntity)
    return m.digest().encode('hex')


def calcResponse(HA1, HA2, algo, pszNonce, pszNonceCount, pszCNonce, pszQop):
    """
    Compute the digest for the given parameters.

    @param HA1: The H(A1) value, as computed by L{calcHA1}.
    @param HA2: The H(A2) value, as computed by L{calcHA2}.
    @param pszNonce: The challenge nonce.
    @param pszNonceCount: The (client) nonce count value for this response.
    @param pszCNonce: The client nonce.
    @param pszQop: The Quality-of-Protection value.
    """
    m = algorithms[algo]()
    m.update(HA1)
    m.update(":")
    m.update(pszNonce)
    m.update(":")
    if pszNonceCount and pszCNonce:
        m.update(pszNonceCount)
        m.update(":")
        m.update(pszCNonce)
        m.update(":")
        m.update(pszQop)
        m.update(":")
    m.update(HA2)
    respHash = m.digest().encode('hex')
    return respHash
