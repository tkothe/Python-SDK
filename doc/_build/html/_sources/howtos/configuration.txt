Configuration
=============

The SDK has to be configured for your connection. The SDK comes with four
instances:

    * :py:class:`aboutyou.Config`
    * :py:class:`aboutyou.YAMLConfig`
    * :py:class:`aboutyou.JSONConfig`
    * :py:class:`aboutyou.JSONEnvironmentFallbackConfig`


A good practice is to use the YAMLConfig instance, so your app-id and password
are not hard coded in the source code and YAML provides a nice and user-friendly
data layout.
