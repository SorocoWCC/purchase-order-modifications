(function() {
    /*=> Tickets Dashboard Module*/
    var _model, _view, _controller, body, container,
    customModule = {
        _attachHandlers: function(){

        },
        _detachHandlers: function(){

        },
        /*Required module functions*/
        suspend: function(){
            this._detachHandlers();
        },
        init: function(model, view, controller){
            _model = model; _view = view; _controller = controller;
            body = window.SOROCOModel.scope.viewBody;
            container = window.SOROCOModel.scope.viewContainer;

            this._attachHandlers();
        }
        /* End Required module functions*/
    };
    window.SOROCOModel.initModule(customModule, 'body');
})(window);