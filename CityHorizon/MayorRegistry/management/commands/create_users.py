from django.core.files import File
from django.core.management.base import BaseCommand
from Authentication.models import User
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Create users'
    def handle(self, *args, **kwargs):
        user = User(FullName="علی مرادی", Email="citizen@gmail.com", Type='Citizen', Verified=True)
        user.set_password('citizen')
        user.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '2.jpg')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            user = User(FullName="مجید احمدی", Email="mayor@gmail.com", Type='Mayor')
            user.set_password('mayor')
            user.Picture.save('2.jpg', django_file, save=False)
            user.save()
        user =  User(FullName="محسن معین‌فر", Email="acc.of.soccer@gmail.com", Type='Admin')
        user.set_password('admin')
        user.save()
        user = User(FullName="رضا محمدی", Email="reza.m1746@gmail.com", Type='Admin')
        user.set_password('admin')
        user.save()
        user = User(FullName="پارسا ایمانی", Email="parsaimani495@gmail.com", Type='Admin')
        user.set_password('admin')
        user.save()
        user = User(FullName="ارسلان دوست زنگنه", Email="a_doost@comp.iust.ac.ir", Type='Admin')
        user.set_password('admin')
        user.save()
        self.stdout.write(self.style.SUCCESS('created users successfully'))