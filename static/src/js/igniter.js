(function() {

    /*=== STARTS Global JS Handler // DO NOT TOUCH===*/
    var body, srcModel, viewWatcher, markupWatcher;
    window.SOROCOModel = {
        _modulesInstances: [], _odooM: {}, activeModuleInstance: {}, _debugState : false,
        _debugMsg : function(msg) {
            var that = this;

            if (that._debugState) {
                console.log('=> Debug:' + msg);
            }
        },
        _attachHandlers: function() {
            var that = this;
            that._debugMsg('[Module] Attaching Module Handlers');
            jQuery(document).ready(function() {
                body = jQuery('body');
                openerp.web.WebClient.include({
                    start: function() {
                        this._super();
                        srcModel._odooM = this;
                        srcModel._modelWatcher(this);
                    },
                });

                jQuery('nav ul li a.oe_menu_toggler, ul#menu_more li a').on('click', function(){
                    that._debugMsg('[Module] Module Changed');
                    srcModel._initModulesRefresh();
                });

                body.on('click','.oe_webclient .oe_leftbar .oe_secondary_menu .oe_secondary_submenu a', function(){
                    that._debugMsg('[Module] Sub-module Changed');
                    if(!srcModel.activeModuleInstance.avoidSubModuleRefresh){
                        srcModel._initModulesRefresh();
                    }
                });
            });
        },
        _modelWatcher: function(scope) {
            var that = this,
                counter = 1;

            that._debugMsg('[MODEL] Model Lookup started');
            modelWatcher = window.setInterval(function() {
                var view, controller;

                if (scope && scope.action_manager && scope.action_manager.inner_widget  
                    && scope.action_manager.inner_widget.active_view) {
                        view = scope.action_manager.inner_widget.active_view;
                        srcModel.scope.model = scope;
                        srcModel.scope.view = scope.action_manager.inner_widget.active_view;
                        srcModel.currentView = scope.action_manager.inner_widget.active_view;
                        srcModel.scope.viewBody = body;
                        srcModel.scope.controller = scope.action_manager.inner_widget.views[view].controller;
                        srcModel.scope.controllerId = srcModel.scope.controller.model;
                    that._debugMsg('[MODEL] Model Found');
                    srcModel._markupWatcher();
                    window.clearInterval(modelWatcher);
                }else if (counter >= 10) {
                    window.clearInterval(modelWatcher);
                    that._debugMsg('[Model] Model Lookup finished');
                    if (markupWatcher) {
                        window.clearInterval(markupWatcher);
                    }
                }
                counter ++;
            }, 2000);
        },
        _markupWatcher: function() {
            this._debugMsg('[MODULE] Looking for custom module files');

            var that = this,
            counter = 1,
            markupWatcher = window.setInterval(function() {
                if (srcModel._modulesInstances.length > 0) {
                    var moduleCont = jQuery('.oe_application .oe_view_manager.oe_view_manager_current');
                    
                    jQuery.each(srcModel._modulesInstances, function(index, module) {
                        var moduleCustomCont = jQuery(module.container);
                        if (moduleCont.length > 0 && moduleCustomCont.length > 0) {
                            srcModel.moduleContainer = moduleCont;
                            srcModel.scope.customModuleSelector = moduleCustomCont;
                            that._debugMsg('[MODULE] Custom Module Found');
                            that._debugMsg('[MODULE] initializing: '+ srcModel.scope.controllerId);
                            srcModel.activeModuleInstance = module;
                            module.inited = true;
                            if (module.viewWatcher) {
                                that._debugMsg('[MODULE] View Watcher Requested');
                                srcModel._viewWatcher(true);
                            }
                            module.instance.init(srcModel.scope, srcModel.scope.view, srcModel.scope.controller);
                            that._debugMsg('[MODULE] Custom Module initialized');
                            window.clearInterval(markupWatcher);
                        }
                    });
                    if (counter >= 5) {
                        that._debugMsg('[MODULE] No custom files found for this module');
                        window.clearInterval(markupWatcher);
                    }
                    counter ++;
                }else{
                    that._debugMsg('[MODULE] There are no custom modules on the queue');
                    window.clearInterval(markupWatcher);
                }
            }, 1500);
        },
        _viewWatcher: function(activate) {
            var that = this;
            if (activate) {
                that._debugMsg('[TIMER] Starting view watcher');
                viewWatcher = window.setInterval(function() {
                    if (srcModel.moduleContainer.attr('data-view-type') !== srcModel.currentView) {
                        srcModel.currentView = srcModel.moduleContainer.attr('data-view-type');
                        srcModel.moduleContainer.trigger('viewChange');
                    }
                }, 1500);
            }else{
                if (viewWatcher) {
                    that._debugMsg('[TIMER] stopping viewWatcher');
                    window.clearInterval(viewWatcher);
                }
            }
        },
        _initModulesRefresh: function() {
            var that = this,
                found = false;
            that._debugMsg('[MODULE] Looking for current instantiate module');

            jQuery.each(srcModel._modulesInstances, function(index, module) {
                if (module.inited) {
                    that._debugMsg('[MODULE] Current Module found');
                    found = true;
                    module.instance.suspend();
                    srcModel.activeModuleInstance = {};
                    module.inited = false;
                    
                }
            });

            srcModel._modelWatcher(srcModel._odooM);

            if (found) {
                that._debugMsg('[MODULE] Instance down');
                return true;
            } else {
                that._debugMsg('[MODULE] Unable to found a module instance running');
                return false;
            }
        },
        _initGlobalDepencies: function() {
        //Init Global JS librarys if required
        },
        /*Start Public access properties*/
        currentView: '',
        moduleContainer : {},
        scope: {},
        initModule: function(module, moduleContainer, viewWat, subModuleRefresh) {
            var viewWatcherInit = (viewWat === true) ? true : false,
            sMRefresh = (subModuleRefresh === true) ? true : false;
            this._modulesInstances.push({instance: module, container: moduleContainer, inited: false, viewWatcher: viewWatcherInit, avoidSubModuleRefresh: sMRefresh});
        },
        init: function(scope) {
            srcModel = this;
            body = jQuery('body');
            srcModel._initGlobalDepencies();
            srcModel._attachHandlers();
        }
        /*End Public access properties*/
    };
    window.SOROCOModel.init();
    /*=== Ends Global JS Handler // DO NOT TOUCH===*/
})(window);
