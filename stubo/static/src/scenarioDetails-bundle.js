webpackJsonp([8],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	/**
	 * Created by karolisrusenas on 22/09/15.
	 */

	'use strict';

	var React = __webpack_require__(1);

	var Inspector = __webpack_require__(544);

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

/***/ 544:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(1);
	var D = React.DOM;

	var Leaf = __webpack_require__(545);
	var leaf = React.createFactory(Leaf);
	var SearchBar = __webpack_require__(549);
	var searchBar = React.createFactory(SearchBar);

	var filterer = __webpack_require__(553);
	var isEmpty = __webpack_require__(555);
	var lens = __webpack_require__(556);
	var noop = __webpack_require__(552);

	module.exports = React.createClass({
	    displayName: 'exports',

	    propTypes: {
	        data: React.PropTypes.oneOfType([React.PropTypes.object.isRequired, React.PropTypes.array.isRequired]),
	        // For now it expects a factory function, not element.
	        search: React.PropTypes.func,
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

/***/ 545:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(1);
	var D = React.DOM;

	var uid = __webpack_require__(546);
	var type = __webpack_require__(547);

	var Highlighter = __webpack_require__(548);
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
	        return key + ':' + value;
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

/***/ 546:
/***/ function(module, exports) {

	"use strict";

	var id = Math.ceil(Math.random() * 10);

	module.exports = function () {
	    return ++id;
	};

/***/ },

/***/ 547:
/***/ function(module, exports) {

	"use strict";

	module.exports = function (value) {
	    return Object.prototype.toString.call(value).slice(8, -1);
	};

/***/ },

/***/ 548:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var React = __webpack_require__(1);
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

/***/ 549:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var debounce = __webpack_require__(550);
	var React = __webpack_require__(1);
	var input = React.DOM.input;

	var noop = __webpack_require__(552);

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
	        this.props.onChange(this.refs.query.getDOMNode().value);
	    }
	});

/***/ },

/***/ 550:
/***/ function(module, exports, __webpack_require__) {

	
	/**
	 * Module dependencies.
	 */

	'use strict';

	var now = __webpack_require__(551);

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

/***/ 551:
/***/ function(module, exports) {

	"use strict";

	module.exports = Date.now || now;

	function now() {
	    return new Date().getTime();
	}

/***/ },

/***/ 552:
/***/ function(module, exports) {

	"use strict";

	module.exports = function () {};

/***/ },

/***/ 553:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var assign = __webpack_require__(554);
	var keys = Object.keys;

	var type = __webpack_require__(547);
	var isEmpty = __webpack_require__(555);

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

/***/ 554:
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

/***/ 555:
/***/ function(module, exports) {

	"use strict";

	module.exports = function (object) {
	    return Object.keys(object).length === 0;
	};

/***/ },

/***/ 556:
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var type = __webpack_require__(547);

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