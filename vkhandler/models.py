from django.db import models


class Group(models.Model):
    group = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=50)


class Settings(models.Model):
    chat_id = models.CharField(max_length=250)
    admin_access = models.BooleanField(default=True)
    add_class = models.BooleanField(default=True)
    add_time = models.BooleanField(default=True)
    add_teacher = models.BooleanField(default=True)
    buttons = models.BooleanField(default=True)
    autosend = models.BooleanField(default=False)
    autosend_time = models.CharField(default='22:00', max_length=10)
    notify_update = models.BooleanField(default=True)


class Notify(models.Model):
    chat_id = models.CharField(max_length=250)
    count = models.IntegerField(default=0)
    name = models.CharField(max_length=250)
    text = models.TextField(max_length=5000)
    urls = models.ManyToManyField('NotifyUrls', related_name='Notifies')


class NotifyUrls(models.Model):
    chat_id = models.CharField(max_length=250)
    url = models.CharField(max_length=500)


class NotifyGroup(models.Model):
    group = models.CharField(max_length=250)
    album_id = models.CharField(max_length=255)


class PushGroup(models.Model):
    name = models.CharField(max_length=250)
    chat_id = models.CharField(max_length=250)
    users = models.JSONField()
