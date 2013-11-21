// GroupServer JavaScript module for providing the Search mechanism
//
// Copyright © 2013 OnlineGroups.net and Contributors.
// All Rights Reserved.
//
// This software is subject to the provisions of the Zope Public License,
// Version 2.1 (ZPL). http://groupserver.org/downloads/license/
//
jQuery.noConflict();

function init_topic_search() {
    var topicsSearch=null, b=null, url=null,
        ts = '#gs-group-messages-topics-search';

    b = jQuery('base').attr('href');
    if (b[b.length -1] != '/') {
        b = b + '/';
    }
    url = b + 'gs-group-topics-ajax.html';
    topicsSearch = GSSearch(ts, url, 0, 6, {}, null);
    jQuery(ts).on('resultsloaded',
                  function(){jQuery('abbr[role=tooltip]').tooltip()});
    jQuery('#gs-group-messages-base-tabs-buttons li:first-child a').click();
    topicsSearch.load();
}

// Connect to the DOM being ready, rather than the window loading, so the
// topics can load while all the other assets are being downloaded
jQuery(document).ready(function () {
    gsJsLoader.with_module('/++resource++gs-search-base-js-min-20131121.js',
                           init_topic_search);
});
