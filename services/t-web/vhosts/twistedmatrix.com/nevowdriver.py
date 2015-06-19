from nevow import rend, tags as T, loaders

import urllib2, os

def cleanup(line):
    parts = line[2:].split()
    email = parts[-1]
    email = email.replace('@', ' (at) ').replace('<', '').replace('>', '')
    name = ' '.join(parts[:-1])
    person = '%s : %s' % (name, email)
    return person


def extractVersion(filename):
    #/foo/Twisted-1.2.1.tar.gz -> 1.2.1
    return os.path.basename(filename[:-len('.tar.gz')]).split('-')[-1]


class Page(rend.Page):
    stableversion = unstableversion = None
    unstabletype = 'Not unstable!'

    def __init__(self, *args, **kwargs):
        rend.Page.__init__(self, *args, **kwargs)
        self.figureVersions()
    
    def render_credits(self, ctx, data):
        data = urllib2.urlopen('http://svn.twistedmatrix.com/cvs/*checkout*/trunk/twisted/topfiles/CREDITS?root=Twisted').read()

        people = []
        i = iter(data.splitlines())
        for line in i:
            if line.startswith('- '):
                person = cleanup(line)
                people.append((person, i.next()))
            if line.startswith('Extras'):
                break

        extras = []
        for line in i:
            if line.startswith('- '):
                extras.append(cleanup(line))
        
        ctx.tag[ T.ul[ [T.li[x[0], T.br, x[1]] for x in people] ] ]

        ctx.tag[T.h2["Extras"]]

        ctx.tag[ T.ul[ [T.li[x] for x in extras] ] ]

        return ctx.tag

    def _writeVersions(self):
        f = open('products/twisted-versions.txt', 'w')
        f.write('STABLE = %r\n' % self.stableversion)
        f.write('UNSTABLE = %r\n' % self.unstableversion)
        f.close()

    def figureVersions(self):
        import glob
        newfiles = glob.glob('/twisted/Releases/Twisted-*.tar.gz')
        newfiles.sort()
        if not newfiles:
            self.stableversion = "STABLE-1.2.3"
            self.unstableversion = "UNSTABLE-1.2.4alpha1"
            self.unstabletype = 'alpha'
            self._writeVersions()
            return
        latest = extractVersion(newfiles[-1])

        alphai = latest.find('alpha')
        rci = latest.find('rc')
        if alphai == -1 and rci == -1:
            # The latest is a stable and there is no relevant unstable
            # version.
            self.stableversion = latest
            self._writeVersions()
            return

        # The latest is an unstable. Remember it and see what the
        # latest stable is.
        self.unstableversion = latest
        # ha ha I love obscure insanely terse code
        self.unstabletype = ['alpha', 'rc'][rci != -1]

        oldfiles = glob.glob('/twisted/Releases/old/Twisted-*.tar.gz')
        oldfiles.sort()
        latest = extractVersion(oldfiles.pop(-1))

        while latest.find('rc') != -1 or latest.find('alpha') != -1:
            latest = extractVersion(oldfiles.pop(-1))

        self.stableversion = latest
        self._writeVersions()


    def render_stableversion(self, ctx, data):
        return ctx.tag.clear()[self.stableversion]

    def render_maybeunstable(self, ctx, data):
        if self.unstableversion:
            thing = ctx.tag
        thing = ""
        return thing

    def render_unstableversion(self, ctx, data):
        if self.unstableversion:
            thing = self.unstableversion
        else:
            thing = "(No unstable)"
        return ctx.tag.clear()[thing]

    def render_unstabletype(self, ctx, data):
        # assume unstable is latest
        ret = self.unstabletype
        if ret == 'rc':
            ret = 'release candidate'
        return ctx.tag.clear()[ret.capitalize()]

    def render_nextversion(self, ctx, data):
        # assume unstable is latest
        if not self.unstableversion:
            return "No next version! Not unstable."
        return ctx.tag.clear()[
            self.unstableversion[
                : self.unstableversion.find(self.unstabletype)
                ]
            ]

tmpage = None
def TMPage(docFactory):
    """
    Hack for having a persistent Page instance.
    """
    global tmpage
    if tmpage:
        tmpage.docFactory = docFactory
        return tmpage
    else:
        tmpage = Page(docFactory=docFactory)
        return tmpage


if __name__ == '__main__':
    tmpage = TMPage(
        docFactory=loaders.htmlstr(
        '<html><body> <span nevow:render="stableversion"/></body></html>'))
    from twisted.trial.util import wait
    print wait(tmpage.renderString())
