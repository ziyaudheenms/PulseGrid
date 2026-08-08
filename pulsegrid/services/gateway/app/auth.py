# This module handles the authentication for all the required routes that are comming thorugh this Gateway
# For the authentication, we are using the clerk sdk
#
# PROCESS ->
# the frontend which uses this gateway will send a signed token issuesd by clerk,
# Backend using the incoming token, verifies it and extracts the user info.
# the session returned by the clerk sdk is used to identify the user and the session is valid for 60 second lifespan.
#
# REFERENCE -> https://clerk.com/articles/how-to-add-authentication-to-a-python-backend
