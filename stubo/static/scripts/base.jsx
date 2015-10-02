var React = require('../node_modules/react');
var Input = require('../node_modules/react-bootstrap').Input;
var cookie = require('react-cookie');
var Tooltip = require('../node_modules/react-bootstrap').Tooltip;
var OverlayTrigger = require('../node_modules/react-bootstrap').OverlayTrigger;

// creating "track all hosts" button + cookie control

var TrackingAllHosts = React.createClass({

    getInitialState: function () {
        return {trackingAll: cookie.load('stubo.all-hosts') || false};
    },

    handleClick: function () {
        var state = this.state.trackingAll;

        // cookie options, passed as json object
        var opt = {
            'path': "/"
        };

        if (this.isMounted()) {
            cookie.save('stubo.all-hosts', !state, opt);
            this.setState({
                trackingAll: !state
            });
        }

    },

    render: function () {
        var msg = null;
        if(this.state.trackingAll){
            msg = "Disable this option to only see data for current hostname";
        }else {
            msg = "Enable this option to see data for all virtualized hosts";
        }

        var ButtonTooltip = (
            <Tooltip> {msg} </Tooltip>
        );

        return (
            <OverlayTrigger placement='right' overlay={ButtonTooltip}>
                <a href="#" onClick={this.handleClick}>
                    <i className="fa fa-th"></i>
                    <span> Tracking all hosts </span>
                    <input className="pull-right"
                           type="checkbox"
                           checked={this.state.trackingAll}
                           onChange={this.handleClick}/>
                </a>
            </OverlayTrigger>
        );
    }

});

React.render(
    <TrackingAllHosts/>,
    document.getElementById("trackingall")
);

function getBooleanState(trackingLevel) {
    return trackingLevel == "full";
}

// creating "full tracking" button
var TrackingLevelComponent = React.createClass({
    getInitialState: function () {
        return {
            checked: false,
            apiHref: "/stubo/api/get/setting?setting=tracking_level"
        }
    },

    // getting current tracking state
    componentDidMount: function () {
        // fetching data
        $.get(this.state.apiHref, function (result) {
            var trackingState = result.data.tracking_level;
            // update state
            if (this.isMounted()) {
                this.setState({
                    checked: getBooleanState(trackingState)
                });
            }
        }.bind(this));
    },

    handleClick: function () {
        // getting current state
        var fullTrack = this.state.checked;

        var settingValue = "full";
        if (fullTrack) {
            settingValue = "normal";
        }
        // creating uri to change current state
        var uri = "/stubo/api/put/setting?setting=tracking_level&value=" + settingValue;

        $.get(uri, function (result) {
            var trackingState = result.data.tracking_level;
            // update state
            if (this.isMounted()) {
                this.setState({
                    checked: getBooleanState(trackingState)
                });
            }
        }.bind(this));

    },

    render: function () {
        var msg = null;
        if(this.state.checked){
            msg = "Disable full tracking (debugging) mode.";
        }else {
            msg = "Enable this option to capture more data. Beware that this option is global and decreases" +
                " performance for all virtual Mirage instances.";
        }

        var ButtonTooltip = (
            <Tooltip> {msg} </Tooltip>
        );

        // rendering field with checkbox
        return (
            <OverlayTrigger placement='right' overlay={ButtonTooltip}>
                <a href="#" onClick={this.handleClick}>
                    <i className="fa fa-flash"></i>
                    <span> Full tracking level </span>
                    <input className="pull-right"
                           type="checkbox"
                           checked={this.state.checked}
                           onChange={this.handleClick}/>
                </a>
            </OverlayTrigger>
        )
    }

});


React.render(
    <TrackingLevelComponent/>,
    document.getElementById("trackinglevel")
);