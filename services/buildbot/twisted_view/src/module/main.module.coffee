# Register new module
class App extends App
    constructor: ->
        return [
            'ui.router'
            'ui.bootstrap'
            'common'
            'ngAnimate'
            'guanlecoja.ui'
            'bbData'
        ]


class State extends Config
    constructor: ($stateProvider, glMenuServiceProvider) ->

        # Name of the state
        name = 'twisted'

        # Menu configuration
        glMenuServiceProvider.addGroup
            name: name
            caption: 'Twisted View'
            icon: 'exclamation-circle'
            order: 5

        # Configuration
        cfg =
            group: name
            caption: 'Twisted View'

        # Register new state
        state =
            controller: "#{name}Controller"
            controllerAs: "c"
            templateUrl: "twisted_view/views/#{name}.html"
            name: name
            url: "/#{name}?branch&tag"
            data: cfg

        $stateProvider.state(state)

class Twisted extends Controller
    constructor: (@$scope, $q, @$window, $stateParams, dataService, glTopbarContextualActionsService) ->
        @buildLimit = 500
        @changeLimit = 10
        @dataAccessor =  dataService.open().closeOnDestroy(@$scope)
        @topbar = glTopbarContextualActionsService

        if $stateParams.branch == undefined
            @branch = 'master'
        else
            @branch = $stateParams.branch

        if $stateParams.tag == undefined
            tag = @tag = 'supported'
        else
            tag = @tag = $stateParams.tag

        @$scope.unfilteredBuilders = @unfilteredBuilders = @dataAccessor.getBuilders({tags__contains: tag})
        @$scope.unfilteredBuilders.queryExecutor.isFiltered = (v) ->
            return not v.masterids? or v.masterids.length > 0

        @$scope.builds = @builds = @dataAccessor.getBuilds({limit: @buildLimit, order: '-complete_at'})
        @changes = changes = @dataAccessor.getChanges({limit: @changeLimit, order: '-when_timestamp', branch: @branch})
        @buildrequests = @dataAccessor.getBuildrequests({limit: @buildLimit, order: '-submitted_at'})
        @buildsets = @dataAccessor.getBuildsets({limit: @buildLimit, order: '-submitted_at'})

        @doForce = ->

           dataService.control('forceschedulers', 'force-' + tag, 'force', {revision: changes[0].sourcestamp.revision, branch: changes[0].sourcestamp.branch}).then (response) ->
              console.log(response)
           , (reason) ->
              console.log(reason)

        @loading = true
        @builds.onChange = @changes.onChange = @buildrequests.onChange = @buildsets.onChange = @onChange

    onChange: (s) =>
        # No builders, no top line.
        if @unfilteredBuilders.length == 0
            return
        @loading = false

        @builders = []
        for builder in @unfilteredBuilders
            if $.inArray(@tag, builder.tags) != -1
                @builders.push(builder)

        # Wipe the requests/builds
        if @changes.length > 0
            for change in @changes
                change.buildsPerBuilder = {}
                change.requestsPerBuilder = {}

        # If there's changes and builds, we can show them
        if @changes.length > 0 and @builds.length > 0 and @buildsets.length > 0
            for build in @builds
                @matchBuildWithChange(build)

        # If there's changes and build requests, we can show them
        if @changes.length > 0 and @buildrequests.length > 0 and @buildsets.length > 0
            for request in @buildrequests
                @matchRequestsWithChange(request)

        # Only show "force build" if there's changes (since you can only force from a change)
        actions = []
        if @changes.length
            actions.push
                caption: "Force build"
                action: @doForce
        @topbar.setContextualActions(actions)

        if @changes.length
            for change in @changes
                change.maxbuilds = 1
                change.maxrequests = 1
                for k, b of change.buildsPerBuilder
                    if b.length > change.maxbuilds
                        change.maxbuilds = b.length
                for k, b of change.requestsPerBuilder
                    if b.length > change.maxrequests
                        change.maxrequests = b.length

        @setWidth(@$window.innerWidth)
        angular.element(@$window).bind 'resize', =>
            @setWidth(@$window.innerWidth)
            @$scope.$apply()

    ###
    # Match builds with a change
    ###
    matchBuildWithChange: (build) =>

        buildrequest = @buildrequests.get(build.buildrequestid)
        if not buildrequest?
            return
        buildset = @buildsets.get(buildrequest.buildsetid)
        if not buildset? or not buildset.sourcestamps?
            return
        for sourcestamp in buildset.sourcestamps
            for change in @changes
                change.buildsPerBuilder ?= {}
                change.buildsPerBuilder[build.builderid] ?= []
                if change.sourcestamp.revision == sourcestamp.revision
                    if build not in change.buildsPerBuilder[build.builderid]
                        change.buildsPerBuilder[build.builderid].push(build)

    matchRequestsWithChange: (buildrequest) =>

        buildset = @buildsets.get(buildrequest.buildsetid)
        if not buildset? or not buildset.sourcestamps?
            return
        for sourcestamp in buildset.sourcestamps
            for change in @changes
                change.requestsPerBuilder ?= {}
                change.requestsPerBuilder[buildrequest.builderid] ?= []
                if change.sourcestamp.revision == sourcestamp.revision
                    if buildrequest not in change.requestsPerBuilder[buildrequest.builderid]
                        if @builds.length > 0
                            for build in change.buildsPerBuilder[buildrequest.builderid]
                                if build.buildrequestid == buildrequest.buildrequestid
                                    return
                        change.requestsPerBuilder[buildrequest.builderid].push(buildrequest)

    ###
    # Set the content width
    ###
    setWidth: (width) ->
        @cellWidth = "50px"
        @width = "#{(@builders.length + 1) * 50}px"
        @widthInclusive = "#{(@builders.length + 1) * 50 + 250}px"
