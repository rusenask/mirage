webpackJsonp([0],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	//import ReactDOM from 'react-dom'
	'use strict';

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

	var _react = __webpack_require__(1);

	var _react2 = _interopRequireDefault(_react);

	var _reactBootstrap = __webpack_require__(157);

	var _reactCookie = __webpack_require__(387);

	var _reactCookie2 = _interopRequireDefault(_reactCookie);

	// creating "track all hosts" button + cookie control

	var TrackingAllHosts = _react2['default'].createClass({
	    displayName: "TrackingAllHosts",

	    getInitialState: function getInitialState() {
	        return { trackingAll: _reactCookie2['default'].load('stubo.all-hosts') || false };
	    },

	    handleClick: function handleClick() {
	        var state = this.state.trackingAll;

	        // cookie options, passed as json object
	        var opt = {
	            'path': "/"
	        };

	        if (this.isMounted()) {
	            _reactCookie2['default'].save('stubo.all-hosts', !state, opt);
	            this.setState({
	                trackingAll: !state
	            });
	        }
	    },

	    render: function render() {
	        var msg = null;
	        if (this.state.trackingAll) {
	            msg = "Disable this option to only see data for current hostname";
	        } else {
	            msg = "Enable this option to see data for all virtualized hosts";
	        }

	        var ButtonTooltip = _react2['default'].createElement(
	            _reactBootstrap.Tooltip,
	            null,
	            ' ',
	            msg,
	            ' '
	        );

	        return _react2['default'].createElement(
	            _reactBootstrap.OverlayTrigger,
	            { placement: 'right', overlay: ButtonTooltip },
	            _react2['default'].createElement(
	                'a',
	                { href: '#', onClick: this.handleClick },
	                _react2['default'].createElement('i', { className: 'fa fa-th' }),
	                _react2['default'].createElement(
	                    'span',
	                    null,
	                    ' Tracking all hosts '
	                ),
	                _react2['default'].createElement('input', { className: 'pull-right',
	                    type: 'checkbox',
	                    checked: this.state.trackingAll,
	                    onChange: this.handleClick })
	            )
	        );
	    }

	});
	//
	//React.render(
	//    <TrackingAllHosts/>,
	//    document.getElementById("trackingall")
	//);

	function getBooleanState(trackingLevel) {
	    return trackingLevel == "full";
	}

	// creating "full tracking" button
	var TrackingLevelComponent = _react2['default'].createClass({
	    displayName: "TrackingLevelComponent",

	    getInitialState: function getInitialState() {
	        return {
	            checked: false,
	            apiHref: "/stubo/api/get/setting?setting=tracking_level"
	        };
	    },

	    // getting current tracking state
	    componentDidMount: function componentDidMount() {
	        // fetching data
	        $.get(this.state.apiHref, (function (result) {
	            var trackingState = result.data.tracking_level;
	            // update state
	            if (this.isMounted()) {
	                this.setState({
	                    checked: getBooleanState(trackingState)
	                });
	            }
	        }).bind(this));
	    },

	    handleClick: function handleClick() {
	        // getting current state
	        var fullTrack = this.state.checked;

	        var settingValue = "full";
	        if (fullTrack) {
	            settingValue = "normal";
	        }
	        // creating uri to change current state
	        var uri = "/stubo/api/put/setting?setting=tracking_level&value=" + settingValue;

	        $.get(uri, (function (result) {
	            var trackingState = result.data.tracking_level;
	            // update state
	            if (this.isMounted()) {
	                this.setState({
	                    checked: getBooleanState(trackingState)
	                });
	            }
	        }).bind(this));
	    },

	    render: function render() {
	        var msg = null;
	        if (this.state.checked) {
	            msg = "Disable full tracking (debugging) mode.";
	        } else {
	            msg = "Enable this option to capture more data. Beware that this option is global and decreases" + " performance for all virtual Mirage instances.";
	        }

	        var ButtonTooltip = _react2['default'].createElement(
	            _reactBootstrap.Tooltip,
	            null,
	            ' ',
	            msg,
	            ' '
	        );

	        // rendering field with checkbox
	        return _react2['default'].createElement(
	            _reactBootstrap.OverlayTrigger,
	            { placement: 'right', overlay: ButtonTooltip },
	            _react2['default'].createElement(
	                'a',
	                { href: '#', onClick: this.handleClick },
	                _react2['default'].createElement('i', { className: 'fa fa-flash' }),
	                _react2['default'].createElement(
	                    'span',
	                    null,
	                    ' Full tracking level '
	                ),
	                _react2['default'].createElement('input', { className: 'pull-right',
	                    type: 'checkbox',
	                    checked: this.state.checked,
	                    onChange: this.handleClick })
	            )
	        );
	    }

	});

	var SettingsComponent = _react2['default'].createClass({
	    displayName: 'SettingsComponent',

	    render: function render() {
	        var trackingLevel = _react2['default'].createElement(
	            'li',
	            null,
	            _react2['default'].createElement(TrackingLevelComponent, null)
	        );
	        var allHosts = _react2['default'].createElement(
	            'li',
	            null,
	            _react2['default'].createElement(TrackingAllHosts, null)
	        );
	        return _react2['default'].createElement(
	            'ul',
	            { className: 'sidebar-menu' },
	            trackingLevel,
	            allHosts
	        );
	    }

	});

	_react2['default'].render(_react2['default'].createElement(SettingsComponent, null), document.getElementById("SettingsComponent"));

/***/ },

/***/ 387:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var cookie = __webpack_require__(388);

	var _rawCookie = {};
	var _res = undefined;

	function load(name, doNotParse) {
	  var cookies = {};

	  if (typeof document !== 'undefined') {
	    cookies = cookie.parse(document.cookie);
	  }

	  var cookieVal = cookies && cookies[name] || _rawCookie[name];

	  if (!doNotParse) {
	    try {
	      cookieVal = JSON.parse(cookieVal);
	    } catch (e) {
	      // Not serialized object
	    }
	  }

	  return cookieVal;
	}

	function save(name, val, opt) {
	  _rawCookie[name] = val;

	  // allow you to work with cookies as objects.
	  if (typeof val === 'object') {
	    _rawCookie[name] = JSON.stringify(val);
	  }

	  // Cookies only work in the browser
	  if (typeof document !== 'undefined') {
	    document.cookie = cookie.serialize(name, _rawCookie[name], opt);
	  }

	  if (_res && _res.cookie) {
	    _res.cookie(name, val, opt);
	  }
	}

	function remove(name, path) {
	  delete _rawCookie[name];

	  if (typeof document !== 'undefined') {
	    var removeCookie = name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';

	    if (path) {
	      removeCookie += ' path=' + path;
	    }

	    document.cookie = removeCookie;
	  }

	  if (_res && _res.clearCookie) {
	    var opt = path ? { path: path } : undefined;
	    _res.clearCookie(name, opt);
	  }
	}

	function setRawCookie(rawCookie) {
	  _rawCookie = cookie.parse(rawCookie);
	}

	function plugToRequest(req, res) {
	  if (req) {
	    if (req.cookie) {
	      _rawCookie = req.cookie;
	    } else if (req.headers && req.headers.cookie) {
	      setRawCookie(req.headers.cookie);
	    }
	  }

	  _res = res;
	}

	var reactCookie = {
	  load: load,
	  save: save,
	  remove: remove,
	  setRawCookie: setRawCookie,
	  plugToRequest: plugToRequest
	};

	if (typeof window !== 'undefined') {
	  window['reactCookie'] = reactCookie;
	}

	module.exports = reactCookie;

/***/ },

/***/ 388:
/***/ function(module, exports) {

	/*!
	 * cookie
	 * Copyright(c) 2012-2014 Roman Shtylman
	 * Copyright(c) 2015 Douglas Christopher Wilson
	 * MIT Licensed
	 */

	/**
	 * Module exports.
	 * @public
	 */

	'use strict';

	exports.parse = parse;
	exports.serialize = serialize;

	/**
	 * Module variables.
	 * @private
	 */

	var decode = decodeURIComponent;
	var encode = encodeURIComponent;

	/**
	 * RegExp to match field-content in RFC 7230 sec 3.2
	 *
	 * field-content = field-vchar [ 1*( SP / HTAB ) field-vchar ]
	 * field-vchar   = VCHAR / obs-text
	 * obs-text      = %x80-FF
	 */

	var fieldContentRegExp = /^[\u0009\u0020-\u007e\u0080-\u00ff]+$/;

	/**
	 * Parse a cookie header.
	 *
	 * Parse the given cookie header string into an object
	 * The object has the various cookies as keys(names) => values
	 *
	 * @param {string} str
	 * @param {object} [options]
	 * @return {object}
	 * @public
	 */

	function parse(str, options) {
	  if (typeof str !== 'string') {
	    throw new TypeError('argument str must be a string');
	  }

	  var obj = {};
	  var opt = options || {};
	  var pairs = str.split(/; */);
	  var dec = opt.decode || decode;

	  pairs.forEach(function (pair) {
	    var eq_idx = pair.indexOf('=');

	    // skip things that don't look like key=value
	    if (eq_idx < 0) {
	      return;
	    }

	    var key = pair.substr(0, eq_idx).trim();
	    var val = pair.substr(++eq_idx, pair.length).trim();

	    // quoted values
	    if ('"' == val[0]) {
	      val = val.slice(1, -1);
	    }

	    // only assign once
	    if (undefined == obj[key]) {
	      obj[key] = tryDecode(val, dec);
	    }
	  });

	  return obj;
	}

	/**
	 * Serialize data into a cookie header.
	 *
	 * Serialize the a name value pair into a cookie string suitable for
	 * http headers. An optional options object specified cookie parameters.
	 *
	 * serialize('foo', 'bar', { httpOnly: true })
	 *   => "foo=bar; httpOnly"
	 *
	 * @param {string} name
	 * @param {string} val
	 * @param {object} [options]
	 * @return {string}
	 * @public
	 */

	function serialize(name, val, options) {
	  var opt = options || {};
	  var enc = opt.encode || encode;

	  if (!fieldContentRegExp.test(name)) {
	    throw new TypeError('argument name is invalid');
	  }

	  var value = enc(val);

	  if (value && !fieldContentRegExp.test(value)) {
	    throw new TypeError('argument val is invalid');
	  }

	  var pairs = [name + '=' + value];

	  if (null != opt.maxAge) {
	    var maxAge = opt.maxAge - 0;
	    if (isNaN(maxAge)) throw new Error('maxAge should be a Number');
	    pairs.push('Max-Age=' + maxAge);
	  }

	  if (opt.domain) {
	    if (!fieldContentRegExp.test(opt.domain)) {
	      throw new TypeError('option domain is invalid');
	    }

	    pairs.push('Domain=' + opt.domain);
	  }

	  if (opt.path) {
	    if (!fieldContentRegExp.test(opt.path)) {
	      throw new TypeError('option path is invalid');
	    }

	    pairs.push('Path=' + opt.path);
	  }

	  if (opt.expires) pairs.push('Expires=' + opt.expires.toUTCString());
	  if (opt.httpOnly) pairs.push('HttpOnly');
	  if (opt.secure) pairs.push('Secure');

	  return pairs.join('; ');
	}

	/**
	 * Try decoding a string using a decoding function.
	 *
	 * @param {string} str
	 * @param {function} decode
	 * @private
	 */

	function tryDecode(str, decode) {
	  try {
	    return decode(str);
	  } catch (e) {
	    return str;
	  }
	}

/***/ }

});