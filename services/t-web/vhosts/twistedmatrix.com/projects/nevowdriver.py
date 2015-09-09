import os
from nevow import rend, loaders, tags as T
import email.Parser, glob

licences = {'MIT': 'http://www.opensource.org/licenses/mit-license.php'}

def _obscured(name, email):
    L = []
    write = "document.write('\\x%x');"
    s = '<a href="%s" title="%s">%s</a>' % (email, name, name)
    for ch in s:
        L.append(write % (ord(ch),))
    return "<script language='javascript'>%s</script>" % (''.join(L),)

class ProjectPage(rend.Page):

    addSlash = True

    docFactory = loaders.xmlfile('project-template.tpl')

    def __init__(self, projectData):
        '''
        projectData is a dict with these keys and values:
            name: short name for project, eg "Twisted Mail"
            description: sentence long description of project
            longdesc: paragraph long description of project
            url: url of project home page
            licence: (name of licence, licence url) tuple
            releases: a list of (version_number, release_date, md5sum,
                download_link, release_notes_link) tuples
            maintainer: a list of (maintainer_name, maintainer_url) tuples
            help: a list of places to get help in (description, url) tuples
            bugs: url of bugtracker
        '''
        rend.Page.__init__(self)
        self.projectData = projectData

    def render_listoflinks(self, ctx, data):
        links = []
        for description, link in data:
            links.append(T.li[
                T.a(title = description, href = link)[description]
            ])
        return ctx.tag[links]

    def render_bugs(self, ctx, data):
        return ctx.tag(href = data)["the bug tracker"]

    def data_project(self, name):
        def _(ctx, data):
            return self.projectData[name]
        return _

    def data_longdesc(self, ctx, data):
        return self.projectData.get_payload()

    def data_latestversion(self, ctx, data):
        return [x.split('|') for x in self.projectData.get_all('releases')]

    def render_maintainers(self, ctx, data):
        for maint in self.projectData.get_all('maintainers'):
            parts = maint.split('|')
            link = _obscured(parts[0], parts[1])
            ctx.tag[T.li[T.xml(link)]]
        return ctx.tag

    def data_help(self, ctx, data):
        return [x.split('|') for x in self.projectData.get_all('help')]
        
    def render_downloadtable(self, ctx, data):
        rows = []
        for packageName, version, release, md5, download, release_notes in \
                data:
            download_link = T.a(href = download)["Download %s" % version]
            release_notes_link = T.a(href = release_notes)["%s release notes" % version]
            tr = T.tr[
                T.td[packageName],
                T.td[version],
                T.td[release],
                T.td[md5],
                T.td[download_link],
                ]
            if release_notes:
                tr[T.td[release_notes_link]]
            rows.append(tr)
        return ctx.tag[
            T.thead[T.tr[
                T.td["Package"],
                T.td["Version number"],
                T.td["Release date"],
                T.td["MD5 sum"],
                T.td["Download link"],
                T.td["Release Notes"]
                ]],
            T.body[rows]
            ]

    def render_metadesc(self, ctx, data):
        return ctx.tag(name = 'description', content = data)
    
    def render_licencelink(self, ctx, data):
        url = licences[data]
        return ctx.tag(title = "%s licence" % data, href=url)[data]

    def render_header(self, ctx, data):
        if 'header' in self.projectData:
            return T.img(style="float: right", src=self.projectData['header'])
        return ctx.tag

DATA_DIR = 'data/'

def loadProject(filename):
    try:
        f = file(filename, 'r')
        m = email.Parser.Parser().parse(f)
        return m
    # ignore project on OS/IO errors
    except (OSError, IOError):
        pass

def loadProjects(directory=DATA_DIR):
    """
    Load info and create projectData dictionaries from the data directory
    """
    projects = {}
    for filename in glob.glob('%s/*.proj' % directory):
        projects[os.path.splitext(os.path.basename(filename))[0]] = (
            loadProject(filename))
    return projects

def orderDict(orderList, d):
    """
    Returns a list of the values of d, ordered by the position of
    their key in orderList, or if they're not in orderList, by Python
    sort order (after the ones that are in the orderList).
    """
    source = d.copy()
    result = []
    for key in orderList:
        result.append(source.pop(key))
    leftOver = source.items()
    leftOver.sort()
    result.extend([x[1] for x in leftOver])
    return result

class ProjectIndex(rend.Page):
    docFactory=loaders.htmlfile("index.html")

    addSlash = True

    def __init__(self):
        rend.Page.__init__(self)
        self.projects = loadProjects()
        for projectData in self.projects.values():
            self.putChild(projectData['url'], ProjectPage(projectData))

    def data_pyprojects(self, ctx, data):
        # We want 'important' projects to go first
        projects = orderDict(['core', 'conch', 'web', 'web2', 'mail', 'names', 'news', 'words', 'lore'],
                             self.projects)
        return [(data['name'], data['description'], '%s/' % data['url'])
                for data in projects]

    def data_otherprojects(self, ctx, data):
        return [
            ("Twisted Emacs", "Emacs integration support for Twisted developers", None),
            ("EIO", "High-level java.nio wrapper networking framework", "http://java.twistedmatrix.com/eio/"),
            ("PB for Java", "Perspective Broker remote object protocol implementation in Java",
             "http://itamarst.org/software/twistedjava/"),
            ]

    def render_title(self, ctx, data):
        title, desc, url = data
        if url:
            return T.a(href=url)[title]
        else:
            return title

    def render_description(self, ctx, data):
        return data[1]

def tac():
    global application
    from twisted.application import service, internet
    from nevow import appserver

    application = service.Application("simple")
    internet.TCPServer(
        8080,
        appserver.NevowSite(
            ProjectIndex()
        )
    ).setServiceParent(application)


def generate():
    import os, sys, glob
    from twisted.python import log
    log.startLogging(sys.stdout)
    from twisted.internet import reactor, defer

    index = ProjectIndex()
    projs = [os.path.splitext(os.path.basename(fn))[0]
             for fn in glob.glob('data/*.proj')]

    def gotString(string, project):
        if not os.path.exists(project):
            os.mkdir(project)
        f = open(os.path.join(project, 'index'), 'w')
        f.write(string)
        f.close()

    def gotIndexString(string):
        f = open('index', 'w')
        f.write(string)
        f.close()

    dlist = []
    print "processing... index"
    dlist.append(
        index.renderString().addCallback(gotIndexString))
    
    for proj in projs:
        print "processing...", proj
        page = index.children[proj]
        dlist.append(
            page.renderString().addCallback(gotString, proj))

    d = defer.gatherResults(dlist).addErrback(lambda f: f.value[0])
    d.pause()
    d.addErrback(log.err)
    d.addBoth(lambda rf: reactor.stop())
    reactor.callWhenRunning(d.unpause)
    reactor.run()



if __name__ == '__main__':
    generate()
else:
    tac()
