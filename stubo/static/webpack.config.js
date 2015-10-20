var CommonsChunkPlugin = require("./node_modules/webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
    entry: {
        base: "./src/base.jsx",
        scenarioDetails: "./src/scenarioDetails.jsx",
        manageScenarios: "./src/manageScenarios.jsx",
        manageExportScenario: "./src/manageExportScenario.jsx",
        manageDelayPolicies: "./src/manageDelayPolicies.jsx",
        manageExternalModules: "./src/manageExternalModules.jsx",
        manageTracker: "./src/manageTracker.jsx",
        manageTrackerDetails: "./src/manageTrackerDetails.jsx",
        manageExecuteCommands: "./src/manageExecuteCommands.jsx"
    },
    output: {
        path: "./dist",
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

