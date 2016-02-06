class TwistedBuildersHeader extends Directive
    constructor: ->
        return {
            replace: true
            restrict: 'EA' # E: Element, A: Attribute
            scope: {
                width: '='
                cellWidth: '='
                builders: '='
            }
            templateUrl: 'twisted_view/views/twistedbuildersheader.html'
            controller: '_twistedbuildersHeaderController'
            controllerAs: 'bh'
        }

class _twistedbuildersHeader extends Controller
    constructor: ($scope) ->
        $scope.$watch 'width', (@width) =>
        $scope.$watch 'cellWidth', (@cellWidth) =>
        $scope.$watchCollection 'builders', (@builders) =>
