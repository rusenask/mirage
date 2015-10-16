webpackJsonp([8],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	/**
	 * Created by karolisrusenas on 22/09/15.
	 */

	'use strict';

	var React = __webpack_require__(146);

	var Inspector = __webpack_require__(555);

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

/***/ },

/***/ 555:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(146);
	var D = React.DOM;

	var Leaf = __webpack_require__(556);
	var leaf = React.createFactory(Leaf);
	var SearchBar = __webpack_require__(561);
	var searchBar = React.createFactory(SearchBar);

	var filterer = __webpack_require__(565);
	var isEmpty = __webpack_require__(567);
	var lens = __webpack_require__(568);
	var noop = __webpack_require__(564);

	module.exports = React.createClass({
	    displayName: 'exports',

	    propTypes: {
	        data: React.PropTypes.oneOfType([React.PropTypes.object.isRequired, React.PropTypes.array.isRequired]),
	        // For now it expects a factory function, not element.
	        search: React.PropTypes.oneOfType([React.PropTypes.func, React.PropTypes.bool]),
	        onClick: React.PropTypes.func,
	        validateQuery: React.PropTypes.func,
	        isExpanded: React.PropTypes.func,
	        filterOptions: React.PropTypes.object
	    },

	    getDefaultProps: function getDefaultProps() {
	        return {
	            data: null,
	            search: searchBar,
	            className: '',
	            id: 'json-' + Date.now(),
	            onClick: noop,
	            filterOptions: {},
	            validateQuery: function validateQuery(query) {
	                return query.length >= 2;
	            },
	            /**
	             * Decide whether the leaf node at given `keypath` should be
	             * expanded initially.
	             * @param  {String} keypath
	             * @param  {Any} value
	             * @return {Boolean}
	             */
	            isExpanded: function isExpanded(keypath, value) {
	                return false;
	            }
	        };
	    },
	    getInitialState: function getInitialState() {
	        return {
	            query: ''
	        };
	    },
	    render: function render() {
	        var p = this.props;
	        var s = this.state;

	        var data = s.query ? s.filterer(s.query) : p.data;

	        var rootNode = leaf({
	            data: data,
	            onClick: p.onClick,
	            id: p.id,
	            getOriginal: this.getOriginal,
	            query: s.query,
	            label: 'root',
	            root: true,
	            isExpanded: p.isExpanded,
	            interactiveLabel: p.interactiveLabel
	        });

	        var notFound = D.div({ className: 'json-inspector__not-found' }, 'Nothing found');

	        return D.div({ className: 'json-inspector ' + p.className }, this.renderToolbar(), isEmpty(data) ? notFound : rootNode);
	    },
	    renderToolbar: function renderToolbar() {
	        var search = this.props.search;

	        if (search) {
	            return D.div({ className: 'json-inspector__toolbar' }, search({ onChange: this.search, data: this.props.data }));
	        }
	    },
	    search: function search(query) {
	        if (query === '' || this.props.validateQuery(query)) {
	            this.setState({
	                query: query
	            });
	        }
	    },
	    componentDidMount: function componentDidMount() {
	        this.createFilterer(this.props.data, this.props.filterOptions);
	    },
	    componentWillReceiveProps: function componentWillReceiveProps(p) {
	        this.createFilterer(p.data, p.filterOptions);
	    },
	    shouldComponentUpdate: function shouldComponentUpdate(p, s) {
	        return s.query !== this.state.query || p.data !== this.props.data || p.onClick !== this.props.onClick;
	    },
	    createFilterer: function createFilterer(data, options) {
	        this.setState({
	            filterer: filterer(data, options)
	        });
	    },
	    getOriginal: function getOriginal(path) {
	        return lens(this.props.data, path);
	    }
	});

/***/ },

/***/ 556:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(146);
	var D = React.DOM;

	var md5omatic = __webpack_require__(557);

	var uid = __webpack_require__(558);
	var type = __webpack_require__(559);

	var Highlighter = __webpack_require__(560);
	var highlighter = React.createFactory(Highlighter);

	var PATH_PREFIX = '.root.';

	var Leaf = React.createClass({
	    displayName: 'Leaf',

	    getInitialState: function getInitialState() {
	        return {
	            expanded: this._isInitiallyExpanded(this.props)
	        };
	    },
	    getDefaultProps: function getDefaultProps() {
	        return {
	            root: false,
	            prefix: ''
	        };
	    },
	    render: function render() {
	        var id = 'id_' + uid();
	        var p = this.props;

	        var d = {
	            path: this.keypath(),
	            key: p.label.toString(),
	            value: p.data
	        };

	        var onLabelClick = this._onClick.bind(this, d);

	        return D.div({ className: this.getClassName(), id: 'leaf-' + this._rootPath() }, D.input({ className: 'json-inspector__radio', type: 'radio', name: p.id, id: id, tabIndex: -1 }), D.label({ className: 'json-inspector__line', htmlFor: id, onClick: onLabelClick }, D.div({ className: 'json-inspector__flatpath' }, d.path), D.span({ className: 'json-inspector__key' }, this.format(d.key), ':', this.renderInteractiveLabel(d.key, true)), this.renderTitle(), this.renderShowOriginalButton()), this.renderChildren());
	    },
	    renderTitle: function renderTitle() {
	        var data = this.data();
	        var t = type(data);

	        switch (t) {
	            case 'Array':
	                return D.span({ className: 'json-inspector__value json-inspector__value_helper' }, '[] ' + items(data.length));
	            case 'Object':
	                return D.span({ className: 'json-inspector__value json-inspector__value_helper' }, '{} ' + items(Object.keys(data).length));
	            default:
	                return D.span({ className: 'json-inspector__value json-inspector__value_' + t.toLowerCase() }, this.format(String(data)), this.renderInteractiveLabel(data, false));
	        }
	    },
	    renderChildren: function renderChildren() {
	        var p = this.props;
	        var childPrefix = this._rootPath();
	        var data = this.data();

	        if (this.state.expanded && !isPrimitive(data)) {
	            return Object.keys(data).map(function (key) {
	                var value = data[key];

	                return leaf({
	                    data: value,
	                    label: key,
	                    prefix: childPrefix,
	                    onClick: p.onClick,
	                    id: p.id,
	                    query: p.query,
	                    getOriginal: this.state.original ? null : p.getOriginal,
	                    key: getLeafKey(key, value),
	                    isExpanded: p.isExpanded,
	                    interactiveLabel: p.interactiveLabel
	                });
	            }, this);
	        }

	        return null;
	    },
	    renderShowOriginalButton: function renderShowOriginalButton() {
	        var p = this.props;

	        if (isPrimitive(p.data) || this.state.original || !p.getOriginal || !p.query || contains(this.keypath(), p.query)) {
	            return null;
	        }

	        return D.span({
	            className: 'json-inspector__show-original',
	            onClick: this._onShowOriginalClick
	        });
	    },
	    renderInteractiveLabel: function renderInteractiveLabel(originalValue, isKey) {
	        if (typeof this.props.interactiveLabel === 'function') {
	            return this.props.interactiveLabel({
	                // The distinction between `value` and `originalValue` is
	                // provided to have backwards compatibility.
	                value: String(originalValue),
	                originalValue: originalValue,
	                isKey: isKey,
	                keypath: this.keypath()
	            });
	        }

	        return null;
	    },
	    componentWillReceiveProps: function componentWillReceiveProps(p) {
	        if (p.query) {
	            this.setState({
	                expanded: !contains(p.label, p.query)
	            });
	        }

	        // Restore original expansion state when switching from search mode
	        // to full browse mode.
	        if (this.props.query && !p.query) {
	            this.setState({
	                expanded: this._isInitiallyExpanded(p)
	            });
	        }
	    },
	    _rootPath: function _rootPath() {
	        return this.props.prefix + '.' + this.props.label;
	    },
	    keypath: function keypath() {
	        return this._rootPath().substr(PATH_PREFIX.length);
	    },
	    data: function data() {
	        return this.state.original || this.props.data;
	    },
	    format: function format(string) {
	        return highlighter({
	            string: string,
	            highlight: this.props.query
	        });
	    },
	    getClassName: function getClassName() {
	        var cn = 'json-inspector__leaf';

	        if (this.props.root) {
	            cn += ' json-inspector__leaf_root';
	        }

	        if (this.state.expanded) {
	            cn += ' json-inspector__leaf_expanded';
	        }

	        if (!isPrimitive(this.props.data)) {
	            cn += ' json-inspector__leaf_composite';
	        }

	        return cn;
	    },
	    toggle: function toggle() {
	        this.setState({
	            expanded: !this.state.expanded
	        });
	    },
	    _onClick: function _onClick(data, e) {
	        this.toggle();
	        this.props.onClick(data);

	        e.stopPropagation();
	    },
	    _onShowOriginalClick: function _onShowOriginalClick(e) {
	        this.setState({
	            original: this.props.getOriginal(this.keypath())
	        });

	        e.stopPropagation();
	    },
	    _isInitiallyExpanded: function _isInitiallyExpanded(p) {
	        var keypath = this.keypath();

	        if (p.root) {
	            return true;
	        }

	        if (p.query === '') {
	            return p.isExpanded(keypath, p.data);
	        } else {
	            // When a search query is specified, first check if the keypath
	            // contains the search query: if it does, then the current leaf
	            // is itself a search result and there is no need to expand further.
	            //
	            // Having a `getOriginal` function passed signalizes that current
	            // leaf only displays a subset of data, thus should be rendered
	            // expanded to reveal the children that is being searched for.
	            return !contains(keypath, p.query) && typeof p.getOriginal === 'function';
	        }
	    }
	});

	// FIXME: There should be a better way to call a component factory from inside
	// component definition.
	var leaf = React.createFactory(Leaf);

	function items(count) {
	    return count + (count === 1 ? ' item' : ' items');
	}

	function getLeafKey(key, value) {
	    if (isPrimitive(value)) {
	        // TODO: Sanitize `value` better.
	        var hash = md5omatic(String(value));
	        return key + ':' + hash;
	    } else {
	        return key + '[' + type(value) + ']';
	    }
	}

	function contains(string, substring) {
	    return string.indexOf(substring) !== -1;
	}

	function isPrimitive(value) {
	    var t = type(value);
	    return t !== 'Object' && t !== 'Array';
	}

	module.exports = Leaf;

/***/ },

/***/ 557:
/***/ function(module, exports) {

	"use strict";

	/**
	 * Expose `md5omatic(str)`.
	 */

	module.exports = md5omatic;

	/**
	 * Hash any string using message digest.
	 *
	 * @param {String} str
	 * @return {String}
	 * @api public
	 */

	function md5omatic(str) {
	    var x = str2blks_MD5(str);
	    var a = 1732584193;
	    var b = -271733879;
	    var c = -1732584194;
	    var d = 271733878;

	    for (var i = 0; i < x.length; i += 16) {
	        var olda = a;
	        var oldb = b;
	        var oldc = c;
	        var oldd = d;

	        a = ff(a, b, c, d, x[i + 0], 7, -680876936);
	        d = ff(d, a, b, c, x[i + 1], 12, -389564586);
	        c = ff(c, d, a, b, x[i + 2], 17, 606105819);
	        b = ff(b, c, d, a, x[i + 3], 22, -1044525330);
	        a = ff(a, b, c, d, x[i + 4], 7, -176418897);
	        d = ff(d, a, b, c, x[i + 5], 12, 1200080426);
	        c = ff(c, d, a, b, x[i + 6], 17, -1473231341);
	        b = ff(b, c, d, a, x[i + 7], 22, -45705983);
	        a = ff(a, b, c, d, x[i + 8], 7, 1770035416);
	        d = ff(d, a, b, c, x[i + 9], 12, -1958414417);
	        c = ff(c, d, a, b, x[i + 10], 17, -42063);
	        b = ff(b, c, d, a, x[i + 11], 22, -1990404162);
	        a = ff(a, b, c, d, x[i + 12], 7, 1804603682);
	        d = ff(d, a, b, c, x[i + 13], 12, -40341101);
	        c = ff(c, d, a, b, x[i + 14], 17, -1502002290);
	        b = ff(b, c, d, a, x[i + 15], 22, 1236535329);
	        a = gg(a, b, c, d, x[i + 1], 5, -165796510);
	        d = gg(d, a, b, c, x[i + 6], 9, -1069501632);
	        c = gg(c, d, a, b, x[i + 11], 14, 643717713);
	        b = gg(b, c, d, a, x[i + 0], 20, -373897302);
	        a = gg(a, b, c, d, x[i + 5], 5, -701558691);
	        d = gg(d, a, b, c, x[i + 10], 9, 38016083);
	        c = gg(c, d, a, b, x[i + 15], 14, -660478335);
	        b = gg(b, c, d, a, x[i + 4], 20, -405537848);
	        a = gg(a, b, c, d, x[i + 9], 5, 568446438);
	        d = gg(d, a, b, c, x[i + 14], 9, -1019803690);
	        c = gg(c, d, a, b, x[i + 3], 14, -187363961);
	        b = gg(b, c, d, a, x[i + 8], 20, 1163531501);
	        a = gg(a, b, c, d, x[i + 13], 5, -1444681467);
	        d = gg(d, a, b, c, x[i + 2], 9, -51403784);
	        c = gg(c, d, a, b, x[i + 7], 14, 1735328473);
	        b = gg(b, c, d, a, x[i + 12], 20, -1926607734);
	        a = hh(a, b, c, d, x[i + 5], 4, -378558);
	        d = hh(d, a, b, c, x[i + 8], 11, -2022574463);
	        c = hh(c, d, a, b, x[i + 11], 16, 1839030562);
	        b = hh(b, c, d, a, x[i + 14], 23, -35309556);
	        a = hh(a, b, c, d, x[i + 1], 4, -1530992060);
	        d = hh(d, a, b, c, x[i + 4], 11, 1272893353);
	        c = hh(c, d, a, b, x[i + 7], 16, -155497632);
	        b = hh(b, c, d, a, x[i + 10], 23, -1094730640);
	        a = hh(a, b, c, d, x[i + 13], 4, 681279174);
	        d = hh(d, a, b, c, x[i + 0], 11, -358537222);
	        c = hh(c, d, a, b, x[i + 3], 16, -722521979);
	        b = hh(b, c, d, a, x[i + 6], 23, 76029189);
	        a = hh(a, b, c, d, x[i + 9], 4, -640364487);
	        d = hh(d, a, b, c, x[i + 12], 11, -421815835);
	        c = hh(c, d, a, b, x[i + 15], 16, 530742520);
	        b = hh(b, c, d, a, x[i + 2], 23, -995338651);
	        a = ii(a, b, c, d, x[i + 0], 6, -198630844);
	        d = ii(d, a, b, c, x[i + 7], 10, 1126891415);
	        c = ii(c, d, a, b, x[i + 14], 15, -1416354905);
	        b = ii(b, c, d, a, x[i + 5], 21, -57434055);
	        a = ii(a, b, c, d, x[i + 12], 6, 1700485571);
	        d = ii(d, a, b, c, x[i + 3], 10, -1894986606);
	        c = ii(c, d, a, b, x[i + 10], 15, -1051523);
	        b = ii(b, c, d, a, x[i + 1], 21, -2054922799);
	        a = ii(a, b, c, d, x[i + 8], 6, 1873313359);
	        d = ii(d, a, b, c, x[i + 15], 10, -30611744);
	        c = ii(c, d, a, b, x[i + 6], 15, -1560198380);
	        b = ii(b, c, d, a, x[i + 13], 21, 1309151649);
	        a = ii(a, b, c, d, x[i + 4], 6, -145523070);
	        d = ii(d, a, b, c, x[i + 11], 10, -1120210379);
	        c = ii(c, d, a, b, x[i + 2], 15, 718787259);
	        b = ii(b, c, d, a, x[i + 9], 21, -343485551);

	        a = addme(a, olda);
	        b = addme(b, oldb);
	        c = addme(c, oldc);
	        d = addme(d, oldd);
	    }

	    return rhex(a) + rhex(b) + rhex(c) + rhex(d);
	};

	var hex_chr = "0123456789abcdef";

	function bitOR(a, b) {
	    var lsb = a & 0x1 | b & 0x1;
	    var msb31 = a >>> 1 | b >>> 1;

	    return msb31 << 1 | lsb;
	}

	function bitXOR(a, b) {
	    var lsb = a & 0x1 ^ b & 0x1;
	    var msb31 = a >>> 1 ^ b >>> 1;

	    return msb31 << 1 | lsb;
	}

	function bitAND(a, b) {
	    var lsb = a & 0x1 & (b & 0x1);
	    var msb31 = a >>> 1 & b >>> 1;

	    return msb31 << 1 | lsb;
	}

	function addme(x, y) {
	    var lsw = (x & 0xFFFF) + (y & 0xFFFF);
	    var msw = (x >> 16) + (y >> 16) + (lsw >> 16);

	    return msw << 16 | lsw & 0xFFFF;
	}

	function rhex(num) {
	    var str = "";
	    var j;

	    for (j = 0; j <= 3; j++) str += hex_chr.charAt(num >> j * 8 + 4 & 0x0F) + hex_chr.charAt(num >> j * 8 & 0x0F);

	    return str;
	}

	function str2blks_MD5(str) {
	    var nblk = (str.length + 8 >> 6) + 1;
	    var blks = new Array(nblk * 16);
	    var i;

	    for (i = 0; i < nblk * 16; i++) blks[i] = 0;

	    for (i = 0; i < str.length; i++) blks[i >> 2] |= str.charCodeAt(i) << (str.length * 8 + i) % 4 * 8;

	    blks[i >> 2] |= 0x80 << (str.length * 8 + i) % 4 * 8;

	    var l = str.length * 8;
	    blks[nblk * 16 - 2] = l & 0xFF;
	    blks[nblk * 16 - 2] |= (l >>> 8 & 0xFF) << 8;
	    blks[nblk * 16 - 2] |= (l >>> 16 & 0xFF) << 16;
	    blks[nblk * 16 - 2] |= (l >>> 24 & 0xFF) << 24;

	    return blks;
	}

	function rol(num, cnt) {
	    return num << cnt | num >>> 32 - cnt;
	}

	function cmn(q, a, b, x, s, t) {
	    return addme(rol(addme(addme(a, q), addme(x, t)), s), b);
	}

	function ff(a, b, c, d, x, s, t) {
	    return cmn(bitOR(bitAND(b, c), bitAND(~b, d)), a, b, x, s, t);
	}

	function gg(a, b, c, d, x, s, t) {
	    return cmn(bitOR(bitAND(b, d), bitAND(c, ~d)), a, b, x, s, t);
	}

	function hh(a, b, c, d, x, s, t) {
	    return cmn(bitXOR(bitXOR(b, c), d), a, b, x, s, t);
	}

	function ii(a, b, c, d, x, s, t) {
	    return cmn(bitXOR(c, bitOR(b, ~d)), a, b, x, s, t);
	}

/***/ },

/***/ 558:
/***/ function(module, exports) {

	"use strict";

	var id = Math.ceil(Math.random() * 10);

	module.exports = function () {
	    return ++id;
	};

/***/ },

/***/ 559:
/***/ function(module, exports) {

	"use strict";

	module.exports = function (value) {
	    return Object.prototype.toString.call(value).slice(8, -1);
	};

/***/ },

/***/ 560:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(146);
	var span = React.DOM.span;

	module.exports = React.createClass({
	    displayName: 'exports',

	    getDefaultProps: function getDefaultProps() {
	        return {
	            string: '',
	            highlight: ''
	        };
	    },
	    shouldComponentUpdate: function shouldComponentUpdate(p) {
	        return p.highlight !== this.props.highlight;
	    },
	    render: function render() {
	        var p = this.props;

	        if (!p.highlight || p.string.indexOf(p.highlight) === -1) {
	            return span(null, p.string);
	        }

	        return span(null, p.string.split(p.highlight).map(function (part, index) {
	            return span({ key: index }, index > 0 ? span({ className: 'json-inspector__hl' }, p.highlight) : null, part);
	        }));
	    }
	});

/***/ },

/***/ 561:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var debounce = __webpack_require__(562);
	var React = __webpack_require__(146);
	var input = React.DOM.input;

	var noop = __webpack_require__(564);

	module.exports = React.createClass({
	    displayName: 'exports',

	    getDefaultProps: function getDefaultProps() {
	        return {
	            timeout: 100,
	            onChange: noop
	        };
	    },
	    render: function render() {
	        return input({
	            className: 'json-inspector__search',
	            type: 'search',
	            placeholder: 'Search',
	            ref: 'query',
	            onChange: debounce(this.update, this.props.timeout)
	        });
	    },
	    update: function update() {
	        this.props.onChange(this.refs.query.value);
	    }
	});

/***/ },

/***/ 562:
/***/ function(module, exports, __webpack_require__) {

	
	/**
	 * Module dependencies.
	 */

	'use strict';

	var now = __webpack_require__(563);

	/**
	 * Returns a function, that, as long as it continues to be invoked, will not
	 * be triggered. The function will be called after it stops being called for
	 * N milliseconds. If `immediate` is passed, trigger the function on the
	 * leading edge, instead of the trailing.
	 *
	 * @source underscore.js
	 * @see http://unscriptable.com/2009/03/20/debouncing-javascript-methods/
	 * @param {Function} function to wrap
	 * @param {Number} timeout in ms (`100`)
	 * @param {Boolean} whether to execute at the beginning (`false`)
	 * @api public
	 */

	module.exports = function debounce(func, wait, immediate) {
	  var timeout, args, context, timestamp, result;
	  if (null == wait) wait = 100;

	  function later() {
	    var last = now() - timestamp;

	    if (last < wait && last > 0) {
	      timeout = setTimeout(later, wait - last);
	    } else {
	      timeout = null;
	      if (!immediate) {
	        result = func.apply(context, args);
	        if (!timeout) context = args = null;
	      }
	    }
	  };

	  return function debounced() {
	    context = this;
	    args = arguments;
	    timestamp = now();
	    var callNow = immediate && !timeout;
	    if (!timeout) timeout = setTimeout(later, wait);
	    if (callNow) {
	      result = func.apply(context, args);
	      context = args = null;
	    }

	    return result;
	  };
	};

/***/ },

/***/ 563:
/***/ function(module, exports) {

	"use strict";

	module.exports = Date.now || now;

	function now() {
	    return new Date().getTime();
	}

/***/ },

/***/ 564:
/***/ function(module, exports) {

	"use strict";

	module.exports = function () {};

/***/ },

/***/ 565:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var assign = __webpack_require__(566);
	var keys = Object.keys;

	var type = __webpack_require__(559);
	var isEmpty = __webpack_require__(567);

	module.exports = function (data, options) {
	    options || (options = {});
	    var cache = {};

	    return function (query) {
	        var subquery;

	        if (!cache[query]) {
	            for (var i = query.length - 1; i > 0; i -= 1) {
	                subquery = query.substr(0, i);

	                if (cache[subquery]) {
	                    cache[query] = find(cache[subquery], query, options);
	                    break;
	                }
	            }
	        }

	        if (!cache[query]) {
	            cache[query] = find(data, query, options);
	        }

	        return cache[query];
	    };
	};

	function find(data, query, options) {
	    return keys(data).reduce(function (acc, key) {
	        var value = data[key];
	        var matches;

	        if (isPrimitive(value)) {
	            if (contains(query, key, options) || contains(query, value, options)) {
	                acc[key] = value;
	            }
	        } else {
	            if (contains(query, key, options)) {
	                acc[key] = value;
	            } else {
	                matches = find(value, query, options);

	                if (!isEmpty(matches)) {
	                    assign(acc, pair(key, matches));
	                }
	            }
	        }

	        return acc;
	    }, {});
	}

	function contains(query, string, options) {
	    if (options.ignoreCase) {
	        query = String(query).toLowerCase();
	        return string && String(string).toLowerCase().indexOf(query) !== -1;
	    } else {
	        return string && String(string).indexOf(query) !== -1;
	    }
	}

	function isPrimitive(value) {
	    var t = type(value);
	    return t !== 'Object' && t !== 'Array';
	}

	function pair(key, value) {
	    var p = {};
	    p[key] = value;
	    return p;
	}

/***/ },

/***/ 566:
/***/ function(module, exports) {

	'use strict';

	function ToObject(val) {
		if (val == null) {
			throw new TypeError('Object.assign cannot be called with null or undefined');
		}

		return Object(val);
	}

	module.exports = Object.assign || function (target, source) {
		var from;
		var keys;
		var to = ToObject(target);

		for (var s = 1; s < arguments.length; s++) {
			from = arguments[s];
			keys = Object.keys(Object(from));

			for (var i = 0; i < keys.length; i++) {
				to[keys[i]] = from[keys[i]];
			}
		}

		return to;
	};

/***/ },

/***/ 567:
/***/ function(module, exports) {

	"use strict";

	module.exports = function (object) {
	    return Object.keys(object).length === 0;
	};

/***/ },

/***/ 568:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var type = __webpack_require__(559);

	var PATH_DELIMITER = '.';

	function lens(_x, _x2) {
	    var _again = true;

	    _function: while (_again) {
	        var data = _x,
	            path = _x2;
	        p = segment = t = undefined;
	        _again = false;

	        var p = path.split(PATH_DELIMITER);
	        var segment = p.shift();

	        if (!segment) {
	            return data;
	        }

	        var t = type(data);

	        if (t === 'Array' && data[integer(segment)]) {
	            _x = data[integer(segment)];
	            _x2 = p.join(PATH_DELIMITER);
	            _again = true;
	            continue _function;
	        } else if (t === 'Object' && data[segment]) {
	            _x = data[segment];
	            _x2 = p.join(PATH_DELIMITER);
	            _again = true;
	            continue _function;
	        }
	    }
	}

	function integer(string) {
	    return parseInt(string, 10);
	}

	module.exports = lens;

/***/ }

});