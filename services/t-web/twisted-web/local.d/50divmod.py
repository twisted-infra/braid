from twisted.web import static

dmcr = static.File('/home/amir/sites/divmod.com')
dmor = static.File('/home/amir/sites/divmod.org')

root.addHost('divmod.org', dmor)
root.addHost('www.divmod.org', dmor)

root.addHost('divmod.com', dmcr)
root.addHost('www.divmod.com', dmcr)

