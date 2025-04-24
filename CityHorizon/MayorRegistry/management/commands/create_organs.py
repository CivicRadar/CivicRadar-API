from django.core.management.base import BaseCommand
from Authentication.models import Cities, Organization
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Create organizations'

    def handle(self, *args, **kwargs):
        cities = Cities.objects.all()
        names = [
            "علی", "محمد", "حسین", "رضا", "امیر",
            "محمود", "ناصر", "عباس", "احمد", "مصطفی",
            "یوسف", "سینا", "پویا", "آرمین", "بهنام",
            "کیان", "سامان", "امیرحسین", "مهدی", "سجاد",
            "پرهام", "آریا", "سیاوش", "کامران", "بهرام",
            "فرهاد", "شایان", "آرش", "پارسا", "کیانوش",
            "داریوش", "آرمان", "فربد", "کوروش", "هومن",
            "امیرعلی", "سهیل", "نیما", "پرهام", "بهزاد",
            "فریدون", "اشکان", "آرین", "پریا", "کیوان",
            "سام", "بیژن", "پرویز", "جمشید", "کیومرث",
            "مانی", "سپهر", "آرتین", "بهروز", "فریبرز",
            "امیرمهدی", "سامان", "پرهام", "بهزاد", "فریدون"
        ]
        last_names = [
            "محمدی", "حسینی", "احمدی", "رضایی", "علیزاده",
            "جعفری", "کریمی", "یوسفی", "سلیمانی", "شاهین",
            "فرهادی", "نجفی", "قاسمی", "موسوی", "رستمی",
            "صادقی", "حیدری", "سلطانی", "امیری", "نوروزی",
            "میرزایی", "رحیمی", "حسین‌زاده", "عباسی", "ملکی",
            "اسدی", "صفوی", "شریفی", "یزدانی", "طاهری",
            "بهرامی", "فروغی", "نعمتی", "سلیمی", "عطایی",
            "محمدپور", "امینی", "شاهمرادی", "قادری", "صمدی",
            "نجاتی", "مرادی", "رضوانی", "صالحی", "اسفندیاری",
            "مهدوی", "فرجاد", "نوری", "اسکندری", "مهران"
        ]
        fake = Faker()
        cnt = 0
        num = 0

        for city in cities:
            for org_type in ['Waste', 'Water', 'Gas', 'Electricity']:
                first_name = random.choice(names)
                last_name = random.choice(last_names)
                full_name = f"{first_name} {last_name}"
                email = fake.free_email()
                number = '09' + ''.join(random.choices('1234567890', k=9))
                organization = Organization(
                    Type=org_type,
                    OrganHead_FullName=full_name,
                    OrganHead_Email=email,
                    OrganHead_Number=number,
                    City=city
                )
                organization.save()

            cnt += 1
            if cnt >= 100:
                num += 1
                cnt = 0
                self.stdout.write(self.style.SUCCESS(f'{num}'))