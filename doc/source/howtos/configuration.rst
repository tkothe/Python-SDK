Configuration
=============

The SDK has to be configured for your connection. The SDK comes with three
instances:

    * :py:class:`collins.Config`
    * :py:class:`collins.JSONConfig`
    * :py:class:`collins.JSONEnvironmentFallbackConfig`


A good practice is to use the JSONConfig instance, so your app-id and password
are not hard coded in the source code.
