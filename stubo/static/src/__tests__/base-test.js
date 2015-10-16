var React = require('react');
var TestUtils = require('react/lib/ReactTestUtils'); //I like using the Test Utils, but you can just use the DOM API instead.
var expect = require('expect');
var TrackingLevelComponent = require('../base'); //my root-test lives in components/__tests__/, so this is how I require in my components.

describe('TrackingLevelComponent exists', function () {
    it('renders without problems', function () {
        var TrackingLevelComponent = TestUtils.renderIntoDocument(<TrackingLevelComponent/>);
        expect(TrackingLevelComponent).toExist();
    });
});