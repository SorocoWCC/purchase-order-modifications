(function() {
    /*=> Tickets Dashboard Module*/
    var igniter = window.SOROCOModel, _model, _view, _controller, body, srcModel,
    calcButton, saveButton, viewCont, formContainer, formInputsContainer,
    fullWeightInput, fullWeightInputVal, emptyWeightInput, emptyWeightInputVal
    purchaseOrdersModule = {
        _attachHandlers: function() {
            
            igniter.moduleContainer.on('click', '.oe_button.oe_form_button_edit, .oe_form .oe_view_manager .oe_list_content tbody tr td.oe_form_field_one2many_list_row_add a', function() {
                srcModel._formElementsInit();
                console.log(calcButton);
                calcButton.removeClass('disabled');
            });

            igniter.moduleContainer.on('click', '.oe_button.oe_form_button.oe_highlight, .oe_button.oe_form_button_save.oe_highlight', function() {
                calcButton.addClass('disabled');
            });
        },
        _formElementsInit: function(){
            //body.addClass('custom-loading');
            if (calcButton === undefined && saveButton === undefined) {
                saveButton = igniter.moduleContainer.find('.oe_button.oe_form_button_save.oe_highlight');
                calcButton = igniter.moduleContainer.find('.oe_stat_button.btn.btn-default.oe_inline.calculatorButton');
                calcButton.off('click');
                calcButton.removeClass('disabled');
                purchaseOrdersModule._initFormElements();

                calcButton.on('click', function() {
                    purchaseOrdersModule._validatePurchaseOrder();
                });
            }else{
                igniter.moduleContainer.off('click.initUI');
            }        
        },
        _detachHandlers: function() {
            igniter.moduleContainer.off('viewChange');
            if (calcButton !== undefined) {
                calcButton.off('click');                
            }
        },
        _initGlobalElements: function() {
           body.append('<div class="custom-modal custom-spinner-loader"></div>');
        },
        _initFormElements: function() {
            formContainer = igniter.moduleContainer.find('.oe_formview.oe_view');
            formInputsContainer = formContainer.find('.oe_form_sheet.oe_form_sheet_width > table.oe_form_group tbody td.oe_form_group_cell:first-child table tbody');
            fullWeightInput = formInputsContainer.find('tr:nth-child(2) td:last-child input');
            emptyWeightInput = formInputsContainer.find('tr:nth-child(3) td:last-child input');
        },
        _validatePurchaseOrder: function() {
            if (fullWeightInputVal !== undefined && emptyWeightInputVal !== undefined) {
                fullWeightInputVal = fullWeightInput.val().replace(/,/g, "");
                emptyWeightInputVal = emptyWeightInput.val().replace(/,/g, "");
                if (jQuery.isNumeric(fullWeightInputVal) && fullWeightInputVal > 0) {
                    if (jQuery.isNumeric(emptyWeightInputVal) && emptyWeightInputVal > 0) {
                        fullWeightInputVal = parseFloat(fullWeightInputVal);
                        emptyWeightInputVal = parseFloat(emptyWeightInputVal);
                        if (fullWeightInputVal > emptyWeightInputVal) {
                            productsRows = formContainer.find('div.oe_list.oe_view.oe_list_editable table.oe_list_content tbody tr[data-id]:not(.oe_form_field_one2many_list_row_add)');
                            if (productsRows.length > 0) {
                                purchaseOrdersModule._calculateIron();
                            }else{
                                console.log('did\'n find any rows');
                            }
                        } else{
                            console.log('full should be greater than empty');
                        } 
                    }else{
                        console.log('emptyWeighNotValid');
                    }
                }else{
                    console.log('fullWeighNotValid');
                }                
            }else{
                console.log('Error while trying to get the car weight fields');
            }
        },
        _calculateIron: function() {
            let ironQuantityElement, hasErrors = false, foundIron = false, weightDifference = fullWeightInputVal - emptyWeightInputVal, nonIronProductsWeight = 0;

            //setTimeout(function() {
                jQuery.each(productsRows, function(index, row) {
                    row = jQuery(row);

                    let productName = row.find('td[data-field=product_id]').html(),
                    productQuantityElement = row.find('td[data-field=product_qty]'),
                    productQuanity = row.find('td[data-field=product_qty]').html();

                    if (jQuery.isNumeric(productQuanity) && productQuanity > 0) {
                        switch(productName) {
                            case '[CH] Chatarra':
                                foundIron = true;
                                ironQuantityElement = productQuantityElement;
                                break;
                            case '[MA] Mantenimiento':
                                break;
                            case '[PRE] Prestamo':
                                break;
                            case '[RE] Rebajo':
                                break;
                            default:
                                if (jQuery.isNumeric(productQuanity)) {
                                    productQuanity = parseFloat(productQuanity);
                                    nonIronProductsWeight += productQuanity;
                                }else{
                                    hasErrors = true;
                                    console.log('error on row '+productName+' Quantity');
                                }
                        }
                    }
                });

                if (foundIron && !hasErrors) {
                    let total = weightDifference - nonIronProductsWeight;
                    if (total > 0) {
                        ironQuantityElement.click();
                        setTimeout(function() {
                            let resultElement = formContainer.find('div.oe_form_container span.oe_form_field.oe_form_field_float.oe_form_required[data-fieldname=product_qty] input');
                            if(resultElement.length > 0){
                                let e = jQuery.Event("keypress");
                                resultElement.val(total);
                                resultElement.change();
                                saveButton.click();
                                calcButton.addClass('disabled');
                            }else{
                                console.log('Something went wrong...');
                            }                            
                        }, 1000);

                        ironQuantityElement.html(total+'.000');
                    }else{
                        console.log('Calculation error, please review the qtys');
                    }
                }else{
                    console.log('Unable to find Iron');
                }
            //}, 2000);
        },
        /*Required module functions*/
        suspend: function() {
            purchaseOrdersModule._detachHandlers();
        },
        init: function(model, view, controller) {
            srcModel = this;
            _model = model; _view = view; _controller = controller;
            body = igniter.scope.viewBody;
            purchaseOrdersModule._initGlobalElements();
            purchaseOrdersModule._attachHandlers();
        }
        /* End Required module functions*/
    };
    igniter.initModule(purchaseOrdersModule, 'th[data-id=amount_total]');
})(window);