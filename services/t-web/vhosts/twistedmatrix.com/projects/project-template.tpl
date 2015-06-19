<html xmlns:n="http://nevow.com/ns/nevow/0.1">
    <head>
        <title n:data="project name" n:render="string"/>
        <meta n:render="metadesc" n:data="project description"/>
        <link type="text/css" rel="stylesheet" href="/stylesheet.css"/>
        <link type="text/css" rel="stylesheet" href="/project.css"/>
    </head>
    <body>
        <div id="maincontent">
            <div id="navigation">
                <p>
                <a href="/">Twisted Matrix Labs</a> :
                <a href="/projects/">Projects</a> :
                <n:invisible n:data="project name" n:render="string"/>
                </p>
            </div>
	    <n:invisible n:render="header" />
            <h1 n:data="project name" n:render="string"/>
            <h2>
                About
                <n:invisible n:data="project name" n:render="string"/>
            </h2>
            <p n:data="longdesc" n:render="xml"/>
            <p>
                <n:invisible n:data="project name" n:render="string"/>
                is available under the
                <a n:data="project licence" n:render="licencelink"/>
                Free Software licence.
            </p>
            <h2>
                Get
                <n:invisible n:data="project name" n:render="string"/>
            </h2>
            <h3>Latest version</h3>
            <table class="download" n:data="latestversion" n:render="downloadtable"/>
<!--
            <h3>Older versions</h3>
            <table class="download" n:data="olderversions" n:render="downloadtable"/>
-->
            <h2>Documentation</h2>
            <a href="documentation/">Documentation</a> is available on the website.
            <h2>Contact</h2>    
            <h3>Community</h3>
            <p>
                Community support for
                <n:invisible n:data="project name" n:render="string"/>
                may be available from the following sources:
            </p>
            <ul n:data="help" n:render="listoflinks"/>
            <h3>Bugs</h3>
            <p>
                Please report bugs and submit patches or feature requests for
                <n:invisible n:data="project name" n:render="string"/>
                to
                <a n:data="project bugs" n:render="bugs"/>.
            </p>
            <h3>Maintainers</h3>
            <ul n:render="maintainers"/>
        </div>
    </body>
</html>
