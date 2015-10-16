import React from 'react'
import { Modal, Button} from 'react-bootstrap'
import Highlight from 'react-highlight'

var Griddle = require('../node_modules/griddle-react');

// remove delay policy action button
var RemoveButton = React.createClass({
    getInitialState: function () {
        // getting ref
        return {
            ref: this.props.data.href,
            name: this.props.data.name
        };
    },
    handleClick: function (event) {

        var infoModal = $('#myModal');
        var name = this.state.name;
        $.ajax({
            type: "DELETE",
            url: this.state.ref,
            success: function () {
                var htmlData = '<ul><li> Module (' + name + ') removed successfuly. </li></ul>';
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

        return (
            <Button onClick={this.handleClick} bsStyle='danger' bsSize='small'>
                <span>Remove</span>
            </Button>
        );
    }
});

let ShowSourceButton = React.createClass({
    displayName: "showSourceButton",

    getInitialState() {
        return {
            data: this.props.data,
            source: this.props.data.source_raw,
            name: this.props.data.name,
            showModal: false
        }
    },

    close() {
        this.setState({ showModal: false });
    },

    open() {
        this.setState({ showModal: true });
    },

    render() {
        return (
            <span>
                <Button
                    bsStyle="info"
                    onClick={this.open}
                    >
                    Show source
                </Button>

                <Modal show={this.state.showModal} onHide={this.close}
                       bsSize="large">
                    <Modal.Header closeButton>
                        <Modal.Title>Module "{this.state.name}" source code</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Highlight>
                            {this.state.source}
                        </Highlight>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.close}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </span>
        );
    }

});

var ActionComponent = React.createClass({
    displayName: "ActionComponent",

    render: function () {
        // rendering action buttons
        return (
            <div>
                <RemoveButton data={this.props.rowData}/> &nbsp;
                <ShowSourceButton data={this.props.rowData}/>
            </div>
        )
    }
});

var columnMeta = [
    {
        "columnName": "name",
        "displayName": "Module name",
        "order": 1,
        "locked": false,
        "visible": true
    },
    {
        "columnName": "latest_code_version",
        "displayName": "Code version",
        "order": 2,
        "locked": false,
        "visible": true
    },
    {
        "columnName": "loaded_sys_versions",
        "displayName": "Loaded versions",
        "locked": false,
        "visible": true
    },
    {
        "columnName": "actions",
        "displayName": "Actions",
        "locked": false,
        "visible": true,
        "customComponent": ActionComponent
    }

];

function updateTable(component, href) {
    $.get(href, function (result) {
        if (component.isMounted()) {
            component.setState({
                results: result.data
            });
        }
    });
}

var ExternalModules = React.createClass({
    getInitialState: function () {
        var initial = {
            "results": [],
            "resultsPerPage": 10
        };

        return initial;
    },
    //general lifecycle methods
    componentWillMount: function () {
    },
    componentDidMount: function () {
        let href = this.props.source;

        updateTable(this, href);

        // subscribing to modal close event
        $('#myModal').on('hidden.bs.modal', function () {
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
                        columns={["name", "latest_code_version", "loaded_sys_versions", "actions"]}/>
    }
});

React.render(
    <ExternalModules source="/api/v2/modules"/>,
    document.getElementById('app')
);
