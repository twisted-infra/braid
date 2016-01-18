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
            url: "/#{name}?category&branch"
            data: cfg

        $stateProvider.state(state)

class Twisted extends Controller
    constructor: (@$scope, $q, @$window, $stateParams, dataService, glTopbarContextualActionsService) ->
        @buildLimit = 500
        @changeLimit = 10
        @dataAccessor =  dataService.open().closeOnDestroy(@$scope)

        @$scope.builders = @builders = @dataAccessor.getBuilders()
        @$scope.builders.queryExecutor.isFiltered = (v) ->
            return not v.masterids? or v.masterids.length > 0

        if $stateParams.branch == undefined
            _branch = 'master'
        else
            _branch = $stateParams.branch

        if $stateParams.category == undefined
            _category = 'supported'
        else
            _category = $stateParams.category

        @branch = _branch
        @category = _category

        @filteredBuilders = {}
        @filteredBuildersList = []

        @$scope.builds = @builds = @dataAccessor.getBuilds({limit: @buildLimit, order: '-complete_at'})
        @changes = changes = @dataAccessor.getChanges({limit: @changeLimit, order: '-when_timestamp', branch: _branch})
        @buildrequests = @dataAccessor.getBuildrequests({limit: @buildLimit, order: '-submitted_at'})
        @buildsets = @dataAccessor.getBuildsets({limit: @buildLimit, order: '-submitted_at'})

        doForce = ->

           dataService.control('forceschedulers', 'force-' + _category, 'force', {revision: changes[0].sourcestamp.revision, branch: changes[0].sourcestamp.branch}).then (response) ->
              console.log(response)
           , (reason) ->
              console.log(reason)

        actions = []
        actions.push
            caption: "Force build"
            action: doForce
        glTopbarContextualActionsService.setContextualActions(actions)

        @loading = true
        @builds.onChange = @changes.onChange = @buildrequests.onChange = @buildsets.onChange = @onChange

    onChange: (s) =>
        # @todo: no way to know if there are no builds, or if its not yet loaded
        if @builders.length == 0
            return
        @loading = false

        @filteredBuilders = {}
        @filteredBuildersList = []

        for builder in @builders
            if $.inArray(@category, builder.tags) != -1
                @filteredBuilders[builder.builderid] = builder
                @filteredBuildersList.push(builder)

        if @builds.length > 0 and @buildsets.length > 0
            for build in @builds
                @matchBuildWithChange(build)

        if @buildrequests.length > 0 and @buildsets.length > 0
            for request in @buildrequests
                @matchRequestsWithChange(request)

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

        builder = @filteredBuilders[build.builderid]
        if builder == undefined
            return

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

        builder = @filteredBuilders[buildrequest.builderid]
        if builder == undefined
            return

        buildset = @buildsets.get(buildrequest.buildsetid)
        if not buildset? or not buildset.sourcestamps?
            return
        for sourcestamp in buildset.sourcestamps
            for change in @changes
                change.requestsPerBuilder ?= {}
                change.requestsPerBuilder[buildrequest.builderid] ?= []
                if change.sourcestamp.revision == sourcestamp.revision
                    if buildrequest not in change.requestsPerBuilder[buildrequest.builderid]
                        change.requestsPerBuilder[buildrequest.builderid].push(buildrequest)

    ###
    # Set the content width
    ###
    setWidth: (width) ->
        @cellWidth = "50px"
        @width = "#{(@filteredBuildersList.length + 1) * 50}px"
        @widthInclusive = "#{(@filteredBuildersList.length + 1) * 50 + 250}px"
