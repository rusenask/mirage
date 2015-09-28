import React from 'react'

import { Grid, Row, Col } from 'react-bootstrap'

function getUrlVars() {
    let vars = [], hash;
    let hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    let lng = hashes.length;
    for (var i = 0; i < lng; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

let LinksComponent = React.createClass({
    displayName: "LinksComponent",

    getInitialState: function () {
        console.log(this.props.data);
        return {
            "data": this.props.data
        }
    },

    render: function () {
        return (
            <div>
                {this.props.data}
            </div>
        )
    }
});


let ExportInformation = React.createClass({
    displayName: "ExportInformation",

    getInitialState: function () {
        return {
            "results": [],
            "href": getUrlVars()["scenario"] || null,
            "mounted": false
        };
    },

    componentWillMount: function () {
    },

    componentDidMount: function () {
        let infoModal = $('#myModal');
        // creating body for export POST request
        let body = {
            export: null
        };

        let that = this;
        // creating full url + removing hashes (can be there due to enabling/disabling check boxes)
        let url = (this.state.href + '/action').replace("#", "");

        $.ajax({
            type: "POST",
            dataType: "json",
            url: url,
            data: JSON.stringify(body),
            success: function (data) {
                if (that.isMounted()) {
                    that.setState({
                        results: data,
                        mounted: true
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

    render: function () {

        let YamlLinks, CommandLinks = null;

        // getting yaml links
        if(this.state.mounted){
            YamlLinks = (
                <LinksComponent data={this.state.results.data.yaml_links}/>
            );
        } else {
            YamlLinks = (
                <div> Loading.. </div>
            );
        }
        // getting command links
        if(this.state.mounted){
            CommandLinks = (
                <LinksComponent data={this.state.results.data.command_links}/>
            );
        } else {
            CommandLinks = (
                <div> Loading.. </div>
            );
        }


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
                                {CommandLinks}
                            </Col>
                        </Col>
                    </Col>

                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Exported YAML files</h3>
                            </Col>

                            <Col className="box-body pad">
                                {YamlLinks}
                            </Col>
                        </Col>
                    </Col>

                </Row>
            </Grid>
        );
        // rendering the grid
        return (
            <div> {gridInstance} </div>
        )
    }

});


React.render(
    <ExportInformation />,
    document.getElementById("app")
);