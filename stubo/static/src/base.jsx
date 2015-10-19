import React from 'react'
import {Input, Tooltip, OverlayTrigger } from 'react-bootstrap'
import cookie from 'react-cookie'
// creating "track all hosts" button + cookie control

var TrackingAllHosts = React.createClass({
    displayName: "TrackingAllHosts",

    getInitialState() {
        // by default - tracking from all hosts.
        return {trackingAll: cookie.load('stubo.all-hosts') || true};
    },

    handleClick() {
        let state = this.state.trackingAll;

        // cookie options, passed as json object
        let opt = {
            'path': "/"
        };

        if (this.isMounted()) {
            cookie.save('stubo.all-hosts', !state, opt);
            this.setState({
                trackingAll: !state
            });
        }

    },

    render() {
        var msg = null;
        if (this.state.trackingAll) {
            msg = "Disable this option to only see data for current hostname";
        } else {
            msg = "Enable this option to see data for all virtualized hosts";
        }

        const ButtonTooltip = (
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

function getBooleanState(trackingLevel) {
    return trackingLevel == "full";
}

// creating "full tracking" button
var TrackingLevelComponent = React.createClass({
    displayName: "TrackingLevelComponent",

    getInitialState() {
        return {
            checked: false,
            apiHref: "/stubo/api/get/setting?setting=tracking_level"
        }
    },

    // getting current tracking state
    componentDidMount() {
        // fetching data
        $.get(this.state.apiHref, function (result) {
            let trackingState = result.data.tracking_level;
            // update state
            if (this.isMounted()) {
                this.setState({
                    checked: getBooleanState(trackingState)
                });
            }
        }.bind(this));
    },

    handleClick() {
        // getting current state
        let fullTrack = this.state.checked;

        let settingValue = "full";
        if (fullTrack) {
            settingValue = "normal";
        }
        // creating uri to change current state
        let uri = "/stubo/api/put/setting?setting=tracking_level&value=" + settingValue;

        $.get(uri, function (result) {
            let trackingState = result.data.tracking_level;
            // update state
            if (this.isMounted()) {
                this.setState({
                    checked: getBooleanState(trackingState)
                });
            }
        }.bind(this));

    },

    render() {
        let msg = null;
        if (this.state.checked) {
            msg = "Disable full tracking (debugging) mode.";
        } else {
            msg = "Enable this option to capture more data. Beware that this option is global and decreases" +
                " performance for all virtual Mirage instances.";
        }

        const ButtonTooltip = (
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

let SettingsComponent = React.createClass({

    render() {
        const trackingLevel = (
            <li>
                <TrackingLevelComponent/>
            </li>);
        const allHosts = (
            <li>
                <TrackingAllHosts/>
            </li>);
        return (
            <ul className="sidebar-menu">
                {trackingLevel}
                {allHosts}
            </ul>
        )
    }

});

React.render(
    <SettingsComponent/>,
    document.getElementById("SettingsComponent")
);