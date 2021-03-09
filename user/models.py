from django.db import models

class User(models.Model):
    first_name              = models.CharField(max_length=45)
    last_name               = models.CharField(max_length=45)
    occupation              = models.CharField(max_length=45, null=True)
    current_company         = models.CharField(max_length=45, null=True)
    my_website              = models.URLField(max_length=2000, null=True)
    about_me                = models.OneToOneField('AboutMe', on_delete=models.SET_NULL, null=True)
    work_experience         = models.ForeignKey('WorkExperience', on_delete=models.SET_NULL, null=True)
    location                = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)
    profile_img_url         = models.URLField(max_length=2000,null = True)
    social_account          = models.CharField(max_length=100)
    created_at              = models.DateTimeField(auto_now_add = True, null = True)
    team                    = models.ManyToManyField('Team', through='UserTeam', related_name = 'member')
    following_user          = models.ManyToManyField('self', through='FollowUser', related_name = 'follower_user')
    following_team          = models.ManyToManyField('Team', through='FollowTeam', related_name = 'follower_team')
    following_field         = models.ManyToManyField('feed.Field', through='FollowField', related_name = 'follower_field')
    following_moodboard     = models.ManyToManyField('MoodBoard', through='FollowMoodBoard', related_name = 'follower_moodboard')
    social_media_link       = models.ManyToManyField('SocialMediaLink', through='UserSocialMediaLink')
    moodboard               = models.ManyToManyField('MoodBoard', through='MoodBoardUser', related_name = 'owner')

    class Meta:
        db_table = 'users'


class AboutMe(models.Model):
    title           = models.CharField(max_length=100)
    description     = models.CharField(max_length=200)

    class Meta:
        db_table = 'aboutme'


class Location(models.Model):
    country = models.CharField(max_length=45)
    state   = models.CharField(max_length=45, null=True)
    city    = models.CharField(max_length=45)

    class Meta:
        db_table = 'locations'


class WorkExperience(models.Model):
    company         = models.CharField(max_length=45, null=True)
    company_url     = models.URLField(max_length=2000, null=True)
    position        = models.CharField(max_length=45, null=True)
    start_date      = models.DateField(null=True)
    end_date        = models.DateField(null=True)
    detail          = models.CharField(max_length=2000, null=True)
    location        = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'work_experiences'


class UserTeam(models.Model):
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    team        = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True)
    status      = models.BooleanField(default=False)
    is_admin    = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_teams'


class Team(models.Model):
    name                = models.CharField(max_length=45)
    team_url            = models.CharField(max_length=1000)
    location            = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    invite_only         = models.BooleanField(default=False)
    team_info           = models.CharField(max_length=2000, null=True)
    team_img_url        = models.URLField(max_length=2000, null=True)
    social_media_link   = models.ManyToManyField('SocialMediaLink', through = 'TeamSocialMediaLink')

    class Meta:
        db_table = 'teams'

class TeamSocialMediaLink(models.Model):
    team                = models.ForeignKey(Team, on_delete = models.SET_NULL, null = True)
    social_media_link   = models.ForeignKey('SocialMediaLink', on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'teams_social_media_links'

class UserSocialMediaLink(models.Model):
    user                = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    social_media_link   = models.ForeignKey('SocialMediaLink', on_delete=models.SET_NULL, null=True)
    link                = models.CharField(max_length=2000, null=True)
    team                = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'users_social_media_links'


class SocialMediaLink(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'social_media_links'

class FollowUser(models.Model):
    follower            = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, related_name = 'following')
    following           = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, related_name = 'follower')

    class Meta:
        db_table = 'follow_users'

class FollowMoodBoard(models.Model):
    follower            = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    following           = models.ForeignKey('MoodBoard', on_delete = models.SET_NULL, null=True)

    class Meta:
        db_table = 'follow_moodboards'

class FollowField(models.Model):
    follower            = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    following           = models.ForeignKey('feed.Field', on_delete = models.SET_NULL, null= True)

    class Meta:
        db_table = 'follow_fields'

class FollowTeam(models.Model):
    follower            = models.ForeignKey(User, on_delete = models.SET_NULL, null = True)
    following           = models.ForeignKey(Team, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'follow_teams'

class MoodBoard(models.Model):
    name                = models.CharField(max_length=45)
    is_private          = models.BooleanField(default=False)

    class Meta:
        db_table = 'moodboards'


class MoodBoardUser(models.Model):
    moodboard   = models.ForeignKey(MoodBoard, on_delete=models.SET_NULL, null=True)
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status      = models.BooleanField(default=False)

    class Meta:
        db_table = 'moodboards_users'
