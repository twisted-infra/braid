#find */documentation/* -type f |grep -v svn | xargs rm
#python <thisprogram>.py ~/EXPORTWHATHADPROCESSDOCSRUN
#svn st | grep '!' | xargs -n1 svn rm
#svn st | grep '?' | xargs -n1 svn add
#svn commit

import glob
from twisted.python import filepath as fp

import sys

for proj in fp.FilePath(sys.argv[1]).child('doc').children():
    dest = fp.FilePath(proj.basename()).child('documentation')
    if dest.exists():
        proj.copyTo(dest)
