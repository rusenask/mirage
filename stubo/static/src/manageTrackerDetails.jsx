import React from 'react';
//import ReactDOM from 'react-dom';
import { Label, Well} from 'react-bootstrap';
import Highlight from 'react-highlight'
var pd = require('pretty-data').pd;


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

let DtWrapper = React.createClass({
    displayName: "DtWrapper",

    render: function () {
        return <dt> {this.props.data} </dt>
    }
});

let DdWrapper = React.createClass({
    displayName: "DdWrapper",

    render: function () {
        var value = this.props.data;
        var objectConstructor = {}.constructor;
        // check if this is a JSON object and recursively applying
        // horizontal key-value styling
        if (value.constructor === objectConstructor) {
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

let FormattedResponseWrapper = React.createClass({
    displayName: "FormattedResponseWrapper",

    render: function () {
        var value = this.props.data;

        let preInstance = (
                <Highlight>
                    {value}
                </Highlight>
        );

        return <dd> {preInstance} </dd>

    }
});

let InfoArrayWrapper = React.createClass({
    displayName: "InfoArrayWrapper",

    render() {
        let info = this.props.data;
        if (info.length == 4) {
            var left = jQuery.parseJSON(info[2]);
            var right = jQuery.parseJSON(info[3]);


            let delta = jsondiffpatch.diff(left, right);

            let diffPatch = jsondiffpatch.formatters.html.format(delta, left);

            // since diffPatch is returning raw html - creating an object so it can pass through React as
            // sanitized and "safe" html
            function createMarkup() {
                return {__html: diffPatch};
            }

            // returning raw html: https://facebook.github.io/react/tips/dangerously-set-inner-html.html
            return <div dangerouslySetInnerHTML={createMarkup()}/>

        } else {
            return <span> {info.slice(1)} </span>

        }
    }

});


let TraceStatus = React.createClass({
    displayName: "TraceStatus",

    render() {
        let infoArray = this.props.data;
        let status = infoArray[0];
        if (status == "ok") {
            // infoArray contains information on response
            return <span> <Label bsStyle="success"> {status} </Label>&nbsp; <InfoArrayWrapper data={infoArray}/> </span>
        } else {
            return <span> <Label bsStyle="danger">{status}</Label>&nbsp; <InfoArrayWrapper data={infoArray}/> </span>
        }
    }
});

// list item wrapper
let TraceListItemWrapper = React.createClass({
    displayName: "TraceListItemWrapper",

    render() {
        let item = this.props.data;
        let time = item[0];
        let infoArray = item[1];

        return <li> Time: <strong> {time} </strong> &nbsp;  <TraceStatus data={infoArray}/></li>;
    }
});

// Wraps and formats trace response (when full tracking is enabled Mirage gathers more data)
let TraceResponseWrapper = React.createClass({
    displayName: "TraceResponseWrapper",

    render: function () {
        let responseList = this.props.data;
        //console.log(responseList);
        let rows = [];
        if(responseList != undefined){
            $.each(responseList, function (idx, item) {
                rows.push(<TraceListItemWrapper key={idx} data={item}/>)
            });

            console.log("TraceResponseWrapper finished, returning");
            return <dd>
                <ul> {rows} </ul>
            </dd>
        } else {
            return <div></div>
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
            rows.push(<DtWrapper data={k}/>);

            if (k == 'stubo_response') {

                let prettyfied = '';

                // checking whether this object is JSON - if so - using JSON pp, otherwise using XML pp.
                // to add more formating, for example CSS, SQL - just add more checks for objects.
                if (typeof v == 'object') {
                    prettyfied = pd.json(v);
                } else {
                    prettyfied = pd.xml(v);
                }
                rows.push(<FormattedResponseWrapper data={prettyfied} />);



            } else if (k == 'trace') {
                // tracing data, consists of response and matcher
                // console.log(v);
                // adding matcher row

                rows.push(<TraceResponseWrapper data={v.matcher}/>);
                // adding response row
                rows.push(<TraceResponseWrapper data={v.response}/>)

            } else {
                rows.push(<DdWrapper data={v}/>);
            }

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