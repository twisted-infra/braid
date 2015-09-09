# Hostname where persistent bot process is listening
BOT_HOST = 'twistedmatrix.com'

# Port number of same
BOT_PORT = 15243

# Maximum number of characters to put into a single IRC message
LINE_LENGTH = 400

# Delay, in seconds, between IRC messages
LINE_RATE = 1.0

# Three-tuples of (repository path, filename expression, channel) defining
# the rules for announcing commit messages.
COMMIT_RULES = [
    ('/svn/Twisted', '.*', ['#twisted', '#twisted-dev']),
    ('/svn/Twisted', '.*/(twisted|doc)/web2?/.*', ['#twisted.web', '#twisted-dev']),
    ('/svn/WebSite', '.*', ['#twisted', '#twisted-dev']),
    ('/svn', 'pypy/.*', ['#pypy'])]

# Two-tuples of (tracker URL, channel) defining the rules for announcing
# ticket changes.
TICKET_RULES = [
    ('http://twistedmatrix.com/trac/', ['#twisted', '#twisted-dev']),
    ]

# The channel to which to send alerts.
ALERT_CHANNEL = '#twisted-admin'

# The directory in which log files will be written.  Most users can
# write to their own home directory, but some can't - eg www-data.
# So, give each user a directory in /tmp.  They can't use /tmp itself
# because users won't be able to open log files written by other
# users.
import os, pwd, tempfile
LOG_ROOT = os.path.join(
    tempfile.gettempdir(),
    'kenaan-logs-' + pwd.getpwuid(os.getuid()).pw_name)
if not os.path.isdir(LOG_ROOT):
    os.makedirs(LOG_ROOT)
