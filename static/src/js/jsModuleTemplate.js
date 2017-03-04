(function() {
    /*=> Tickets Dashboard Module*/
    var _model, _view, _controller, body, container, srcModel
    customModule = {
        _attachHandlers: function() {

        },
        _detachHandlers: function() {

        },
        /*Required module functions*/
        suspend: function() {
            this._detachHandlers();
        },
        init: function(model, view, controller) {
            srcModel = this;
            _model = model; _view = view; _controller = controller;
            body = window.SOROCOModel.scope.viewBody;
            container = window.SOROCOModel.scope.customModuleSelector;

            this._attachHandlers();
        }
        /* End Required module functions*/
    };
    window.SOROCOModel.initModule(customModule, 'body');
})(window);