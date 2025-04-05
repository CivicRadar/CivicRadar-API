from django.core.files import File
from django.core.management.base import BaseCommand
from Authentication.models import CityProblem, MayorCities, User, Cities
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Create reports'
    def handle(self, *args, **kwargs):
        mayor = User.objects.filter(Type='Mayor').first()
        c1 = Cities.objects.filter(id=1).first()
        c2 = Cities.objects.filter(id=2).first()
        c3 = Cities.objects.filter(id=3).first()
        mcity = MayorCities(User=mayor, City=c1)
        mcity.save()
        mcity = MayorCities(User=mayor, City=c2)
        mcity.save()
        citizen = User.objects.filter(Type='Citizen').first()
        image_path = os.path.join(settings.MEDIA_ROOT, '1.png')
        video_path = os.path.join(settings.MEDIA_ROOT, '1.mp4')
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='There is a problem in the intersection', Reporter=citizen,
                                Type='Lighting', Longitude=2.33234766, Latitude=43, FullAdress='خیابان میزرایی کوچه سوم غربی')
            cprob.Picture.save('1.png', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.save()
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c2, Information='There is a problem in the street', Reporter=citizen,
                                Type='Street', Longitude=100, Latitude=97.1, FullAdress='بزرگراه شهید مدنی')
            cprob.Picture.save('1.png', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.save()
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c1, Information='There is a problem in the intersection', Reporter=citizen,
                                Type='Lighting', Longitude=2, Latitude=4, FullAdress='آزادراه حجازی')
            cprob.Picture.save('1.png', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.save()
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c2, Information='There is a problem in the street', Reporter=citizen,
                                Type='Street', Longitude=2.33234766, Latitude=43, FullAdress='کمربندی شمالی جنب فروشگاه افق کوروش')
            cprob.Picture.save('1.png', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.save()
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            cprob = CityProblem(City=c3, Information='There is a problem in the intersection', Reporter=citizen,
                                Type='Lighting', Longitude=0, Latitude=0, FullAdress='فلکه گوهردشت بلوار میرزایی پور')
            cprob.Picture.save('1.png', django_file, save=False)
        with open(video_path, 'rb') as vid_file:
            django_file = File(vid_file)
            cprob.Video.save('1.mp4', django_file, save=False)
            cprob.save()

        self.stdout.write(self.style.SUCCESS('Successfully created all reports'))