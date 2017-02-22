(function() {
    /*=> Tickets Dashboard Module*/
    var _model, _view, _controller, body, container, calcButton, formViewWatcher, viewCont,
    purchaseOrdersModule = {
        container: {},
        _attachHandlers: function() {
            calcButton.on('click', function(e){
                console.log('execute calculation');
            });
        },
        _detachHandlers: function() {
            calcButton.off('click');
        },
        _waitForFormView: function(){
            var poModule = this;
            //Update this functionality for a full view manager, with view change events
            formViewWatcher = window.setInterval(function() {
               if (viewCont.attr('data-view-type') === 'form') {
                    var buttons = viewCont.find('.oe_stat_button.btn.btn-default.oe_inline');

                    calcButton = viewCont.find('.fa.fa-calculator');
                    console.log('detaching default Handlers');
                    poModule._detachHandlers();
                    console.log('attaching Handlers');
                    poModule._attachHandlers();
                    window.clearInterval(formViewWatcher);
               }
            }, 1500);
        },
        /*Required module functions*/
        suspend: function() {
            this._detachHandlers();
        },
        init: function(model, view, controller) {
            _model = model; _view = view; _controller = controller;
            body = window.SOROCOModel.scope.viewBody;
            console.log('init from purchases module');
            viewCont = body.find('.oe_application .oe_view_manager.oe_view_manager_current');
            this._waitForFormView();
            //this._unbindDefaultHandlers();
        }
        /* End Required module functions*/
    };
    window.SOROCOModel.initModule(purchaseOrdersModule, 'th[data-id=amount_total]');
})(window);