var React = require('../node_modules/react');
var Griddle = require('../node_modules/griddle-react');

var Tooltip = require('../node_modules/react-bootstrap').Tooltip;
var OverlayTrigger = require('../node_modules/react-bootstrap').OverlayTrigger;
var Button = require('../node_modules/react-bootstrap').Button;


function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

var DtWrapper = React.createClass({
    displayName: "DtWrapper",

    render: function () {
        return <dt> {this.props.data} </dt>
    }
});

var DdWrapper = React.createClass({
    displayName: "DdWrapper",

    render: function () {
        return <dd> {this.props.data} </dd>
    }
});

var DlHorizontalWrapper = React.createClass({
    displayName: "dlHorizontalWrapper",

    render: function () {
        var rows = [];

        $.each(this.props.data, function (k, v) {
            //display the key and value pair
            rows.push(<DtWrapper data={k} />);
            rows.push(<DdWrapper data={v} />);
            //console.log(k + ' is ' + v);
        });
        return (
            <dl className="dl-horizontal">{rows}</dl>
        )
    }
});

var TrackerDetails = React.createClass({
    displayName: "TrackerDetails",

    getInitialState: function () {
        return {data: []}
    },

    componentDidMount: function () {
        // fetching data
        var href = getUrlVars()["href"];
        $.get(href, function (result) {
            var trackerRecord = result.data;
            console.log(trackerRecord);
            // update state
            if (this.isMounted()) {
                this.setState({
                    data: trackerRecord
                });
            }
        }.bind(this));
    },

    render: function () {
        return (
            <DlHorizontalWrapper data={this.state.data}/>
        )
    }
});

React.render(
    <TrackerDetails/>,
    document.getElementById("app")
);