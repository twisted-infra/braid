class ConsoleModal extends Controller
    constructor: ($scope, @$modalInstance, @selectedBuild) ->
        $scope.$on '$stateChangeStart', =>
            @close()

    close: ->
        @$modalInstance.close()
