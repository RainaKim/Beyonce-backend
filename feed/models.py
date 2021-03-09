from django.db import models
from user.models import User, MoodBoard, Team


class Feed(models.Model):
    name        = models.CharField(max_length=100, null=True)
    created_at  = models.DateTimeField(auto_now_add=True, null = True)
    view        = models.IntegerField(default=0)
    description = models.CharField(max_length=2000, null=True)
    cover_url   = models.URLField(max_length=2000)
    content     = models.TextField(null = True)
    color       = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True)
    owner       = models.ManyToManyField(User, through='UserFeed', related_name = 'owner_feed')
    commenter   = models.ManyToManyField(User, through='Comment', related_name = 'commenter_feed')
    liker       = models.ManyToManyField(User, through='Like', related_name = 'liker_feed')
    field       = models.ManyToManyField('Field', through='FeedField')
    text_tool   = models.ManyToManyField('TextTool', through='FeedTextTool')
    image_tool  = models.ManyToManyField('ImageTool', through='FeedImageTool')
    tag         = models.ManyToManyField('HashTag', through='FeedHashTag', related_name = 'tagged_feed')
    moodboard   = models.ManyToManyField(MoodBoard, through='MoodBoardFeed')
    team        = models.ManyToManyField(Team, through = 'TeamFeed')

    class Meta:
        db_table = 'feeds'

class UserFeed(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    feed    = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        db_table = 'users_feeds'

class TeamFeed(models.Model):
    team    = models.ForeignKey(Team, on_delete = models.CASCADE)
    feed    = models.ForeignKey(Feed, on_delete = models.CASCADE)

    class Meta:
        db_table = 'teams_feeds'

class Image(models.Model):
    img_url = models.URLField(max_length = 2000)
    feed    = models.ForeignKey('Feed', on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'images'

class Field(models.Model):
    name = models.CharField(max_length=45)
    is_main = models.BooleanField(default = 0)
    related_to = models.ForeignKey('self', on_delete = models.SET_NULL, null = True, related_name = 'sub_category')
    description = models.CharField(max_length = 200, null = True)

    class Meta:
        db_table = 'fields'

class FeedField(models.Model):
    feed        = models.ForeignKey(Feed, on_delete=models.CASCADE)
    field       = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'feeds_fields'

class Comment(models.Model):
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    feed        = models.ForeignKey(Feed, on_delete=models.SET_NULL, null=True)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'

class HashTag(models.Model):
    name    = models.CharField(max_length=45)

    class Meta:
        db_table = 'hashtags'

class FeedHashTag(models.Model):
    feed    = models.ForeignKey(Feed, on_delete = models.SET_NULL, null = True)
    hashtag = models.ForeignKey(HashTag, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'feeds_hashtags'

class Like(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    feed    = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        db_table = 'likes'

class ImageTool(models.Model):
    icon_url        = models.URLField(max_length=2000)

    class Meta:
        db_table = 'image_tools'

class FeedImageTool(models.Model):
    feed        = models.ForeignKey(Feed, on_delete=models.SET_NULL, null=True)
    image_tool  = models.ForeignKey(ImageTool, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'feeds_image_tools'

class TextTool(models.Model):
    name        = models.CharField(max_length = 45)

    class Meta:
        db_table = 'text_tools'

class FeedTextTool(models.Model):
    feed        = models.ForeignKey(Feed, on_delete = models.SET_NULL, null = True)
    text_tool   = models.ForeignKey(TextTool, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'feeds_text_tools'


class MoodBoardFeed(models.Model):
    moodboard   = models.ForeignKey(MoodBoard, on_delete=models.SET_NULL, null=True)
    feed        = models.ForeignKey(Feed, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'moodboards_feeds'

class Color(models.Model):
    rvalue = models.IntegerField(default=0)
    gvalue = models.IntegerField(default=0)
    bvalue = models.IntegerField(default=0)

    class Meta:
        db_table = 'colors'

