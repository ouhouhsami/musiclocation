from social_auth.backends import BaseOAuth2, OAuthBackend, USERNAME
from urllib2 import Request, urlopen, HTTPError
from urllib import urlencode
from django.utils import simplejson
from django.contrib.auth import authenticate
from social_auth.backends.exceptions import StopPipeline, AuthException, \
                                            AuthFailed, AuthCanceled, \
                                            AuthUnknownError, AuthTokenError, \
                                            AuthMissingParameter
from django.http import QueryDict

class DeezerBackend(OAuthBackend):
    name = "deezer"

    def get_user_id(self, details, response):
        from pprint import pprint
        pprint(details)
        """Return user id"""
        return response['id']
    
    def get_user_details(self, response):
        """Return user details from Instagram account"""
        return {USERNAME: response.get('id'),
              'email': response.get('email'),
              'fullname': response.get('username', ''),
              'first_name': response.get('firstname', ''),
              'last_name': response.get('lastname', '')}

class DeezerAuth(BaseOAuth2):
    AUTHORIZATION_URL = 'http://connect.deezer.com/oauth/auth.php'
    ACCESS_TOKEN_URL = 'http://connect.deezer.com/oauth/access_token.php'
    RESPONSE_TYPE = 'code'
    AUTH_BACKEND = DeezerBackend
    SETTINGS_KEY_NAME = 'DEEZER_APP_ID'
    SETTINGS_SECRET_NAME = 'DEEZER_SECRET_KEY'

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        params = {'access_token': access_token}
        url = 'http://api.deezer.com/2.0/user/me?' + urlencode(params)
        #TODO: check json element types
        return simplejson.load(urlopen(url))
        
    def auth_complete(self, *args, **kwargs):
        """Completes loging process, must return user instance"""
        if self.data.get('error'):
            error = self.data.get('error_description') or self.data['error']
            raise AuthFailed(self, error)

        client_id, client_secret = self.get_key_and_secret()
        params = {'code': self.data.get('code', ''), 
                  'app_id': client_id,
                  'secret': client_secret,
                  'redirect_uri': self.redirect_uri}
        
        # ugly: I can't use Request with deezer OAUTH
        url = self.ACCESS_TOKEN_URL + '?' + urlencode(params)
        try:
            response = QueryDict(urlopen(url).read(), mutable=True)
        except HTTPError, e:
            if e.code == 400:
                raise AuthCanceled(self)
            else:
                raise
        except (ValueError, KeyError):
            raise AuthUnknownError(self)

        if response.get('error'):
            error = response.get('error_description') or response.get('error')
            raise AuthFailed(self, error)
        else:
            data = self.user_data(response.get('access_token'), response)
            response.update(data or {})
            kwargs.update({
                'auth': self,
                'response': response,
                self.AUTH_BACKEND.name: True
            })
            return authenticate(*args, **kwargs)



BACKENDS = {
    'deezer': DeezerAuth,
}