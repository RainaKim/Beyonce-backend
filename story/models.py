from django.db import models
from user.models import User


class Story(models.Model):
    content_url     = models.URLField(max_length=2000)
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    user            = models.ManyToManyField(User, through='StoryView')
    tag             = models.ManyToManyField('Tag', through='StoryTag')

    class Meta:
        db_table = 'stories'

class Tag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'tags'

class StoryTag(models.Model):
    story   = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    tag     = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'stories_tags'

class StoryView(models.Model):
    user    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    story   = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'stories_views'

