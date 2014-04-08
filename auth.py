#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

This module contains the OAuth2 implementation for the Collins-API.
"""
import base64
import json


class AuthException(Exception):
    pass


class Auth(object):
    def __init__(self, appid, apptoken, appsecrete,
                 loginUrl, resourceUrl, redirectUri):
        self.appid = appid
        self.apptoken = apptoken
        self.appsecrete = appsecrete
        self.loginUrl = loginUrl
        self.resourceUrl = resourceUrl
        self.redirectUri = redirectUri

        self.accessToken = None
        self.grantCode = None
        self.states = {}

    def __buildStateUrlValue(self):
        return base64.b64encode(json.dumps(self.states))

    def __parseStateUrlValue(self, value):
        return json.loads(base64.b64decode(value))

    def parseRedirectResponse(self):
        pass


    def getToken(self):
        """
        Return access_token from storage or fetch from auth-server.

        Most of the time its easier to use @see api()

        :return: AuthResult
        """
        if self.grantCode:
            params = {
                    'client_id': self.appid,
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.redirectUri,
                    'code': self.grantCode
                }
        else:
            raise AuthException('not logged in')

    def api(self):
        pass
