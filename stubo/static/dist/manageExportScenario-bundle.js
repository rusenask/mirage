webpackJsonp([3],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

	var _react = __webpack_require__(1);

	var _react2 = _interopRequireDefault(_react);

	var _reactBootstrap = __webpack_require__(157);

	function getUrlVars() {
	    var vars = [],
	        hash = undefined;
	    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	    var lng = hashes.length;
	    for (var i = 0; i < lng; i++) {
	        hash = hashes[i].split('=');
	        vars.push(hash[0]);
	        vars[hash[0]] = hash[1];
	    }
	    return vars;
	}

	// display scenario name near the header
	var ScenarioNameComponent = _react2['default'].createClass({
	    displayName: "ScenarioNameComponent",

	    render: function render() {
	        return _react2['default'].createElement(
	            'small',
	            null,
	            ' Exported scenario name: ',
	            this.props.data,
	            ' '
	        );
	    }
	});

	// displaying single list entry (name + download button)
	var ListItemWrapper = _react2['default'].createClass({
	    displayName: "ListItemWrapper",

	    render: function render() {
	        var tooltip = _react2['default'].createElement(
	            _reactBootstrap.Tooltip,
	            null,
	            'Download this file.'
	        );
	        return _react2['default'].createElement(
	            'li',
	            null,
	            _react2['default'].createElement(
	                _reactBootstrap.OverlayTrigger,
	                { placement: 'right', overlay: tooltip },
	                _react2['default'].createElement(
	                    'a',
	                    { className: 'btn btn-xs btn-info', href: this.props.data[1] },
	                    _react2['default'].createElement('i', { className: 'fa fa-fw fa-download' })
	                )
	            ),
	            _react2['default'].createElement(
	                'span',
	                null,
	                ' ',
	                this.props.data[0],
	                ' '
	            )
	        );
	    }
	});

	// this component get a list of lists (those children lists contain name and href to resource)
	var LinksComponent = _react2['default'].createClass({
	    displayName: "LinksComponent",

	    getInitialState: function getInitialState() {
	        return {
	            "data": this.props.data
	        };
	    },

	    render: function render() {
	        return _react2['default'].createElement(
	            'ul',
	            null,
	            this.props.data.map(function (result) {
	                return _react2['default'].createElement(ListItemWrapper, { key: result[0], data: result });
	            })
	        );
	    }
	});

	// creates two boxes with links and also provides a scenario name for the template
	var ExportInformation = _react2['default'].createClass({
	    displayName: "ExportInformation",

	    getInitialState: function getInitialState() {
	        return {
	            "results": [],
	            "href": getUrlVars()["scenario"] || null,
	            "mounted": false
	        };
	    },

	    componentWillMount: function componentWillMount() {},

	    componentDidMount: function componentDidMount() {
	        var infoModal = $('#myModal');
	        // creating body for export POST request
	        var body = {
	            'export': null
	        };

	        var that = this;
	        // creating full url + removing hashes (can be there due to enabling/disabling check boxes)
	        var url = (this.state.href + '/action').replace("#", "");

	        $.ajax({
	            type: "POST",
	            dataType: "json",
	            url: url,
	            data: JSON.stringify(body),
	            success: function success(data) {
	                if (that.isMounted()) {

	                    that.setState({
	                        results: data,
	                        mounted: true
	                    });

	                    // rendering name
	                    _react2['default'].render(_react2['default'].createElement(ScenarioNameComponent, { key: data.data.scenario, data: data.data.scenario }), document.getElementById("scenarioName"));
	                }
	            }
	        }).fail(function ($xhr) {
	            var data = $xhr.responseJSON;
	            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
	            infoModal.find('.modal-body').html(htmlData);
	            infoModal.modal('show');
	        });
	    },

	    render: function render() {

	        var YamlLinks = undefined,
	            CommandLinks = null;

	        // getting yaml links
	        if (this.state.mounted) {
	            YamlLinks = _react2['default'].createElement(LinksComponent, { data: this.state.results.data.yaml_links });
	        } else {
	            YamlLinks = _react2['default'].createElement(
	                'div',
	                null,
	                ' Loading.. '
	            );
	        }
	        // getting command links
	        if (this.state.mounted) {
	            CommandLinks = _react2['default'].createElement(LinksComponent, { data: this.state.results.data.command_links });
	        } else {
	            CommandLinks = _react2['default'].createElement(
	                'div',
	                null,
	                ' Loading.. '
	            );
	        }

	        // constructing grid
	        var gridInstance = _react2['default'].createElement(
	            _reactBootstrap.Grid,
	            { fluid: true },
	            _react2['default'].createElement(
	                _reactBootstrap.Row,
	                null,
	                _react2['default'].createElement(
	                    _reactBootstrap.Col,
	                    { md: 6 },
	                    _react2['default'].createElement(
	                        _reactBootstrap.Col,
	                        { className: 'box' },
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-header' },
	                            _react2['default'].createElement(
	                                'h3',
	                                { className: 'box-title' },
	                                ' Exported Command files'
	                            )
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-body pad' },
	                            CommandLinks
	                        )
	                    )
	                ),
	                _react2['default'].createElement(
	                    _reactBootstrap.Col,
	                    { md: 6 },
	                    _react2['default'].createElement(
	                        _reactBootstrap.Col,
	                        { className: 'box' },
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-header' },
	                            _react2['default'].createElement(
	                                'h3',
	                                { className: 'box-title' },
	                                ' Exported YAML files'
	                            )
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-body pad' },
	                            YamlLinks
	                        )
	                    )
	                )
	            )
	        );
	        // rendering the grid
	        return _react2['default'].createElement(
	            'div',
	            null,
	            ' ',
	            gridInstance,
	            ' '
	        );
	    }

	});

	_react2['default'].render(_react2['default'].createElement(ExportInformation, null), document.getElementById("app"));

/***/ }
]);