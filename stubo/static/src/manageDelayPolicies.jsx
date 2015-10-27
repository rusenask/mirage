var React = require('../node_modules/react');
var Griddle = require('../node_modules/griddle-react');
var Button = require('../node_modules/react-bootstrap').Button;
var cookie = require('react-cookie');

// wrapper for list items
var ListItemWrapper = React.createClass({
    displayName: "ListItemWrapper",

    getInitialState: function () {
        return {
            item: this.props.item,
            kvalue: this.props.kvalue
        };
    },

    render: function () {
        return <li><strong>{this.state.kvalue}: </strong> {this.state.item}</li>
    }

});

var DelayDetailsComponent = React.createClass({
    displayName: "DelayDetailsComponent",

    getInitialState: function () {
        // getting scenario name and hostname
        return {
            labelClass: 'label label-default'
        };
    },

    componentDidMount: function () {

    },

    render: function () {

        switch (this.props.rowData.delay_type) {
            case undefined:
                this.state.labelClass = '';
                break;

            case 'fixed':
                return <span> {this.props.rowData.milliseconds} milliseconds</span>;
                break;

            case 'normalvariate':
                return (
                    <ul className="list-unstyled">
                        <ListItemWrapper kvalue='stddev' item={this.props.rowData.stddev}></ListItemWrapper>
                        <ListItemWrapper kvalue='mean' item={this.props.rowData.mean}></ListItemWrapper>
                    </ul>
                );
                break;

            case 'weighted':
                //delay list array
                var delayList = this.props.rowData.delays.split(":");
                return (
                    <ul className="list-unstyled">
                        {delayList.map(function(d) {
                            var delay = d.split(",");
                            var kvalue = delay[0];
                            var item = delay.slice(1).join(', ');
                            return  <ListItemWrapper kvalue={kvalue} item={item}></ListItemWrapper>;
                        })}
                    </ul>
                );

                break;
        }


        return <span className={this.state.labelClass}> {this.props.rowData.delay_type}</span>

    }
});

// remove delay policy action button
var RemoveButton = React.createClass({
    getInitialState: function () {
        // getting ref
        return {
            ref: this.props.data.delayPolicyRef,
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
                var htmlData = '<ul><li> Delay policy (' + name + ') removed successfuly. </li></ul>';
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

var ActionComponent = React.createClass({
    displayName: "ActionComponent",

    render: function () {
        // rendering action buttons
        return (
            <RemoveButton data={this.props.rowData}/>
        )
    }
});

var columnMeta = [
    {
        "columnName": "name",
        "displayName": "Delay Name",
        "order": 1,
        "locked": false,
        "visible": true
    },
    {
        "columnName": "delay_type",
        "displayName": "Type",
        "order": 2,
        "locked": false,
        "visible": true
    },
    {
        "columnName": "details",
        "displayName": "Details",
        "locked": false,
        "visible": true,
        "customComponent": DelayDetailsComponent
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

var ExternalDelayPolicies = React.createClass({
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
        // getting delay policies
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
                        columns={["delay_type", "name", "details", "actions"]}/>
    }
});

React.render(
    <ExternalDelayPolicies source="/api/v2/delay-policy/detail"/>,
    document.getElementById('app')
);
