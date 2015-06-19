from os.path import expanduser
from twisted.web.static import File

resource = File(expanduser("~/data/documentation/"))
