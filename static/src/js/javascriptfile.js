(function() {
    /*=> Tickets Dashboard Module*/
    var igniter = window.SOROCOModel, _model, _view, _controller, body, 
    calcButton, viewCont, formContainer, fullWeightInput, emptyWeightInput,
    purchaseOrdersModule = {
        _attachHandlers: function() {

            /*igniter.moduleContainer.on('viewChange', function() {
                setTimeout(function(){ 
                    if (igniter.currentView === 'form') {
                        let actionBtns = igniter.moduleContainer.find('.oe_stat_button.btn.btn-default.oe_inline:not(.oe_form_invisible)');
                        
                        console.log(actionBtns);
                        jQuery.each(actionBtns, function(index, actionBtn) {
                            let actBtn = jQuery(actionBtn);
                            if (actBtn.find('.fa.fa-calculator').length > 0) {
                                calcButton = actBtn;
                                calcButton.off('click');
                                purchaseOrdersModule._initFormElements();

                                calcButton.on('click', function(e){
                                    purchaseOrdersModule._calculateIron();
                                });
                                return;
                            }
                        });
                    }
                }, 1500);
            });*/

            igniter.moduleContainer.on('click', '.oe_button.oe_form_button_edit', function() {
                calcButton = igniter.moduleContainer.find('.oe_stat_button.btn.btn-default.oe_inline.calculatorButton');
                calcButton.off('click');
                calcButton.removeClass('disabled');
                purchaseOrdersModule._initFormElements();

                calcButton.on('click', function(){
                    purchaseOrdersModule._calculateIron();
                });
            });

            igniter.moduleContainer.on('click', '.oe_button.oe_form_button.oe_highlight, .oe_button.oe_form_button_save.oe_highlight', function() {
                calcButton.addClass('disabled');
            });
        },
        _detachHandlers: function() {
            igniter.moduleContainer.off('viewChange');
            calcButton.off('click');
        },
        _initFormElements: function() {
            formContainer = igniter.moduleContainer.find('oe_formview oe_view');
            fullWeightInput = formContainer.find('#oe-field-input-4');
            emptyWeightInput = formContainer.find('#oe-field-input-5');
            productsRows = formContainer.find('div.oe_list.oe_view.oe_list_editable table.oe_list_content tbody tr[data-id]:not(.oe_form_field_one2many_list_row_add)');
        },
        _calculateIron: function(object) {
            console.log('trigger');
        },
        /*Required module functions*/
        suspend: function() {
            purchaseOrdersModule._detachHandlers();
        },
        init: function(model, view, controller) {
            _model = model; _view = view; _controller = controller;
            body = igniter.scope.viewBody;
            purchaseOrdersModule._attachHandlers();
            //this._unbindDefaultHandlers();
        }
        /* End Required module functions*/
    };
    igniter.initModule(purchaseOrdersModule, 'th[data-id=amount_total]');
})(window);