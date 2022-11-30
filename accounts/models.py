from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.urls import reverse


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = 'M', '남성'
        FEMALE = 'F', '여성'

    follower_set = models.ManyToManyField('self', symmetrical=False, related_name='accounts_follower_set')
    following_set = models.ManyToManyField('self', symmetrical=False, related_name='accounts_following_set')

    website_url = models.URLField(blank=True)
    bio = models.CharField(blank=True, max_length=100)

    phone_number = models.CharField(max_length=11,
                                    blank=True,
                                    validators=[RegexValidator(r'^010[1-9]\d{3}\d{4}$')])
    gender = models.CharField(max_length=1, choices=GenderChoices.choices)
    avatar = models.ImageField(blank=True, upload_to='accounts/avatar/%Y/%m/%d')


    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return resolve_url('pydenticon_image', self.username)

    def welcome_mail_send(self):
        subject = render_to_string('accounts/welcome_mail_subject.txt', {
            'user': self
        })
        content = render_to_string('accounts/welcome_mail_content.txt', {
            'user': self
        })
        sender_mail = "email"
        send_mail(subject, content, sender_mail, [self.email], fail_silently=False)
