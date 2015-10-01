var CommonsChunkPlugin = require("./node_modules/webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
    entry: {
        base: "./scripts/base.jsx",
        scenarioDetails: "./scripts/scenarioDetails.jsx",
        manageScenarios: "./scripts/manageScenarios.jsx",
        manageExportScenario: "./scripts/manageExportScenario.jsx",
        manageDelayPolicies: "./scripts/manageDelayPolicies.jsx",
        manageExternalModules: "./scripts/manageExternalModules.jsx",
        manageTracker: "./scripts/manageTracker.jsx",
        manageTrackerDetails: "./scripts/manageTrackerDetails.jsx",
        manageExecuteCommands: "./scripts/manageExecuteCommands.jsx"
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
              loader: 'babel'
          },
          {
              test: /\.js$/, loader: 'babel-loader'
          }
      ]
    },
    plugins: [
        new CommonsChunkPlugin("commons.js")
    ]
};

