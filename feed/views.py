import json
import random
import datetime
import boto3

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from itertools import chain

from .models import *
from user.models import *
from user.utils import login_decorator, login_and_public_decorator
from my_settings import ACCESS_KEY, SECRET_ACCESS_KEY

class FeedListView(View):
    @login_and_public_decorator
    def get(self,request,page_type,category_id):
        try:
            limit   = int(request.GET.get('limit'))
            offset  = int(request.GET.get('offset'))
            result  = {
                'main_categories' : [{
                    'id'    : cate.id,
                    'title' : cate.name,
                    'img'   : Feed.objects.get(id = random.randint(0,100)).cover_url
                } for cate in Field.objects.filter(is_main = 1)][::-1]
            }
            feeds_obj = Feed.objects.prefetch_related(
                'userfeed_set',
                'moodboardfeed_set',
                'teamfeed_set',
                'feedfield_set'
            ).all()
            if request.user != "":
                user_id = request.user.id
                if page_type == "for_you":
                    feeds_obj = feeds_obj.filter(
                        Q(team__member                  = user_id) | 
                        Q(owner                         = user_id) | 
                        Q(team__follower_team           = user_id) | 
                        Q(field__follower_field         = user_id) | 
                        Q(owner__follower               = user_id) | 
                        Q(moodboard__owner              = user_id) | 
                        Q(moodboard__follower_moodboard = user_id)
                    ).distinct()
                elif page_type == "main":
                    pass
                else:
                    return JsonResponse({'message' : 'INVALID KEYS'}, status = 400)
            if page_type == "main" and category_id != 37:
                field = Field.objects.get(id = category_id)
                result.update({
                    'field'         : field.name,
                    'description'   : field.description,
                    'is_followed'   : True if request.user != '' and user.following_field.filter(id = category_id).exists() else False
                })
                feeds_obj = feeds_obj.filter(
                    Q(field__related_to = category_id)
                ).distinct()
            elif page_type == "main" and category_id == 37:
                result.update({
                    'field'         : 'Best of behance',
                    'description'   : Field.objects.get(name = 'Best of Behance').description
                })
                feeds_obj_with = feeds_obj.filter(
                    Q(owner__isnull = False) |
                    Q(team__isnull  = False) 
                    )
                feeds_obj = feeds_obj_with.distinct()
                feeds_obj = feeds_obj.order_by('-id')

            feeds = []
            if len(feeds_obj) < offset+limit:
                limit = len(feeds_obj) - offset
            result.update({
                'feeds' : [{
                    'id'                : feeds_obj[i].id,
                    'title'             : feeds_obj[i].name,
                    'cover_img'         : feeds_obj[i].cover_url,
                    'like'              : len(feeds_obj[i].like_set.all()),
                    'view'              : feeds_obj[i].view,
                    'background_color'  : "rgb(" + str(feeds_obj[i].color.rvalue) + ", " + str(feeds_obj[i].color.gvalue) + ", " + str(feeds_obj[i].color.bvalue) + ")" if feeds_obj[i].color else "rgb(105, 105, 105)",
                    'owners'            : [{
                        'id'                : owner.user.id,
                        'name'              : owner.user.first_name + " " + owner.user.last_name,
                        'profile_img'       : owner.user.profile_img_url,
                        'type'              : 'user'
                    } for owner in feeds_obj[i].userfeed_set.all()] if feeds_obj[i].userfeed_set.all().exists() and len(feeds_obj[i].userfeed_set.all()) > 1 else [{
                        'id'            : owner.user.id,
                        'name'          : owner.user.first_name + " " + owner.user.last_name,
                        'profile_img'   : owner.user.profile_img_url,
                        'location'      : ', '.join(filter(None,[
                            owner.user.location.city,
                            owner.user.location.state,
                            owner.user.location.country
                        ])) if owner.user.location else None,
                        'work_imgs'     : list(filter(None,[UserFeed.objects.filter(user_id = owner.user.id)[i].feed.cover_url if i < len(UserFeed.objects.filter(user_id = owner.user.id)) else None for i in range(3)])),
                        'like'          : sum([len(obj.feed.like_set.all()) for obj in UserFeed.objects.filter(user_id = owner.user.id)]),
                        'view'          : sum([obj.feed.view for obj in UserFeed.objects.filter(user_id = owner.user.id)]),
                        'type'          : 'user'
                    } for owner in feeds_obj[i].userfeed_set.all()] if feeds_obj[i].userfeed_set.all().exists() and len(feeds_obj[i].userfeed_set.all()) == 1 else [{
                        'id'            : team_obj.team.id,
                        'name'          : team_obj.team.name,
                        'profile_img'   : team_obj.team.team_img,
                        'type'          : 'team'
                    } for team_obj in feeds_obj[i].teamfeed_set.all()] if feeds_obj[i].teamfeed_set.all().exists() and len(feeds_obj[i].teamfeed_set.all()) > 1 else [{
                        'id'            : team_obj.team.id,
                        'name'          : team_obj.team.name,
                        'profile_img'   : team_obj.team.team_img_url  ,
                        'location'      : ', '.join(filter(None,[
                            team_obj.team.location.city,
                            team_obj.team.location.state,
                            team_obj.team.location.country
                        ])) if team_obj.team.location else None,
                        'work_imgs'     : list(filter(None,[TeamFeed.objects.filter(team_id = team_obj.team.id)[i].feed.cover_url if i < len(TeamFeed.objects.filter(team_id = team_obj.team.id)) else None for i in range(3)])),
                        'like'          : sum([len(team_obj.feed.like_set.all()) for team_obj in TeamFeed.objects.filter(team_id = team_obj.team.id)]),
                        'view'          : sum([team_obj.feed.view for team_obj in TeamFeed.objects.filter(team_id = team_obj.team.id)]),
                        'type'          : 'team'
                    } for team_obj in feeds_obj[i].teamfeed_set.all()] if feeds_obj[i].teamfeed_set.all().exists() and len(feeds_obj[i].teamfeed_set.all()) == 1 else None
                } for i in range(offset,offset+limit)]
            })
            return JsonResponse({'data':result}, status = 200) 
        except TypeError:
            return JsonResponse({'message' : 'NO INPUT VALUES'}, status = 400)
        except Feed.DoesNotExist:
            return JsonResponse({'message' : 'FEED DOES NOT EXIST'}, status = 400)

class FeedDetailView(View):
    def get(self,request,feed_id):
        feed = Feed.objects.get(id = feed_id)
        result = {
            'title'     : feed.name,
            'owners'    : [{
                'name'          : obj.user.first_name + " " + obj.user.last_name,
                'profile_img'   : obj.user.profile_img_url,
                'location'      : ', '.join(filter(None,[
                        obj.user.location.city,
                        obj.user.location.state,
                        obj.user.location.country
                ])) if obj.user.location else None,
                'work_imgs'     : list(filter(None,[UserFeed.objects.filter(user_id = obj.user.id)[i].feed.cover_url if i < len(UserFeed.objects.filter(user_id = obj.user.id)) else None for i in range(6)])),
                'type'          : 'user'
            } for obj in feed.userfeed_set.all()] if feed.userfeed_set.all().exists() else
                [{
                    'name'          : team_obj.team.name,
                    'profile_img'   : team_obj.team.team_img_url,
                    'location'      : ', '.join(filter(None,[
                        team_obj.team.location.city,
                        team_obj.team.location.state,
                        team_obj.team.location.country
                    ])) if team_obj.team.location else None,
                    'work_imgs'     : list(filter(None,[TeamFeed.objects.filter(team_id = team_obj.team.id)[i].feed.cover_url if i < len(TeamFeed.objects.filter(team_id = team_obj.team.id)) else None for i in range(6)])),
                    'type'          : 'team'
                } for team_obj in feed.teamfeed_set.all()] if feed.teamfeed_set.all().exists() else None,
            'like'          : len(feed.like_set.all()),
            'view'          : feed.view,
            'comment'       : len(feed.comment_set.all()),
            'comment_lst'   : [{
                'username'      : com.user.first_name + " " + com.user.last_name,
                'profile_img'   : com.user.profile_img_url,
                'content'       : com.content,
                'created_at'    : com.created_at
            } for com in feed.comment_set.all()],
            'img_tool'      : [obj.imge_tool.icon_url for obj in feed.feedimagetool_set.all()],
            'created_at'    : feed.created_at,
            'content'       : feed.content if feed.content else [img.img_url for img in Image.objects.filter(feed_id = feed_id)]
        }
        return JsonResponse({'data':result}, status = 200)
        
    @login_decorator
    def delete(self,request,feed_id):
        try:
            feed = Feed.objects.get(id = feed_id)
            if feed.userfeed_set.all().exists():
                feed.userfeed_set.all().delete()
            elif feed.teamfeed_set.all().exists():
                feed.teamfeed_set.all().delete()
            feed.delete()
            return HttpResponse(status = 200)

        except Feed.DoesNotExist:
            return JsonResponse({'message' : 'FEED DOES NOT EXIST'}, status = 400)

        except KeyError:
            return JsonResponse({'message' : 'INVALID_KEYS'}, status = 400)
        
class FeedUploadView(View):
    @login_decorator
    def post(self,request):
        try:
            user        = request.user
            name        = request.POST.get('title')
            s3_client   = boto3.client(
                's3',
                aws_access_key_id       = ACCESS_KEY,
                aws_secret_access_key   = SECRET_ACCESS_KEY
            )
            for file in request.FILES.getlist('file'):
                s3_client.upload_fileobj(
                    file,
                    "behanceimg",
                    file.name,
                    ExtraArgs = {
                        "ContentType" : file.content_type
                    }
                )
            file_urls   = [f"https://s3.ap-northeast-2.amazonaws.com/behanceimg/{file.name}" for file in request.FILES.getlist('file')]
            new_feed    = Feed.objects.create(
                name        = name,
                cover_url   = file_urls[0]
            )
            UserFeed.objects.create(
                feed_id     = new_feed.id,
                user_id     = user.id
            )
            for i in range(1,len(file_urls)):
                Image.objects.create(
                    img_url = file_urls[i],
                    feed_id = new_feed.id
                )
            return JsonResponse({'id': new_feed.id}, status = 200)
        except IndexError:
            return JsonResponse({'message':'NO_FILES'}, status = 400)