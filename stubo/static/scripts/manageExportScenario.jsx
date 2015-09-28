import React from 'react'

import { Grid, Row, Col } from 'react-bootstrap'

function getUrlVars()
{
    let vars = [], hash;
    let hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    let lng = hashes.length;
    for(var i = 0; i < lng; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}


let ExportInformation = React.createClass({
    displayName: "ExportInformation",

    getInitialState: function() {
        return {
            "results": [],
            "href": getUrlVars()["scenario"] || null
        };
    },

    componentWillMount: function() {
      console.log("component will mount");
    },

    componentDidMount: function(){
        console.log(this.state.href);
        let infoModal = $('#myModal');
        // creating body for export POST request
        let body = {
            export: null
        };

        let that = this;

        $.ajax({
            type: "POST",
            dataType: "json",
            url: this.state.href + '/action',
            data: JSON.stringify(body),
            success: function (data) {
                if (that.isMounted()) {
                    that.setState({
                        results: data
                    });
                }
            }
        }).fail(function ($xhr) {
            var data = $xhr.responseJSON;
            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
        });
    },

    render: function(){
        // constructing grid
        const gridInstance = (
            <Grid fluid={true}>
                <Row>
                    <Col md={6}>
                       <Col className="box">
                           <Col className="box-header">
                               <h3 className="box-title"> Exported Command files</h3>
                           </Col>

                           <Col className="box-body pad">
                               Commands
                           </Col>
                       </Col>
                    </Col>

                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Exported YAML files</h3>
                            </Col>

                            <Col className="box-body pad">
                                Yaml
                            </Col>
                        </Col>
                    </Col>

                </Row>
            </Grid>
        );
        // rendering
        return (
            <div> {gridInstance} </div>
        )
    }

});


React.render(
    <ExportInformation />,
    document.getElementById("app")
);