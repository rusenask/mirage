import React from 'react'

import { Grid, Row, Col, OverlayTrigger, Tooltip, Input, ButtonInput, Label, Button} from 'react-bootstrap'

let infoModal = $('#myModal');

// component to create form for execute command files
const ExecuteCmdsFile = React.createClass({
    displayName: "ExecuteCmdsFile",

    getInitialState() {
        return {
            disabled: true,
            style: null,
            placeholder: "/static/cmds/demo/first.commands",
            submitUrl: "/manage/execute"
        };
    },

    resetValidation() {
        this.setState({
            disabled: true,
            style: null
        });
    },

    validationState() {
        let length = this.refs.input.getValue().length;
        let style = 'danger';

        if (length > 0) style = 'success';
        //else if (length > 5) style = 'warning';

        let disabled = style !== 'success';

        return {style, disabled};
    },

    handleChange() {
        this.setState(this.validationState());
    },

    handleSubmit(e) {
        let val = this.refs.input.getValue();
        //
        e.preventDefault();
        // make a POST call
        let body = {
            commandFile: val
        };
        $.ajax({
            type: "POST",
            dataType: "json",
            url: this.state.submitUrl,
            data: JSON.stringify(body),
            success: function (data) {
                // unmounting current results
                React.unmountComponentAtNode(document.getElementById('CommandResults'));
                // mounting results
                React.render(<CommandResultsComponent data={data}/>, document.getElementById("CommandResults"))
            }
        }).fail(function ($xhr) {
            var data = $xhr.responseJSON;
            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
        });
    },

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <Input type="text" ref="input" name="cmdfile" placeholder={this.state.placeholder}

                       onChange={this.handleChange}/>
                <ButtonInput type="reset" bsStyle="primary" bsSize="small" onClick={this.resetValidation}/>
                <ButtonInput type="submit" value="Execute" bsStyle={this.state.style} bsSize="small"
                             disabled={this.state.disabled}/>
            </form>
        );
    }
});

const ExecuteDirectCommands = React.createClass({
    displayName: "ExecuteDirectCommands",

    getInitialState() {
        return {
            disabled: true,
            style: null,
            submitUrl: "/manage/execute"
        };
    },

    resetValidation() {
        this.setState({
            disabled: true,
            style: null
        });
    },

    validationState() {
        let length = this.refs.input.getValue().length;
        let style = 'danger';

        if (length > 0) style = 'success';
        //else if (length > 5) style = 'warning';

        let disabled = style !== 'success';

        return {style, disabled};
    },

    handleChange() {
        this.setState(this.validationState());
    },

    handleSubmit(e) {

        let val = this.refs.input.getValue();
        //
        e.preventDefault();
        // make a POST call
        let body = {
            command: val
        };
        $.ajax({
            type: "POST",
            dataType: "json",
            url: this.state.submitUrl,
            data: JSON.stringify(body),
            success: function (data) {
                // unmounting current results
                React.unmountComponentAtNode(document.getElementById('CommandResults'));
                // mounting results
                React.render(<CommandResultsComponent data={data}/>, document.getElementById("CommandResults"))
            }
        }).fail(function ($xhr) {
            var data = $xhr.responseJSON;
            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
        });
    },

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <Input type="textarea" ref="input" placeholder="delete/stubs?scenario=scenario_name1"
                       onChange={this.handleChange}/>
                <ButtonInput type="reset" bsStyle="primary" bsSize="small" onClick={this.resetValidation}/>
                <ButtonInput type="submit" value="Execute" bsStyle={this.state.style} bsSize="small"
                             disabled={this.state.disabled}/>
            </form>
        );
    }
});


let ExecuteCommandsPanel = React.createClass({
    displayName: "ExecuteCommandsPanel",

    render: function () {

        let ExecuteCommandsFile = <ExecuteCmdsFile />;
        let ExDirectCommands = <ExecuteDirectCommands />;

        // constructing grid
        const gridInstance = (
            <Grid fluid={true}>
                <Row>
                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Execute Commands from file</h3>
                            </Col>

                            <Col className="box-body pad">
                                {ExecuteCommandsFile}
                            </Col>
                        </Col>
                    </Col>

                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Execute Commands directly</h3>
                            </Col>

                            <Col className="box-body pad">
                                {ExDirectCommands}
                            </Col>
                        </Col>
                    </Col>

                </Row>
            </Grid>
        );
        // rendering the grid
        return (
            <div> {gridInstance} </div>
        )
    }

});

// label wrapper
let StatusCodeWrapper = React.createClass({
    displayName: "StatusCodeWrapper",

    render() {
        let sc = this.props.data;

        if (200 <= sc < 300) {
            return <Label bsStyle="success">{sc}</Label>
        } else if (300 <= sc < 400) {
            return <Label bsStyle="warning">{sc}</Label>
        } else {
            return <Label bsStyle="danger">{sc}</Label>
        }
    }
});

// displaying single list entry (name + download button)
let ListItemWrapper = React.createClass({
    displayName: "ListItemWrapper",

    render: function () {
        let statusCode = <StatusCodeWrapper data={this.props.data[1]}/>;
        return ( <li>
                <span> {this.props.data[0]} {statusCode}</span>
            </li>
        )
    }
});

// this component get a list of tuples (those children lists contain api call path and status code)
let CommandsComponent = React.createClass({
    displayName: "CommandsComponent",

    getInitialState: function () {
        return {
            "data": this.props.data
        }
    },

    render: function () {
        return (
            <ol>
                {this.props.data.map(function (result) {
                    return <ListItemWrapper key={result[0]} data={result}/>;
                })}
            </ol>
        )
    }
});

// this component is only rendered when commands are executed either by "from file" or "directly"
let CommandResultsComponent = React.createClass({
    displayName: "CommandResultsComponent",

    getInitialState() {
        return {
            results: this.props.data.data.executed_commands.commands,
            disabled: false

        }
    },

    // cleaning up results
    handleClick() {
        if (this.isMounted()) {
            this.setState({
                results: [],
                disabled: true
            });
        }
    },

    render() {

        let CommandsResultList = <CommandsComponent data={this.state.results}/>;

        return (
            <Grid fluid={true}>
                <Row>
                    <Col md={12}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Command execution results</h3>
                            </Col>

                            <Col className="box-body pad">
                                {CommandsResultList}
                            </Col>

                            <Col className="box-footer clearfix">
                                <Button bsStyle="primary" bsSize="small" onClick={this.handleClick}
                                        disabled={this.state.disabled}>
                                    Clear
                                </Button>
                            </Col>
                        </Col>
                    </Col>
                </Row>
            </Grid>
        )
    }

});


React.render(<ExecuteCommandsPanel />, document.getElementById("ExecuteCommands"));