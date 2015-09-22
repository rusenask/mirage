/**
 * Created by karolisrusenas on 22/09/15.
 */

var React = require('../node_modules/react/react.js');

var Inspector = require('../node_modules/react-json-inspector');

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

var scenario_href = getUrlVars()["scenario"];


function getData(href){
    $.get(href, function (result) {
        // render component
        React.render(
            <Inspector data={ result.data } />,
            document.getElementById('app')
        );
    });
}

getData(scenario_href + "/stubs");

