import React from 'react';
//import ReactDOM from 'react-dom';
import cookie from 'react-cookie';
import Griddle from 'griddle-react';
import { Button, Tooltip, OverlayTrigger, Grid, Row, Col, Modal, Input, ButtonInput, Alert } from 'react-bootstrap';
import Dropzone from 'react-dropzone';
import request from 'superagent';

function ExecuteRequest(href, body) {
    var infoModal = $('#myModal');

    $.ajax({
        type: "POST",
        dataType: "json",
        url: href,
        data: JSON.stringify(body),
        success (data) {
            var info_msg = JSON.stringify(data.data, null, 2);
            var htmlData = '<ul><li>Message: ' + info_msg + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
            return false;
        }
    }).fail(function ($xhr) {
        var data = $xhr.responseJSON;
        var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
        infoModal.find('.modal-body').html(htmlData);
        infoModal.modal('show');
        return false;
    });
}

// we are getting session data nested in the array, so we bring it forward
function reformatJSON(initialData) {

    var newScenariosList = [];
    for (var key in initialData) {
        if (initialData.hasOwnProperty(key)) {
            // console.log(key + " -> " + initialData[key].name);
            var singleObj = {};
            singleObj['name'] = initialData[key].name;
            singleObj['ref'] = initialData[key].scenarioRef;
            singleObj['space_used_kb'] = initialData[key].space_used_kb;
            singleObj['stub_count'] = initialData[key].stub_count;
            singleObj['recorded'] = initialData[key].recorded;
            // creating children array

            var sessions = [];

            initialData[key].sessions.forEach(function (entry, index) {
                // adding session information to parent object
                if (index == 0) {
                    singleObj['session'] = entry.name;
                    singleObj['status'] = entry.status;
                    singleObj['loaded'] = entry.loaded;
                    singleObj['last_used'] = entry.last_used;

                } else {
                    var childrenObj = {};
                    childrenObj['name'] = initialData[key].name;
                    childrenObj['session'] = entry.name;
                    childrenObj['status'] = entry.status;
                    childrenObj['loaded'] = entry.loaded;
                    childrenObj['last_used'] = entry.last_used;
                    childrenObj['ref'] = initialData[key].scenarioRef;
                    childrenObj['space_used_kb'] = initialData[key].space_used_kb;
                    childrenObj['stub_count'] = initialData[key].stub_count;
                    childrenObj['recorded'] = initialData[key].recorded;
                    // adding object to children array
                    sessions.push(childrenObj)
                }
            });
            singleObj['sessions'] = sessions;

            newScenariosList.push(singleObj);
        }
    }
    return newScenariosList
}

var LinkComponent = React.createClass({
    displayName: "LinkComponent",

    render () {
        var url = "/manage/scenarios/details?scenario=" + this.props.rowData.ref;
        return <a href={url}><span style={{overflow: 'hidden', textOverflow: 'ellipsis'}}> {this.props.data}</span></a>

    }
});

var ExportButton = React.createClass({
    displayName: "ExportButton",
    render () {
        const tooltip = (
            <Tooltip>Export scenario.</Tooltip>
        );

        var url = '/manage/scenarios/export?scenario=' + this.props.data.ref;

        return (
            <OverlayTrigger placement='left' overlay={tooltip}>
                <a href={url} className="btn btn-sm btn-info">
                            <span
                                className="glyphicon glyphicon-cloud-download"></span>
                </a>
            </OverlayTrigger>
        );
    }
});

// end session button
var EndSessionsButton = React.createClass({
    displayName: "EndSessionsButton",

    getInitialState () {
        return {
            ref: this.props.data.ref,
            status: false
        };
    },
    handleClick (event) {
        this.setState({status: !this.state.status});

        var href = this.state.ref + "/action";

        var body = {
            end: 'sessions'
        };
        ExecuteRequest(href, body);

    },
    render () {


        const EndSessionsTooltip = (
            <Tooltip>End all active sessions for this scenario.</Tooltip>
        );
        // checking whether scenario has a session and whether it is dormant or not
        if (this.props.data.session != null && this.props.data.status != 'dormant') {
            return (
                <OverlayTrigger placement='left' overlay={EndSessionsTooltip}>

                    <Button onClick={this.handleClick} bsStyle='warning' bsSize='small'>
                        <span className="glyphicon glyphicon-stop"></span>
                    </Button>
                </OverlayTrigger>
            );
        }
        // session status is either dormant or there are no sessions, disabling button
        else {
            return (
                <Button onClick={this.handleClick} bsStyle='warning' bsSize='small' disabled>
                    <span className="glyphicon glyphicon-stop"></span>
                </Button>

            );
        }
    }
});

// remove scenario action button
var RemoveButton = React.createClass({
    displayName: "RemoveButton",

    getInitialState () {
        // getting scenario ref
        return {
            ref: this.props.data.ref,
            name: this.props.data.name,
            session: this.props.data.status,
            showModal: false
        };
    },

    close() {
        this.setState({showModal: false});
    },

    open() {
        this.setState({showModal: true});
    },

    handleClick (event) {

        var infoModal = $('#myModal');
        var scenarioName = this.state.name;

        $.ajax({
            type: "DELETE",
            url: this.state.ref,
            success () {
                var htmlData = '<ul><li> Scenario (' + scenarioName + ') removed successfuly. </li></ul>';
                infoModal.find('.modal-body').html(htmlData);
                infoModal.modal('show');
                return false;
            }
        }).fail(function ($xhr) {
            var response = $xhr;
            var htmlData = '<ul><li> Status code: ' + response.status + '. Error: ' + response.responseText + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
            return false;
        });

    },
    render () {
        const RemoveTooltip = (
            <Tooltip>Remove scenario.</Tooltip>
        );
        if (this.state.session == "playback" || this.state.session == "record") {
            return (
                <Button bsStyle='danger' bsSize='small' disabled>
                    <span className="glyphicon glyphicon-remove-sign"></span>
                </Button>
            )
        } else{
            return (
                <OverlayTrigger placement='left' overlay={RemoveTooltip}>
                    <Button onClick={this.handleClick} bsStyle='danger' bsSize='small'>
                        <span className="glyphicon glyphicon-remove-sign"></span>
                    </Button>
                </OverlayTrigger>
            );
        }


    }
});


// BeginSessionButton
var BeginSessionButton = React.createClass({
    displayName: "BeginSessionButton",

    getInitialState () {
        //console.log(this.props.data.ref);
        return {
            ref: this.props.data.ref,
            data: this.props.data,
            mode: null,
            disabled: false
        };
    },

    handleClick (event) {
        this.setState({disabled: !this.state.disabled});

        let href = this.state.ref + "/action";

        var body = {
            begin: null,
            session: this.state.data.session,
            mode: this.state.mode
        };
        ExecuteRequest(href, body);

    },
    render () {

        // getting mode, scenarios that have at least 1 stub - can't enter record mode again, only playback is available
        if (this.state.data.stub_count > 0) {
            this.state.mode = "playback"
        } else {
            this.state.mode = "record"
        }

        let sessiontooltip = "";
        let glyphicon = "";
        let style = "";

        if (this.state.mode == "record") {
            glyphicon = "glyphicon glyphicon-record";
            style = "info";
            sessiontooltip = (
                <Tooltip>Start recording</Tooltip>
            );
        } else {
            glyphicon = "glyphicon glyphicon-play-circle";
            style = "success";
            sessiontooltip = (
                <Tooltip>Start playback</Tooltip>
            );
        }


        return (
            <OverlayTrigger placement='left' overlay={sessiontooltip}>

                <Button onClick={this.handleClick} bsStyle={style} bsSize='small' disabled={this.state.disabled}>
                    <span className={glyphicon}></span>
                </Button>
            </OverlayTrigger>
        );


    }
});


var ActionComponent = React.createClass({
    displayName: "ActionComponent",

    render() {

        // default button - end all sessions
        let sessionControll = <EndSessionsButton data={this.props.rowData}/>;
        //
        if (this.props.rowData.status == "dormant") {
            sessionControll = <BeginSessionButton data={this.props.rowData}/>;
        }

        // rendering action buttons
        return (<div className="btn-group">
                <ExportButton data={this.props.rowData}/>
                <RemoveButton data={this.props.rowData}/>
                {sessionControll}
            </div>
        )
    }
});

var StatusLabelComponent = React.createClass({
    displayName: "StatusLabelComponent",

    getInitialState () {
        // getting scenario name and hostname
        return {
            labelClass: 'label label-default'
        };
    },

    render () {
        switch (this.props.rowData.status) {
            case undefined:
                this.state.labelClass = '';
                break;
            case 'dormant':
                break;
            case 'playback':
                this.state.labelClass = 'label label-success';
                break;
            case 'record':
                this.state.labelClass = 'label label-warning';
                break;
        }

        var sessionStatusTooltip = (
            <Tooltip>Current session mode is {this.props.rowData.status}. Check out documentation for more
                information.</Tooltip>
        );

        // checking whether row has children object, removing children objects from children because they cause
        // to create a whole separate grid inside a row
        if (this.props.rowData.sessions != undefined) {
            var sessions = this.props.rowData.sessions.length;
            if (sessions > 1) {
                // adding session count number to the label
                var sessionCounterTooltip = (
                    <Tooltip>There are {sessions} sessions in this scenario. Access scenario details to get
                        more information.</Tooltip>
                );
                return (

                    <div>
                        <OverlayTrigger placement='left' overlay={sessionStatusTooltip}>
                            <span className={this.state.labelClass}> {this.props.rowData.status}</span>
                        </OverlayTrigger>
                        &nbsp;
                        <OverlayTrigger placement='left' overlay={sessionCounterTooltip}>
                            <span className="label label-primary">{sessions}</span>
                        </OverlayTrigger>
                    </div>

                )

            } else {
                // standard row output for each scenario
                return ( <OverlayTrigger placement='left' overlay={sessionStatusTooltip}>
                        <span className={this.state.labelClass}> {this.props.rowData.status}</span>
                    </OverlayTrigger>
                )
            }
        } else {
            // children session status label
            return (<OverlayTrigger placement='left' overlay={sessionStatusTooltip}>
                <span className={this.state.labelClass}> {this.props.rowData.status}</span>
            </OverlayTrigger>)
        }


    }
});

var columnMeta = [
    {
        "columnName": "name",
        "displayName": "Scenario",
        "order": 1,
        "locked": false,
        "visible": true,
        "customComponent": LinkComponent
    },
    {
        "columnName": "actions",
        "displayName": "Actions",
        "locked": false,
        "visible": true,
        "customComponent": ActionComponent
    },
    {
        "columnName": "status",
        "displayName": "Status",
        "locked": false,
        "visible": true,
        "customComponent": StatusLabelComponent
    }

];

function updateTable(component) {

    var href = '';
    if (cookie.load('stubo.all-hosts') || false) {
        // amending query argument to get all hosts
        href = '/api/v2/scenarios/detail?all-hosts=true'
    } else {
        href = '/api/v2/scenarios/detail?all-hosts=false'
    }

    $.get(href, function (result) {
        var newList = reformatJSON(result.data);
        if (component.isMounted()) {
            component.setState({
                results: newList
            });
        }
    });
}

var ExternalScenarios = React.createClass({
    displayName: "ExternalScenarios",
    getInitialState () {
        var initial = {
            "results": [],
            "resultsPerPage": 50
        };

        return initial;
    },
    //general lifecycle methods
    componentWillMount () {
    },
    componentDidMount () {
        // getting scenarios
        updateTable(this);

        // subscribing to modal close event
        $('#myModal').on('hidden.bs.modal', function () {
            updateTable(this);
        }.bind(this));
    },

    //what page is currently viewed
    setPage (index) {
    },
    //this will handle how the data is sorted
    sortData (sort, sortAscending, data) {
    },
    //this changes whether data is sorted in ascending or descending order
    changeSort (sort, sortAscending) {
    },
    //this method handles the filtering of the data
    setFilter (filter) {
    },
    //this method handles determining the page size
    setPageSize (size) {
    },


    render () {
        const gridInstance = (
            <Grid fluid={true}>
                <Row>
                    <div className="pull-right">
                        <CreateScenarioBtn parent={this}/>
                        &nbsp;
                        <ImportScenarioForm parent={this}/>
                    </div>
                </Row>

                <Row>
                    <hr/>
                </Row>


                <Row>
                    <Griddle results={this.state.results}
                             useGriddleStyles={true}
                             showFilter={true} showSettings={true}
                             resultsPerPage={this.state.resultsPerPage}
                             columnMetadata={columnMeta}
                             columns={["name", "session", "status", "loaded", "last_used", "space_used_kb", "stub_count", "recorded", "actions"]}
                        />
                </Row>

            </Grid>
        );


        return gridInstance
    }
});

function BeginSession(that, scenario, session, mode) {
    let sessionPayload = {
        "begin": null,
        "session": session,
        "mode": mode
    };

    // making ajax call
    $.ajax({
        type: "POST",
        dataType: "json",
        data: JSON.stringify(sessionPayload),
        url: "/api/v2/scenarios/objects/" + scenario + "/action",
        success () {
            if (that.isMounted()) {
                that.setState({
                    message: "Session for scenario '" + scenario + "' started successfully!",
                    alertVisible: true,
                    alertStyle: "success"
                });
            }
        }
    }).fail(function ($xhr) {
        let data = jQuery.parseJSON($xhr.responseText);
        if (that.isMounted()) {
            that.setState({
                message: "Could not begin session. Error: " + data.error.message,
                alertVisible: true,
                alertStyle: "danger"
            });
        }
    });
}


let CreateScenarioBtn = React.createClass({
    getInitialState() {
        return {
            disabled: true,
            style: null,
            sessionInputDisabled: true,
            showModal: false,
            message: "",
            alertVisible: false,
            alertStyle: "danger",
            parent: this.props.parent
        }
    },

    close() {
        this.setState({showModal: false});
    },

    open() {
        this.setState({showModal: true});
    },

    validationState() {
        let length = this.refs.scenarioName.getValue().length;
        let sessionLength = this.refs.sessionName.getValue().length;

        let style = 'danger';

        if (this.state.sessionInputDisabled == false) {
            if (length > 0 && sessionLength > 0) {
                style = 'success'
            }
        } else {
            if (length > 0) {
                style = 'success'
            }
        }

        let disabled = style !== 'success';


        return {style, disabled};
    },

    handleChange()
    {
        this.setState(this.validationState());
    },

    handleCheckbox()
    {
        // inverting checkbox state
        this.state.sessionInputDisabled = !this.state.sessionInputDisabled;

        // doing validation
        this.setState(this.validationState());
    },


    handleSubmit(e)
    {
        e.preventDefault();

        let scenarioName = this.refs.scenarioName.getValue();

        let payload = {
            "scenario": scenarioName
        };

        let that = this;

        $.ajax({
            type: "PUT",
            dataType: "json",
            data: JSON.stringify(payload),
            url: "/api/v2/scenarios",
            success (data) {
                if (that.isMounted()) {
                    that.setState({
                        message: "Scenario '" + scenarioName + "' created successfully!",
                        alertVisible: true,
                        alertStyle: "success"
                    });
                }
                // session input is expected if that.state.sessionInputDisabled is enabled
                if (that.state.sessionInputDisabled == false) {
                    let sessionName = that.refs.sessionName.getValue();
                    BeginSession(that, scenarioName, sessionName, "record")
                }
                updateTable(that.state.parent);

            }
        }).fail(function ($xhr) {
            if (that.isMounted()) {
                that.setState({
                    message: "Could not create scenario. Error: " + $xhr.statusText,
                    alertVisible: true,
                    alertStyle: "danger"
                });
            }
        });
    },

    handleAlertDismiss() {
        this.setState({alertVisible: false});
    },

    render() {

        let createForm = (
            <div>
                <form onSubmit={this.handleSubmit}>
                    <Input type="text" ref="scenarioName" label="Scenario name"
                           placeholder="scenario-0"
                           onChange={this.handleChange}/>
                    <Input type="checkbox" ref="sessionCheckbox"
                           label="Start session in record mode after scenario is created"
                           onChange={this.handleCheckbox}/>

                    <Input type="text" ref="sessionName" label="Session name"
                           placeholder="session-0"
                           disabled={this.state.sessionInputDisabled}
                           onChange={this.handleChange}/>

                    <ButtonInput type="submit" value="Submit"
                                 bsStyle={this.state.style} bsSize="small"
                                 disabled={this.state.disabled}/>
                </form>
            </div>
        );

        // alert style to display messages
        let alert = (<p></p>);
        if (this.state.alertVisible) {
            alert = (
                <Alert bsStyle={this.state.alertStyle} dismissAfter={10000} onDismiss={this.handleAlertDismiss}>
                    <p>{this.state.message}</p>
                </Alert>
            );
        }
        return (
            <span>
                <Button pullRigh={true}
                        onClick={this.open}
                        bsStyle="primary">
                    <span className="glyphicon glyphicon-plus" aria-hidden="true"></span> Add new scenario
                </Button>

                <Modal show={this.state.showModal} onHide={this.close}
                       bsSize="medium">
                    <Modal.Header closeButton>
                        <Modal.Title>Add new scenario</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {alert}
                        {createForm}
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.close}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </span>
        );
    }
});

let ImportScenarioForm = React.createClass({
    getInitialState() {
        return {
            disabled: true,
            showModal: false,
            parent: this.props.parent
        }
    },

    close() {
        this.setState({showModal: false});
    },

    open() {
        this.setState({showModal: true});
    },

    handleAlertDismiss() {
        this.setState({alertVisible: false});
    },

    render() {

        return (
            <span>
                <Button pullRigh={true}
                        onClick={this.open}
                        bsStyle="success">
                    <span className="glyphicon glyphicon-upload" aria-hidden="true"></span> Import Scenario
                </Button>

                <Modal show={this.state.showModal} onHide={this.close}
                       bsSize="small">
                    <Modal.Header closeButton>
                        <Modal.Title>Import Scenario</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>

                        <DropzoneComponent grid={this.state.parent} parent={this}/>

                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.close}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </span>
        );
    }
});

let DropzoneComponent = React.createClass({

    getInitialState: function () {
        return {
            files: [],
            grid: this.props.grid,
            parent: this.props.parent
        };
    },

    callback() {
        console.log("callback here");
        updateTable(this.state.grid);
        // dismiss modal
        console.log("grid updated, dismissing modal");
        this.state.parent.close();
    },

    onDrop: function (files) {
        this.setState({
            files: files
        });


        var req = request.post('/api/v2/scenarios/upload');
        files.forEach((file)=> {

            req.attach(file.name, file, file.name);
        });
        req.end(this.callback);
    },

    onOpenClick: function () {
        this.refs.dropzone.open();
    },


    render: function () {
        return (
            <div>
                <Dropzone ref="dropzone" onDrop={this.onDrop}>
                    <div> Drop files here, or click to select files to upload.</div>
                </Dropzone>
                {this.state.files.length > 0 ? <div>
                    <h2>Uploading {this.state.files.length} files...</h2>

                    <div>{this.state.files.map((file) => <img src={file.preview}/>)}</div>
                </div> : null}
            </div>
        );
    }
});

React.render(
    <ExternalScenarios />,
    document.getElementById("app")
);