var React = require('../node_modules/react');
var cookie = require('react-cookie');
var Griddle = require('../node_modules/griddle-react');
var Tooltip = require('../node_modules/react-bootstrap').Tooltip;
var OverlayTrigger = require('../node_modules/react-bootstrap').OverlayTrigger;
var Button = require('../node_modules/react-bootstrap').Button;


function ExecuteRequest(href, body) {
    var infoModal = $('#myModal');

    $.ajax({
        type: "POST",
        dataType: "json",
        url: href,
        data: JSON.stringify(body),
        success: function (data) {
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

    render: function () {
        var url = "/manage/scenarios/details?scenario=" + this.props.rowData.ref;
        return <a href={url}><span style={{overflow: 'hidden', textOverflow: 'ellipsis'}}> {this.props.data}</span></a>

    }
});

var ExportButton = React.createClass({
    displayName: "ExportButton",
    render: function () {
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

    getInitialState: function () {
        return {
            ref: this.props.data.ref,
            status: false
        };
    },
    handleClick: function (event) {
        this.setState({status: !this.state.status});

        var href = this.state.ref + "/action";

        var body = {
            end: 'sessions'
        };
        ExecuteRequest(href, body);

    },
    render: function () {


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

    getInitialState: function () {
        // getting scenario ref
        return {
            ref: this.props.data.ref,
            name: this.props.data.name
        };
    },
    handleClick: function (event) {

        var infoModal = $('#myModal');
        var scenarioName = this.state.name;

        $.ajax({
            type: "DELETE",
            url: this.state.ref,
            success: function () {
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
    render: function () {
        const RemoveTooltip = (
            <Tooltip>Remove scenario.</Tooltip>
        );
        return (
            <OverlayTrigger placement='left' overlay={RemoveTooltip}>
                <Button onClick={this.handleClick} bsStyle='danger' bsSize='small'>
                    <span className="glyphicon glyphicon-remove-sign"></span>
                </Button>
            </OverlayTrigger>
        );
    }
});

var ActionComponent = React.createClass({
    displayName: "ActionComponent",

    render: function () {
        // rendering action buttons
        return (<div className="btn-group">
                <ExportButton data={this.props.rowData}/>
                <RemoveButton data={this.props.rowData}/>
                <EndSessionsButton data={this.props.rowData}/>
            </div>
        )
    }
});

var StatusLabelComponent = React.createClass({
    displayName: "StatusLabelComponent",

    getInitialState: function () {
        // getting scenario name and hostname
        return {
            labelClass: 'label label-default'
        };
    },

    componentDidMount: function () {

    },

    render: function () {
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

function updateTable(component, href) {
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
    getInitialState: function () {
        var initial = {
            "results": [],
            "resultsPerPage": 50
        };

        return initial;
    },
    //general lifecycle methods
    componentWillMount: function () {
    },
    componentDidMount: function () {
        // getting scenarios
        var href = '';
        if (cookie.load('stubo.all-hosts') || false) {
            // amending query argument to get all hosts
            href = this.props.source + '?all-hosts=true'
        } else {
            href = this.props.source + '?all-hosts=false'
        }

        updateTable(this, href);

        // subscribing to modal close event
        $('#myModal').on('hidden.bs.modal', function () {
            console.log("downloading new scenario list");
            updateTable(this, href);
        }.bind(this));
    },

    //what page is currently viewed
    setPage: function (index) {
    },
    //this will handle how the data is sorted
    sortData: function (sort, sortAscending, data) {
    },
    //this changes whether data is sorted in ascending or descending order
    changeSort: function (sort, sortAscending) {
    },
    //this method handles the filtering of the data
    setFilter: function (filter) {
    },
    //this method handles determining the page size
    setPageSize: function (size) {
    },


    render: function () {
        return <Griddle results={this.state.results}
                        useGriddleStyles={true}
                        showFilter={true} showSettings={true}
                        resultsPerPage={this.state.resultsPerPage}
                        columnMetadata={columnMeta}
                        columns={["name", "session", "status", "loaded", "last_used", "space_used_kb", "stub_count", "recorded", "actions"]}/>
    }
});

React.render(
    <ExternalScenarios source="/stubo/api/v2/scenarios/detail"/>,
    document.getElementById("app")
);