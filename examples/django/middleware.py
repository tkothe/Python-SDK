#-*- coding: utf-8 -*-
"""
:Author: Arne Simon [arne.simon@slice-dice.de]
"""
from django.contrib.auth import authenticate, login
import logging

logger = logging.getLogger("aboutyou.middleware")

class AboutYouMiddleware(object):
    """
    An authentication middleware which uses aboutyou access token.
    """
    def process_request(self, request):
        try:
            if not request.user.is_authenticated():
                token = None

                # try to use the Authorization header
                if "HTTP_AUTHORIZATION" in request.META:
                    token = request.META["HTTP_AUTHORIZATION"].split(' ')[1]
                else:

                    # there is no authorization header so we look in the cookies
                    if "aboutyou_access_token" in request.COOKIES:
                        token = request.COOKIES["aboutyou_access_token"]

                if token:
                    user = authenticate(aboutyou_token=token)

                    if user is not None and not user.is_anonymous():
                        login(request, user)
        except:
            logger.exception('')
