### Nalo-Apollo Gateway Proxy ###

## Configuration settings: ##

You may use environment variables or a .env file to configure the application.

The following configuration options apply:

`APOLLO_ENDPOINT` is a string containing the Kannel messaging endpoint for Apollo
`APOLLO_SECRET` is a string containing the messaging secret shared with any application allowed to communicate with Apollo
`NALO_API_KEY` is a string containing the API key for the Nalo account to use for outgoing messages
`NALO_SENDER_ID` is a string containing the whitelisted sender id to use.

The application listens on port 5000 and the docs are available at http://hostname:5000/docs
