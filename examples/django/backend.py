#-*- coding: utf-8 -*-
"""
:Author: Arne Simon [arne.simon@slice-dice.de]
"""
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from users.models import User
from aboutyou.auth import get_me
import logging


logger = logging.getLogger("aboutyou.backend")


class AboutYouBackend(ModelBackend):
    """
    An aboutyou backend which authenticates a user by its access token.

    .. node::

        If no user with the corresponding collins id exists a new one will be creates.
    """
    def authenticate(self, aboutyou_token=None):
        if aboutyou_token is not None:

            response = get_me(aboutyou_token)

            if response.status_code == 200:
                user = None

                try:
                    data = response.json()

                    user, created = User.objects.get_or_create(aboutyou_id=data.get("id"))

                    user.token = aboutyou_token

                    if created:
                        logger.info("created user %s %s %s", user.aboutyou_id, user.username, user.email)

                        user.username = "{}_{}.".format(data.get("firstname"), data.get("lastname")[0])

                    # we update the user information, maybe the user changed
                    user.email = data.get("email")
                    user.first_name = data.get("firstname")
                    user.last_name = data.get("lastname")
                    user.save()

                except ValueError:
                    logger.exception('aboutyou_token')
                    user = None

                if user is not None and user.is_active:
                    logger.debug("authenticated user %s %s %s", user.aboutyou_id, user.username, user.email)

                    return user

