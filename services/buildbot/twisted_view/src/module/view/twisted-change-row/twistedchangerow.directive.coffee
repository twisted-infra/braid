class TwistedChangeRow extends Directive
    constructor: ->
        return {
            replace: false
            restrict: 'EA' # E: Element, A: Attribute
            scope: {
                width: '='
                cellWidth: '='
                change: '='
                builders: '='
            }
            templateUrl: 'twisted_view/views/twistedchangerow.html'
            controller: '_twistedchangeRowController'
            controllerAs: 'cr'
        }


class _twistedchangeRow extends Controller
    constructor: ($scope, resultsService, @$modal) ->
        angular.extend this, resultsService

        $scope.$watch 'width', (@width) =>
        $scope.$watch 'cellWidth', (@cellWidth) =>
        $scope.$watch 'change', (@change) =>
            if @change
                if angular.isString(@change.repository)
                    @createLink()
        $scope.$watch 'builders', (@builders) ->

    createLink: ->
        repository = @change.repository.replace('.git', '')
        @change.link = "#{repository}/commit/#{@change.revision}"

    selectBuild: (build) ->
        modal = @$modal.open
            templateUrl: 'twisted_view/views/modal.html'
            controller: 'consoleModalController as modal'
            windowClass: 'modal-small'
            resolve:
                selectedBuild: -> build
