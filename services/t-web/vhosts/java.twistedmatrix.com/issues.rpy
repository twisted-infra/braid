cache()

from twisted.web import distrib

resource = distrib.ResourceSubscription('unix', '/home/roundup/.twistd-web-pb')
