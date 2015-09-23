var CommonsChunkPlugin = require("./node_modules/webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
    entry: {
        scenarioDetails: "./scripts/scenarioDetails.jsx",
        manageScenarios: "./scripts/manageScenarios.jsx",
        manageDelayPolicies: "./scripts/manageDelayPolicies.jsx",
        manageTracker: "./scripts/manageTracker.jsx",
        manageTrackerDetails: "./scripts/manageTrackerDetails.jsx"
    },
    output: {
        path: "./src",
        filename: "[name]-bundle.js"
    },
    module: {
      loaders: [
          {
              //regex for file type supported by the loader
              test: /\.(jsx)$/,

              //type of loader to be used
              //loaders can accept parameters as a query string
              loader: 'jsx-loader?harmony'
          }
      ]
    },
    plugins: [
        new CommonsChunkPlugin("commons.js")
    ]
};

