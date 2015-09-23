var React = require('../node_modules/react');
var Well = require('../node_modules/react-bootstrap').Well;


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
        var value = this.props.data;
        var objectConstructor = {}.constructor;
        // check if this is a JSON object and recursively applying
        // horizontal key-value styling
        if(value.constructor === objectConstructor){
            const wellInstance = (
                <Well bsSize="xsmall">
                    <DlHorizontalWrapper data={value}/>
                </Well>
            );
            return <dd> {wellInstance} </dd>
        }
         else {
            return <dd> {value} </dd>
        }
    }
});

var DlHorizontalWrapper = React.createClass({
    displayName: "dlHorizontalWrapper",

    render: function () {
        var rows = [];
        var list = this.props.data;
        $.each(list, function (k, v) {
            //display the key and value pair
            rows.push(<DtWrapper data={k} />);
            rows.push(<DdWrapper data={v} />);
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