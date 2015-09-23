var React = require('../node_modules/react');
var Input = require('../node_modules/react-bootstrap').Input;


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
        // rendering field with checkbox
        return (
            <a href="#" onClick={this.handleClick}>
                <i className="fa fa-flash"></i>
                <span> Full tracking level </span>
                <input className="pull-right"
                       type="checkbox"
                       checked={this.state.checked}
                       onChange={this.handleClick}/>
            </a>
        )
    }

});


React.render(
    <TrackingLevelComponent/>,
    document.getElementById("trackinglevel")
);