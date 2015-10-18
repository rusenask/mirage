webpackJsonp([8],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	/**
	 * Created by karolisrusenas on 22/09/15.
	 */

	'use strict';

	var React = __webpack_require__(146);

	var Inspector = __webpack_require__(!(function webpackMissingModule() { var e = new Error("Cannot find module \"../node_modules/react-json-inspector\""); e.code = 'MODULE_NOT_FOUND'; throw e; }()));

	function getUrlVars() {
	    var vars = [],
	        hash;
	    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	    for (var i = 0; i < hashes.length; i++) {
	        hash = hashes[i].split('=');
	        vars.push(hash[0]);
	        vars[hash[0]] = hash[1];
	    }
	    return vars;
	}

	var LoadJsonData = function LoadJsonData(href) {
	    // getting current url
	    if (href == null) {
	        href = getUrlVars()["scenario"];
	    }
	    // adding stubs path
	    href = href + '/stubs';

	    $.get(href, function (result) {
	        // render component
	        React.render(React.createElement(Inspector, {
	            ignoreCase: false,
	            data: result.data }), document.getElementById('app'));
	    });
	};

	LoadJsonData();

/***/ }
]);