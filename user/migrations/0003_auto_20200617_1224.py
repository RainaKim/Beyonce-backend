# Generated by Django 3.0.6 on 2020-06-17 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200615_0501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followuser',
            name='follower',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='following', to='user.User'),
        ),
        migrations.AlterField(
            model_name='followuser',
            name='following',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='follower', to='user.User'),
        ),
    ]