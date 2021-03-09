import json
import bcrypt
import jwt
import requests

from django.views import  View
from django.http import HttpResponse, JsonResponse

from behance_project.settings import SECRET_KEY
from .models import User, FollowUser, FollowField, FollowMoodBoard, FollowTeam
from feed.models import UserFeed
from .utils import login_decorator, login_and_public_decorator

class SocialLoginView(View):
    def post(self,request):
        try:
            access_token    = request.headers.get('Authorization',None)
            profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me", headers={"Authorization" : f"Bearer {access_token}"},
            )
            profile_json    = profile_request.json()
            kakao_id        = profile_json.get("id")
            kakao_account   = profile_json.get("kakao_account")
            profile         = kakao_account.get("profile")
            nickname        = profile.get("nickname")
            first_name      = nickname[1:]
            last_name       = nickname[0]
            profile_img     = profile.get("profile_image_url")


            if User.objects.filter(social_account = kakao_id).exists():
                user    = User.objects.get(social_account = kakao_id)
                token   = jwt.encode({"id" : user.id}, SECRET_KEY, algorithm = "HS256")
                token   = token.decode("utf-8")
                return JsonResponse({"token" : token}, status=200)

            else:
                User(
                    first_name      = first_name,
                    last_name       = last_name,
                    profile_img_url = profile_img,
                    social_account  = kakao_id,
                ).save()

                return HttpResponse(status=200)

        except jwt.DecodeError:
            return JsonResponse({"message" : "INVALID_TOKEN"}, status=400)

class ProfileView(View):
    @login_and_public_decorator
    def get(self,request):
        try:
            user        = None
            target_user = request.GET.get('target',None)
            if request.user != '':
                if target_user:
                    user = User.objects.get(id = target_user)
                else:
                    user = request.user
            else:
                if target_user:
                    user = User.objects.get(id = target_user)
                else:
                    return JsonResponse({'message':'NO INPUT VALUES'}, status = 400)
            user_info = {
                'name'          : user.first_name + " " + user.last_name,
                'profile_img'   : user.profile_img_url if user.profile_img_url else None,
                'location'      : ', '.join(filter(None,[user.location.city, user.location.state, user.location.country])) if user.location else None,
                'created_at'    : user.created_at,
                'view'          : sum([obj.feed.view for obj in user.userfeed_set.all()]),
                'like'          : sum([len(obj.feed.like_set.all()) for obj in user.userfeed_set.all()]),
                'followers'     : len(user.follower.all()),
                'following'     : len(user.following.all()),
                'team'          : [{
                    'name'          : obj.team.name,
                    'profile_img'   : obj.team.team_img_url,
                    'location'      : ', '.join(filter(None,[
                        obj.team.location.city,
                        obj.team.location.state,
                        obj.team.location.country
                    ])) if obj.team.location else None,
                } for obj in user.userteam_set.all()]
            }
            return JsonResponse({'data' : user_info}, status = 200)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_KEYS'}, status = 400)

class FollowView(View):
    @login_decorator
    def post(self,request):
        try:
            user                = User.objects.get(id = request.user.id)
            following_user      = request.POST.get('following_user',None)
            following_team      = request.POST.get('following_team',None)
            following_moodboard = request.POST.get('following_moodboard',None)
            following_field     = request.POST.get('following_field',None)
            if following_user:
                FollowUser.objects.create(follower_id = user.id, following_id = following_user)
            elif following_team:
                FollowTeam.objects.create(follower_id = user.id, following_id = following_team)
            elif following_moodboard:
                FollowMoodBoard.objects.create(follower_id = user.id, following_id = following_moodboard)
            elif following_field:
                FollowField.objects.create(follower_id = user.id, following_id = following_field)
            else:
                return JsonResponse({'message':'NO INPUT VALUES'})
            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

    def get(self,request):
        try:
            select              = request.GET.get('type')
            target_user         = request.GET.get('user',None)
            target_team         = request.GET.get('team',None)
            target_moodboard    = request.GET.get('moodboard',None)
            target_field        = request.GET.get('field',None)
            if select == 'followers':
                followuser_obj = None
                if target_user:
                    followuser_obj      = FollowUser.objects.filter(following_id = target_user)
                elif target_team:
                    followuser_obj      = FollowTeam.objects.filter(following_id = target_team)
                elif target_moodboard:
                    followmoodboard_obj = FollowMoodBoard.objects.filter(following_id = target_moodboard)     
                elif target_field:
                    followfield_obj     = FollowField.objects.filter(following_id = target_field)
                else:
                    pass
                follower_lst = []
                for obj in followuser_obj:
                        user_info = {
                            'id'            : obj.follower.id,
                            'name'          : obj.follower.first_name + " " + obj.follower.last_name,
                            'profile_img'   : obj.follower.profile_img_url
                        }
                        follower_lst.append(user_info)
                return JsonResponse({'data':follower_lst}, status = 200)

            elif select == 'following':
                following_lst   = []
                target_user     = User.objects.get(id = target_user)
                for user in target_user.following_user.all():
                    user_info = {
                        'id'            : user.id,
                        'name'          : user.first_name + " " + user.last_name,
                        'profile_img'   : user.profile_img_url
                    }
                    following_lst.append(user_info)
                for team in user.following_team.all():
                    team_info = {
                        'id'            : team.id,
                        'name'          : team.name,
                        'profile_img'   : team.team_img_url
                    }
                    following_lst.append(team_info)
                return JsonResponse({'data':following_lst}, status = 200)
            else:
                return JsonResponse({'message':'NO INPUT VALUES'})
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

    @login_decorator
    def delete(self, request):
        try:
            user                = User.objects.get(id = request.user.id)
            following_user      = request.POST.get('following_user',None)
            following_team      = request.POST.get('following_team',None)
            following_moodboard = request.POST.get('following_moodboard',None)
            following_field     = request.POST.get('following_field',None)
            if following_user:
                item = FollowUser.objects.get(follower_id = user.id, following_id = following_user)
                item.delete()
            elif following_team:
                item = FollowTeam.objects.get(follower_id = user.id, following_id = following_team)
                item.delete()
            elif following_moodboard:
                item = FollowMoodBoard.objects.get(follower_id = user.id, following_id = following_moodboard)
                item.delete()
            elif following_field:
                item = FollowField.objects.get(follower_id = user.id, following_id = following_field)
                item.delete()
            else:
                return JsonResponse({'message':'NO INPUT VALUES'}, status = 400)
            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

class LikeView(View):
    @login_decorator
    def post(self, request):
        try:
            user        = request.user
            target_feed = request.POST.get('feed_id')
            Like.objects.create(user_id = user.id, feed_id = feed_id)
            return HttpResponse(status = 200)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'})
    
    def get(self, request):
        try:
            select      = request.GET.get('type')
            target_feed = request.GET.get('feed_id',None)
            target_user = request.GET.get('user_id',None)
            
            if select == 'appreciations':
                user = None
                if request.user != "":
                    user = request.user
                else:
                    user = User.objects.get(id = target_user)
                like_obj = user.like_set.all()
                feed_lst = []
                for obj in like_obj:
                    feed_info = {
                        'id'        : obj.feed.id,
                        'name'      : obj.feed.name,
                        'cover_img' : obj.feed.cover_url
                    }
                return JsonResponse({'data' : feed_lst}, status = 200)

            else:
                like_obj = Like.objects.get(feed_id = target_feed)
                user_lst = []
                for obj in like_obj:
                    user_info = {
                        'id'            : obj.user.id,
                        'name'          : obj.user.first_name + " " + obj.user.last_name,
                        'profile_img'   : obj.user.profile_img_url
                    }
                    user_lst.append(user_info)
                return JsonResponse({'data' : user_lst}, status = 200)

        except KeyError:
            return JsonResponse({'message' : 'INVALID_KEYS'}, status = 400)

    @login_decorator
    def delete(self,request):
        try:
            user        = request.user
            target_feed = request.POST.get('feed_id')
            item = Like.objects.get(user_id = user.id, feed_id = feed_id)
            item.delete()
            return HttpResponse(status = 200)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'})

            




                          
            


        
        
        
        
            



