from django.core.files import File
from django.core.management.base import BaseCommand
from Authentication.models import CityProblem, MayorCities, User, Cities, CityProblemReaction
from django.conf import settings
import os
import random

class Command(BaseCommand):
    help = 'Create reports'
    def handle(self, *args, **kwargs):
        mayor = User.objects.filter(Type='Mayor').first()
        c1 = Cities.objects.filter(id=341).first()
        c2 = Cities.objects.filter(id=240).first()
        mcity = MayorCities(User=mayor, City=c1)
        mcity.save()
        mcity = MayorCities(User=mayor, City=c2)
        mcity.save()
        citizen = User.objects.filter(Email='citizen@gmail.com').first()
        citizen2 = User.objects.filter(Email='citizen2@gmail.com').first()
        citizen3 = User.objects.filter(Email='citizen3@gmail.com').first()
        citizen4 = User.objects.filter(Email='citizen4@gmail.com').first()
        citizen5 = User.objects.filter(Email='citizen5@gmail.com').first()
        citizen6 = User.objects.filter(Email='citizen6@gmail.com').first()
        citizens = User.objects.filter(Type='Citizen').all()
        image_path = os.path.join(settings.MEDIA_ROOT, '3.jpg')
        video_path = os.path.join(settings.MEDIA_ROOT, '1.mp4')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='سطح جاده آسفالت نشده و خطرناک است. لطفاً برای جلوگیری از حوادث اقدام کنید.', Reporter=citizen,
                                Type='Street', Longitude=2.33234766, Latitude=43, FullAdress='خیابان لاله زار')
            cprob.Picture.save('3.jpg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '4.jpg')           
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='چراغ‌های خیابان از کار افتاده‌اند و شب‌ها کاملا تاریک است', Reporter=citizen2,
                                Type='Lighting', Longitude=100, Latitude=97.1, FullAdress='خیابان ولیعصر، بین خیابان‌های انقلاب و آزادی')
            cprob.Picture.save('4.jpg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '5.jpeg')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='زباله‌های زیادی انباشته شده است و این موضوع آلودگی محیط شده است.', Reporter=citizen6,
                                Type='Garbage', Longitude=2, Latitude=4, FullAdress='میدان امام حسین، جلوی فروشگاه آتی شهر')
            cprob.Picture.save('5.jpeg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '6.jpg')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='تجهیزات ورزشی پارک آسیب دیده و قابل استفاده نیستند. لطفاً برای تعمیر اقدام کنید.', Reporter=citizen5,
                                Type='Other', Longitude=2.33234766, Latitude=43, FullAdress='محله شهرک غرب')
            cprob.Picture.save('6.jpg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '7.jpg')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c2, Information='چراغ‌های مسیرهای پیاده‌روی در باغ لاله‌ها از کار افتاده‌اند.', Reporter=citizen3,
                                Type='Lighting', Longitude=0, Latitude=0, FullAdress='بلوار چمران (جنوب به شمال)، بعد از میدان امام حسین')
            cprob.Picture.save('7.jpg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()
        image_path = os.path.join(settings.MEDIA_ROOT, '8.jpg')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c2, Information='زباله‌های زیادی در کنار سطل‌های زباله زمین بدمینتون باغ فاتح انباشته شده است', Reporter=citizen4,
                                Type='Garbage', Longitude=0, Latitude=0, FullAdress='جهانشهر، جنب بلوار جمهوری، نرسیده به میدان سپاه')
            cprob.Picture.save('8.jpg', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.full_clean()
            cprob.save()

        self.stdout.write(self.style.SUCCESS('Successfully created all reports'))

        cprobes = CityProblem.objects.all()
        for cprobe in cprobes:
            for cz in citizens:
                liked = random.choice([True, False])
                CityProblemReaction(CityProblem=cprobe, Like=liked, Reactor=cz).save()

        self.stdout.write(self.style.SUCCESS('Successfully created likes and dislikes'))