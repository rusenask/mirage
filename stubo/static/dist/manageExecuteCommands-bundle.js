webpackJsonp([2],[
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { 'default': obj }; }

	var _react = __webpack_require__(1);

	var _react2 = _interopRequireDefault(_react);

	var _reactBootstrap = __webpack_require__(157);

	var infoModal = $('#myModal');

	// component to create form for execute command files
	var ExecuteCmdsFile = _react2['default'].createClass({
	    displayName: "ExecuteCmdsFile",

	    getInitialState: function getInitialState() {
	        return {
	            disabled: true,
	            style: null,
	            placeholder: "/static/cmds/demo/first.commands",
	            submitUrl: "/manage/execute"
	        };
	    },

	    resetValidation: function resetValidation() {
	        this.setState({
	            disabled: true,
	            style: null
	        });
	    },

	    validationState: function validationState() {
	        var length = this.refs.input.getValue().length;
	        var style = 'danger';

	        if (length > 0) style = 'success';
	        //else if (length > 5) style = 'warning';

	        var disabled = style !== 'success';

	        return { style: style, disabled: disabled };
	    },

	    handleChange: function handleChange() {
	        this.setState(this.validationState());
	    },

	    handleSubmit: function handleSubmit(e) {
	        var val = this.refs.input.getValue();
	        //
	        e.preventDefault();
	        // make a POST call
	        var body = {
	            commandFile: val
	        };
	        $.ajax({
	            type: "POST",
	            dataType: "json",
	            url: this.state.submitUrl,
	            data: JSON.stringify(body),
	            success: function success(data) {
	                // unmounting current results
	                _react2['default'].unmountComponentAtNode(document.getElementById('CommandResults'));
	                // mounting results
	                _react2['default'].render(_react2['default'].createElement(CommandResultsComponent, { data: data }), document.getElementById("CommandResults"));
	            }
	        }).fail(function ($xhr) {
	            var data = $xhr.responseJSON;
	            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
	            infoModal.find('.modal-body').html(htmlData);
	            infoModal.modal('show');
	        });
	    },

	    render: function render() {
	        return _react2['default'].createElement(
	            'form',
	            { onSubmit: this.handleSubmit },
	            _react2['default'].createElement(_reactBootstrap.Input, { type: 'text', ref: 'input', name: 'cmdfile', placeholder: this.state.placeholder,

	                onChange: this.handleChange }),
	            _react2['default'].createElement(_reactBootstrap.ButtonInput, { type: 'reset', bsStyle: 'primary', bsSize: 'small', onClick: this.resetValidation }),
	            _react2['default'].createElement(_reactBootstrap.ButtonInput, { type: 'submit', value: 'Execute', bsStyle: this.state.style, bsSize: 'small',
	                disabled: this.state.disabled })
	        );
	    }
	});

	var ExecuteDirectCommands = _react2['default'].createClass({
	    displayName: "ExecuteDirectCommands",

	    getInitialState: function getInitialState() {
	        return {
	            disabled: true,
	            style: null,
	            submitUrl: "/manage/execute"
	        };
	    },

	    resetValidation: function resetValidation() {
	        this.setState({
	            disabled: true,
	            style: null
	        });
	    },

	    validationState: function validationState() {
	        var length = this.refs.input.getValue().length;
	        var style = 'danger';

	        if (length > 0) style = 'success';
	        //else if (length > 5) style = 'warning';

	        var disabled = style !== 'success';

	        return { style: style, disabled: disabled };
	    },

	    handleChange: function handleChange() {
	        this.setState(this.validationState());
	    },

	    handleSubmit: function handleSubmit(e) {

	        var val = this.refs.input.getValue();
	        //
	        e.preventDefault();
	        // make a POST call
	        var body = {
	            command: val
	        };
	        $.ajax({
	            type: "POST",
	            dataType: "json",
	            url: this.state.submitUrl,
	            data: JSON.stringify(body),
	            success: function success(data) {
	                // unmounting current results
	                _react2['default'].unmountComponentAtNode(document.getElementById('CommandResults'));
	                // mounting results
	                _react2['default'].render(_react2['default'].createElement(CommandResultsComponent, { data: data }), document.getElementById("CommandResults"));
	            }
	        }).fail(function ($xhr) {
	            var data = $xhr.responseJSON;
	            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
	            infoModal.find('.modal-body').html(htmlData);
	            infoModal.modal('show');
	        });
	    },

	    render: function render() {
	        return _react2['default'].createElement(
	            'form',
	            { onSubmit: this.handleSubmit },
	            _react2['default'].createElement(_reactBootstrap.Input, { type: 'textarea', ref: 'input', placeholder: 'delete/stubs?scenario=scenario_name1',
	                onChange: this.handleChange }),
	            _react2['default'].createElement(_reactBootstrap.ButtonInput, { type: 'reset', bsStyle: 'primary', bsSize: 'small', onClick: this.resetValidation }),
	            _react2['default'].createElement(_reactBootstrap.ButtonInput, { type: 'submit', value: 'Execute', bsStyle: this.state.style, bsSize: 'small',
	                disabled: this.state.disabled })
	        );
	    }
	});

	var ExecuteCommandsPanel = _react2['default'].createClass({
	    displayName: "ExecuteCommandsPanel",

	    render: function render() {

	        var ExecuteCommandsFile = _react2['default'].createElement(ExecuteCmdsFile, null);
	        var ExDirectCommands = _react2['default'].createElement(ExecuteDirectCommands, null);

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
	                                ' Execute Commands from file'
	                            )
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-body pad' },
	                            ExecuteCommandsFile
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
	                                ' Execute Commands directly'
	                            )
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-body pad' },
	                            ExDirectCommands
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

	// label wrapper
	var StatusCodeWrapper = _react2['default'].createClass({
	    displayName: "StatusCodeWrapper",

	    render: function render() {
	        var sc = this.props.data;

	        if (200 <= sc < 300) {
	            return _react2['default'].createElement(
	                _reactBootstrap.Label,
	                { bsStyle: 'success' },
	                sc
	            );
	        } else if (300 <= sc < 400) {
	            return _react2['default'].createElement(
	                _reactBootstrap.Label,
	                { bsStyle: 'warning' },
	                sc
	            );
	        } else {
	            return _react2['default'].createElement(
	                _reactBootstrap.Label,
	                { bsStyle: 'danger' },
	                sc
	            );
	        }
	    }
	});

	// displaying single list entry (name + download button)
	var ListItemWrapper = _react2['default'].createClass({
	    displayName: "ListItemWrapper",

	    render: function render() {
	        var statusCode = _react2['default'].createElement(StatusCodeWrapper, { data: this.props.data[1] });
	        return _react2['default'].createElement(
	            'li',
	            null,
	            _react2['default'].createElement(
	                'span',
	                null,
	                ' ',
	                this.props.data[0],
	                ' ',
	                statusCode
	            )
	        );
	    }
	});

	// this component get a list of tuples (those children lists contain api call path and status code)
	var CommandsComponent = _react2['default'].createClass({
	    displayName: "CommandsComponent",

	    getInitialState: function getInitialState() {
	        return {
	            "data": this.props.data
	        };
	    },

	    render: function render() {
	        return _react2['default'].createElement(
	            'ol',
	            null,
	            this.props.data.map(function (result) {
	                return _react2['default'].createElement(ListItemWrapper, { key: result[0], data: result });
	            })
	        );
	    }
	});

	// this component is only rendered when commands are executed either by "from file" or "directly"
	var CommandResultsComponent = _react2['default'].createClass({
	    displayName: "CommandResultsComponent",

	    getInitialState: function getInitialState() {
	        return {
	            results: this.props.data.data.executed_commands.commands,
	            disabled: false

	        };
	    },

	    // cleaning up results
	    handleClick: function handleClick() {
	        if (this.isMounted()) {
	            this.setState({
	                results: [],
	                disabled: true
	            });
	        }
	    },

	    render: function render() {

	        var CommandsResultList = _react2['default'].createElement(CommandsComponent, { data: this.state.results });

	        return _react2['default'].createElement(
	            _reactBootstrap.Grid,
	            { fluid: true },
	            _react2['default'].createElement(
	                _reactBootstrap.Row,
	                null,
	                _react2['default'].createElement(
	                    _reactBootstrap.Col,
	                    { md: 12 },
	                    _react2['default'].createElement(
	                        _reactBootstrap.Col,
	                        { className: 'box' },
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-header' },
	                            _react2['default'].createElement(
	                                'h3',
	                                { className: 'box-title' },
	                                ' Command execution results'
	                            )
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-body pad' },
	                            CommandsResultList
	                        ),
	                        _react2['default'].createElement(
	                            _reactBootstrap.Col,
	                            { className: 'box-footer clearfix' },
	                            _react2['default'].createElement(
	                                _reactBootstrap.Button,
	                                { bsStyle: 'primary', bsSize: 'small', onClick: this.handleClick,
	                                    disabled: this.state.disabled },
	                                'Clear'
	                            )
	                        )
	                    )
	                )
	            )
	        );
	    }

	});

	_react2['default'].render(_react2['default'].createElement(ExecuteCommandsPanel, null), document.getElementById("ExecuteCommands"));

/***/ }
]);