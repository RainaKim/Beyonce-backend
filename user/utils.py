import jwt
import json
import requests

from django.http import JsonResponse
from my_settings import SECRET
from .models import User

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token    = request.headers.get('Authorization')
            payload         = jwt.decode(access_token, SECRET['SECRET_KEY'], algorithm = 'HS256')
            user            = User.objects.get(id = payload['id'])
            request.user    = user
            return func(self, request, *args, **kwargs)
        
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status = 400)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            JsonResponse({'message':'INVALID_KEY'}, status = 400)
    return wrapper

def login_and_public_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization')
            if access_token:
                payload         = jwt.decode(access_token, SECRET['SECRET_KEY'], algorithm = 'HS256')
                user            = User.objects.get(id = payload['id'])
                request.user    = user
            else:
                request.user    = ''
            return func(self, request, *args, **kwargs)
        
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status = 400)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            JsonResponse({'message':'INVALID_KEY'}, status = 400)
    return wrapper



            


