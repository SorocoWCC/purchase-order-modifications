(function() {
    /*=> Tickets Dashboard Module*/
    var _model, _view, _controller, body, container,
    purchaseOrdersModule = {
        _attachHandlers: function(){
            /*jQuery(document).on('click', function(e){

            });*/
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
            console.log('init from purchases module');
            //this._attachHandlers();
        }
        /* End Required module functions*/
    };
    window.SOROCOModel.initModule(purchaseOrdersModule, 'th[data-id=amount_total]');
})(window);