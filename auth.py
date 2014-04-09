#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]

This module contains the OAuth2 implementation for the Collins-API.
"""
import base64
import hashlib
import hmac
import json
import os
import urllib
import urllib2
import uuid


class AuthException(Exception): pass


signing_methods = {
    'HS256': lambda msg, key: hmac.new(key, msg, hashlib.sha256).digest(),
    'HS384': lambda msg, key: hmac.new(key, msg, hashlib.sha384).digest(),
    'HS512': lambda msg, key: hmac.new(key, msg, hashlib.sha512).digest(),
    'RS256': lambda msg, key: key.sign(hashlib.sha256(msg).digest(), 'sha256'),
    'RS384': lambda msg, key: key.sign(hashlib.sha384(msg).digest(), 'sha384'),
    'RS512': lambda msg, key: key.sign(hashlib.sha512(msg).digest(), 'sha512'),
    'none': lambda msg, key: '',
}


def base64url_decode(input):
    input += '=' * (4 - (len(input) % 4))
    return base64.urlsafe_b64decode(input)


def base64url_encode(input):
    return base64.urlsafe_b64encode(input).replace('=', '')


def encode(payload, key, algorithm='HS256'):
    segments = []
    header = {"typ": "JWT", "alg": algorithm}

    segments.append(base64url_encode(json.dumps(header)))
    segments.append(base64url_encode(json.dumps(payload)))
    signing_input = '.'.join(segments)

    try:
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        signature = signing_methods[algorithm](signing_input, key)
    except KeyError:
        raise NotImplementedError("Algorithm not supported")

    segments.append(base64url_encode(signature))
    return '.'.join(segments)


class Auth(object):
    def __init__(self, config, scope, popup):
        self.config = config

        self.scope = scope
        self.popup = popup
        self.accessToken = None
        self.grantCode = None
        self.states = {}

    def __buildStateUrlValue(self):
        return base64.b64encode(json.dumps(self.states))

    def __parseStateUrlValue(self, value):
        return json.loads(base64.b64decode(value))

    def __sign(payload):
        salt = os.urandom(16) # 16 bytes of randomnes
        payload["salt"] = base64_encode(salt)

        sign = encode(payload, self.config.app_secret, 'HS256')

        return sign

    def parseRedirectResponse(self, request):
        # the sdk requires state was given for auth request..
        if self.states['csrf']:
            states = self.__parseStateUrlValue(request['state']);
            if 'csrf' in states and self.states['csrf'] == states['csrf']:

                # version a) if set directly by authserver
                if 'code' in request:
                    self.grantCode = request['code']
                    self.accessToken = None
                    return 'success'

                # varsion b TODO unused) if "wrapped" by checkout
                if 'result' in request:

                    if request['result'] == 'success':
                        self.grantCode = request['code']
                        self.accessToken = None
                        return request['result']
                    else:
                        if request['result'] == 'cancel':
                            return request['result']
                        else:
                            return False

        return False

    def getLoginUrl(self):
        """
        """
        uniqid = uuid.uuid5('python_auth_sdk', self.config.app_token)
        self.states["csrf"] = hashlib.md5(uniqid)

        payload = {"app_id": self.config.app_id,
                    "info": "python_auth_sdk_{}".format(self.config.app_id),
                    "redirect_uri": self.config.redirectUri,
                    "scope": self.scope,
                    "popup": self.popup,
                    "state": self.__buildStateUrlValue(),
                    "flow": "auth"}

        sign = self.__sign(payload)

        return self.config.loginUrl + "?app_id=" + self.config.app_id + "&asr=" + payload

    def logout(self):
        self.grantCode = None
        self.accessToken = None
        self.states.clear()
        self.userAuthResult = None

    def getToken(self):
        """
        Return access_token from storage or fetch from auth-server.

        Most of the time its easier to use @see api()

        :return: AuthResult
        """
        if self.accessToken is not None:
            return self.accessToken
        elif self.grantCode:
            params = {
                'client_id': self.config.app_id,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.redirectUri,
                'code': self.grantCode
            }

            headers = {
                "Content-Type": "text/plain;charset=UTF-8",
                "User-Agent": self.config.agent,
                "Authorization": self.config.authorization,
            }

            url = self.config.resourceUrl + '/oauth/token?'
            url += urllib.urlencode(params)

            req = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(req)

            status = response.getcode()
            if status == 200:
                result = response.read()
                self.accessToken = json.loads(result)
                self.grantCode = None
                return self.accessToken
            else:
                raise AuthException("could not fetch token, because auf HTTP: {}".format(status))
        else:
            raise AuthException('not logged in')

    def api(self, resourcePath, method='get', params={}):
        tokenResult = self.getToken()

        headers = {
                "Content-Type": "text/plain;charset=UTF-8",
                "User-Agent": self.config.agent,
                "Authorization": 'Bearer {}'.format(tokenResult),
        }

        if method == 'get':
            url = '{}/api{}?{}'.format(self.resourceUrl,
                                       resourcePath, urllib.urlencode(params))
            req = urllib2.Request(url, headers=headers)
        else:
            url = '{}/api{}'.format(self.resourceUrl)
            req = urllib2.Request(url, data=params, headers=headers)

        response = urllib2.urlopen(req)

        status = response.getcode()

        if status == 200:
            return response.read()
        else:
            raise AuthException(response.read())
