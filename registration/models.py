from django.db import models
from django.contrib.auth.models import User

import secrets
import datetime
# Create your models here.

class UserResetPassword(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)

    def generate_token(self):
        return secrets.token_urlsafe()

    def check_token(self, token):
        tz = self.date.tzinfo
        t_now = datetime.datetime.now(tz=tz)

        # Check the token time less than hour
        dt = t_now - self.date
        if dt.total_seconds() > 3600:
            self.is_valid = False

        # Return True if the token is correct and is_valid
        res = (token == self.token) and self.is_valid
        
        # Set the token invalid
        self.is_valid = False

        return res

    def save(self, *args, **kwargs):
        # Generate a token and set valid
        self.token = self.generate_token()
        self.is_valid = True
        super(UserResetPassword, self).save(*args, **kwargs)

