var CommonsChunkPlugin = require("./node_modules/webpack/lib/optimize/CommonsChunkPlugin");

module.exports = {
    entry: {
        scenarioDetails: "./scripts/scenarioDetails.jsx"
        //account: "./static/src/js/Account.js"
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
              loader: 'jsx-loader?harmony'
          }
      ]
    },
    plugins: [
        new CommonsChunkPlugin("commons.js")
    ]
};

