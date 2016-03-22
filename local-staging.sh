#!/bin/sh

set -e
vagrant up
fab config.vagrant base.bootstrap
fab config.vagrant t-web.install
fab config.vagrant t-web.makeTestTLSKeys
fab config.vagrant t-web.installTLSKeys
fab config.vagrant trac.install
fab config.vagrant trac.installTestData
fab config.vagrant amptrac.install
fab config.vagrant kenaan.install
fab config.vagrant t-web.start
fab config.vagrant trac.start
fab config.vagrant amptrac.start
fab config.vagrant kenaan.start

