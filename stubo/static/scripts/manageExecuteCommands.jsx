import React from 'react'

import { Grid, Row, Col, OverlayTrigger, Tooltip, Input, ButtonInput} from 'react-bootstrap'


const ExecuteCmdsFile = React.createClass({
    getInitialState() {
        return {
            disabled: true,
            style: null,
            placeholder: "/static/cmds/demo/first.commands",
            submitUrl: "/manage/execute"
        };
    },

    resetValidation() {
        this.setState({
            disabled: true,
            style: null
        });
    },

    validationState() {
        let length = this.refs.input.getValue().length;
        let style = 'danger';

        if (length > 0) style = 'success';
        //else if (length > 5) style = 'warning';

        let disabled = style !== 'success';

        return { style, disabled };
    },

    handleChange() {
        this.setState( this.validationState() );
    },

    handleSubmit(e) {
        let val = this.refs.input.getValue();
        //
        e.preventDefault();
        // make a POST call
        let body = {
            commandFile: val
        };
        $.ajax({
            type: "POST",
            dataType: "json",
            url: this.state.submitUrl,
            data: JSON.stringify(body),
            success: function (data) {
                console.log(data);
            }
        }).fail(function ($xhr) {
            var data = $xhr.responseJSON;
            var htmlData = '<ul><li>Error: ' + data.error.message + '</li></ul>';
            infoModal.find('.modal-body').html(htmlData);
            infoModal.modal('show');
        });
    },

    render() {


        return (
            <form onSubmit={this.handleSubmit} >
                <Input type="text" ref="input" name="cmdfile" placeholder={this.state.placeholder}

                       onChange={this.handleChange} />
                <ButtonInput type="reset" bsStyle="primary" onClick={this.resetValidation} />
                <ButtonInput type="submit" value="Execute from file" bsStyle={this.state.style} bsSize="small" disabled={this.state.disabled} />
            </form>
        );
    }
});


let ExecuteCommandsPanel = React.createClass({
    displayName: "ExecuteCommandsPanel",

    render: function () {

        let ExecuteCommandsFile = <ExecuteCmdsFile />;

        // constructing grid
        const gridInstance = (
            <Grid fluid={true}>
                <Row>
                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Execute Commands from file</h3>
                            </Col>

                            <Col className="box-body pad">
                                {ExecuteCommandsFile}
                            </Col>
                        </Col>
                    </Col>

                    <Col md={6}>
                        <Col className="box">
                            <Col className="box-header">
                                <h3 className="box-title"> Execute Commands directly</h3>
                            </Col>

                            <Col className="box-body pad">
                                execute commands directly
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




React.render(<ExecuteCommandsPanel />, document.getElementById("ExecuteCommands"));