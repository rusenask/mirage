var React = require('../node_modules/react');

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
            console.log(trackingState);
            // update state
            if (this.isMounted()) {
                this.setState({
                    checked: getBooleanState(trackingState)
                });


            }
        }.bind(this));
    },

    render: function () {
        return (
            <a href="#" id="all_hosts_label">
                <i className="fa fa-flash"></i>
                <span> Full tracking level </span>
                <input type="checkbox"
                       className="pull-right" value={this.state.checked}/>
            </a>
        )

    }

});


React.render(
    <TrackingLevelComponent/>,
    document.getElementById("trackinglevel")
);