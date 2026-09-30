/******************************************************************************/
//Paging with Pages Interaction Plugin v0.0.4
//Initially (c) 2024 Benjamin Zachey at http://msx.benzac.de/interaction/js/paging.js
//Action syntax examples:
//- "content:request:interaction:http://link.to.content?page={PAGE}&@http://msx.benzac.de/interaction/paging.html"
//- "content:request:interaction:http://link.to.content?page={PAGE}|1&@http://msx.benzac.de/interaction/paging.html"
/******************************************************************************/

/******************************************************************************/
//PagingSettings
/******************************************************************************/
var PagingSettings = {
    MIN_APP_VERSION: "0.1.82",
    DEFAULT_PAGE: 1,
    CACHE_ALL_DATA: true
};
/******************************************************************************/

/******************************************************************************/
//PagingHandler
/******************************************************************************/
function PagingHandler() {
    var infoData = null;
    var pagingBaseUrl = null;
    var pagingData = null;
    var pagingPage = PagingSettings.DEFAULT_PAGE;
    var pagingCache = {};
    var dataService = new TVXDataService();
    var readyService = new TVXBusyService();
    var extending = false;

    //--------------------------------------------------------------------------
    //Private functions
    //--------------------------------------------------------------------------
    var getDeviceId = function() {
        return TVXTools.strFullCheck(infoData != null && infoData.info != null ? infoData.info.id : null, null);
    };
    var decodeUrl = function(url) {
        return TVXTools.isFullStr(url) && url.indexOf("id:") == 0 ? TVXTools.base64DecodeId(url.substr(3)) : url;
    };
    var secureUrl = function(url) {
        return TVXTools.isSecureContext() ? TVXTools.secureUrl(url) : url;
    };
    var completeError = function(error) {
        if (error != null && TVXTools.isFullStr(error.message)) {
            error = error.message;
        }
        if (TVXTools.isFullStr(error) && error.lastIndexOf(".") != error.length - 1) {
            return error + ".";
        }
        return error;
    };
    var createServiceOptions = function(url) {
        return TVXTools.isFullStr(url) ? {
            withCredentials: url.indexOf("credentials") > 0
        } : null;
    };
    var createPagingUrl = function(url, page) {
        return TVXTools.strReplaceMap(url, {
            "{ID}": TVXTools.strToUrlStr(getDeviceId()),
            "{PAGE}": page
        });
    };
    var validatePagingStartData = function(data) {
        //Template and items are needed for the start data
        return data != null && data.template != null && data.items != null && data.items.length >= 0;
    };
    var validatePagingExtensionData = function(data) {
        //Only items are needed for the extension data
        return data != null && data.items != null && data.items.length >= 0;
    };
    var completePagingData = function(data, page, extendable) {
        if (data != null && data.items != null && data.items.length > 0) {
            var items = data.items;
            for (var i = 0; i < items.length; i++) {
                if (extendable && i == items.length - 1) {
                    //Replace live object for last item in the list to extend it
                    if (items[i].extended !== true) {
                        items[i].extended = true;
                        items[i].liveOrigin = items[i].live != null ? items[i].live : null;
                        items[i].live = {
                            type: "setup",
                            action: "interaction:commit:message:extend"
                        };
                    }
                } else if (items[i].extended === true) {
                    //Restore live object
                    items[i].extended = false;
                    items[i].live = items[i].liveOrigin;
                    items[i].liveOrigin = null;
                }
            }
        }
        return data;
    };
    var mergePagingData = function(data, extension, page) {
        if (data != null && data.items != null && data.items.length > 0 &&
                extension != null && extension.items != null && extension.items.length > 0) {
            for (var i = 0; i < extension.items.length; i++) {
                data.items.push(extension.items[i]);
            }
        }
        return completePagingData(data, page, extension.items.length > 0);
    };
    var createCacheId = function(url, page) {
        return TVXTools.isHttpUrl(url) && TVXTools.createHash(url + "|" + page);
    };
    var cachePagingData = function(url, page, data) {
        var id = createCacheId(url, page);
        if (id != null && data != null && data.cache !== false) {
            pagingCache[id] = {
                url: url,
                page: page,
                data: data
            };
        }
    };
    var restorePagingData = function(url, page) {
        var id = createCacheId(url, page);
        return id != null ? pagingCache[id] : null;
    };
    var processPagingData = function(url, page) {
        return url == pagingBaseUrl && page == pagingPage;
    };
    var createWarning = function(headline, message, action) {
        return {
            type: "pages",
            headline: "Warning",
            pages: [{
                    items: [{
                            type: "default",
                            layout: "0,0,12,6",
                            color: "msx-glass",
                            headline: "{ico:msx-yellow:warning} " + TVXTools.strFullCheck(headline, "Content Not Available"),
                            text: [
                                TVXTools.strFullCheck(message, "Content could not be loaded."),
                                "{br}{br}",
                                action == "reload" ? "Please press {txt:msx-white:OK} to reload." : action == "update" ? "Please update Media Station X and try it again." : ""
                            ],
                            action: action == "reload" ? "[invalidate:content|reload:content]" : null
                        }]
                }]
        };
    };
    var loadPagingData = function(url, page, callback) {
        var restoredData = null;
        if (PagingSettings.CACHE_ALL_DATA) {
            cachePagingData(pagingBaseUrl, pagingPage, pagingData);
            restoredData = restorePagingData(url, page);
        }
        if (restoredData != null) {
            pagingBaseUrl = restoredData.url;
            pagingPage = restoredData.page;
            pagingData = restoredData.data;
            TVXInteractionPlugin.debug("Restored paging data: " + createPagingUrl(pagingBaseUrl, pagingPage));
            callback(pagingData);
        } else {
            pagingBaseUrl = url;
            pagingPage = page;
            pagingData = null;
            if (TVXTools.isHttpUrl(pagingBaseUrl)) {
                var currentBasedUrl = pagingBaseUrl;
                var currentPage = pagingPage;
                var pagingStartUrl = createPagingUrl(pagingBaseUrl, pagingPage);
                TVXInteractionPlugin.debug("Load paging data: " + pagingStartUrl);
                dataService.loadData("temp:data", pagingStartUrl, {
                    success: function(entry) {
                        if (processPagingData(currentBasedUrl, currentPage)) {
                            if (validatePagingStartData(entry.data)) {
                                extending = false;
                                pagingData = completePagingData(entry.data, pagingPage, true);
                                callback(pagingData);
                            } else {
                                callback(createWarning(null, "Paging start data is invalid.", "reload"));
                            }
                        }
                    },
                    error: function(entry) {
                        if (processPagingData(currentBasedUrl, currentPage)) {
                            callback(createWarning(null, "Paging start data could not be loaded. " + completeError(entry.error), "reload"));
                        }
                    }
                }, createServiceOptions());
            } else {
                callback(createWarning(null, "Paging start URL is invalid."));
            }
        }
    };
    var extendPagingData = function() {
        if (TVXTools.isHttpUrl(pagingBaseUrl)) {
            if (pagingData != null) {
                if (!extending) {
                    extending = true;
                    var currentBasedUrl = pagingBaseUrl;
                    var currentPage = pagingPage;
                    var pagingExtendUrl = createPagingUrl(pagingBaseUrl, currentPage + 1);
                    TVXInteractionPlugin.debug("Extend paging data: " + pagingExtendUrl);
                    dataService.loadData("temp:data", pagingExtendUrl, {
                        success: function(entry) {
                            if (pagingData != null && processPagingData(currentBasedUrl, currentPage)) {
                                extending = false;
                                if (validatePagingExtensionData(entry.data)) {
                                    pagingPage += 1;
                                    pagingData = mergePagingData(pagingData, entry.data, pagingPage);
                                    TVXInteractionPlugin.executeAction("reload:content");
                                } else {
                                    TVXInteractionPlugin.warn("Paging extension data is invalid.");
                                }
                            }
                        },
                        error: function(entry) {
                            if (pagingData != null && processPagingData(currentBasedUrl, currentPage)) {
                                extending = false;
                                TVXInteractionPlugin.warn("Paging extension data could not be loaded. " + completeError(entry.error));
                            }
                        }
                    }, createServiceOptions());
                }
            } else {
                TVXInteractionPlugin.warn("Paging start data is not available.");
            }
        } else {
            TVXInteractionPlugin.warn("Paging start URL is invalid.");
        }
    };
    //--------------------------------------------------------------------------

    //--------------------------------------------------------------------------
    //Public functions
    //--------------------------------------------------------------------------
    this.init = function() {
        //Placeholder
    };
    this.ready = function() {
        readyService.start();
        TVXInteractionPlugin.requestData("info", function(data) {
            infoData = data;
            readyService.stop();
        });
    };
    this.handleData = function(data) {
        if (TVXTools.isFullStr(data.message)) {
            if (data.message == "extend") {
                extendPagingData();
            } else {
                TVXInteractionPlugin.warn("Unknown interaction message: '" + data.message + "'");
            }
        }
    };
    this.handleRequest = function(dataId, data, callback) {
        if (TVXTools.isFullStr(dataId)) {
            readyService.onReady(function() {
                if (TVXPluginTools.checkApplication(infoData, PagingSettings.MIN_APP_VERSION)) {
                    var token = dataId.split("|");
                    var url = secureUrl(decodeUrl(token[0]));

                    var requestedPage = TVXTools.strToNum(token.length > 1 ? token[1] : null, PagingSettings.DEFAULT_PAGE);
                    var page = (pagingData != null && pagingBaseUrl == url) ? pagingPage : requestedPage;

                    if (pagingData != null && pagingBaseUrl == url && pagingPage == page) {
                        callback(pagingData);
                    } else {
                        loadPagingData(url, page, callback);
                    }
                } else {
                    callback(createWarning("Version Not Supported", "Media Station X version {txt:msx-white:" + PagingSettings.MIN_APP_VERSION + "} or higher is needed for this plugin.", "update"));
                }
            });
        } else {
            callback({
                error: "Invalid paging data ID: '" + dataId + "': ID must be a full string"
            });
        }
    };
    //--------------------------------------------------------------------------

}
/******************************************************************************/

/******************************************************************************/
//Setup
/******************************************************************************/
TVXPluginTools.onReady(function() {
    TVXInteractionPlugin.setupHandler(new PagingHandler());
    TVXInteractionPlugin.init();
});
/******************************************************************************/