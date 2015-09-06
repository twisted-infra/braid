from twisted.web.resource import Resource
from twisted.python.filepath import FilePath

content = FilePath(__file__).sibling('index.html').getContent()

class MaintenceResource(Resource):
    def render(self, request):
        return content

    def getChild(self, path, request):
        return self

resource = MaintenceResource()
