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


var dlHorizontalWrapper = React.createClass({
   displayName: "dlHorizontalWrapper",

    getInitialState: function() {
        return {data: this.props.data}
    },

    render: function() {
        var trackerData = this.state.data;
        console.log("entering dlhorizontalwrapper");
        console.log(trackerData);
        return <dd> {trackerData} </dd>
    }
});

function updateComponent(component, href) {
    $.get(href, function (result) {
        if (component.isMounted()) {
            console.log("updating");
            //console.log(result);
            component.setState({
                data: result.data
            });
        }
    });
}

var TrackerDetails = React.createClass({
    displayName: "TrackerDetails",

    getInitialState: function () {
        return {data: []}
    },

    componentDidMount: function () {
        // fetching data
        var href = getUrlVars()["href"];
        $.get(href, function(result) {
            var trackerRecord = result.data;
            console.log(trackerRecord);
            if (this.isMounted()) {
                this.setState({
                    data: trackerRecord
                });
            }
        }.bind(this));
    },

    render: function() {
        return <dlHorizontalWrapper data={this.state.data}/>
    }
});

React.render(
    <TrackerDetails/>,
    document.getElementById("app")
);