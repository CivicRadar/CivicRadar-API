from django.contrib.staticfiles.views import serve
from django.db.models import Count
from django.shortcuts import render
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import (CityProblem, ReportCitizen, MayorCities, User, Cities, MayorNote,
                                   Notification, MayorPriority, Organization, Provinces, ReportCitizen)
from .serializers import (CityProblemSerializer, ReportCitizenSerializer, NoteSerializer, MayorPrioritySerializer,
                          MayorCompleteCityProblemSerializer, OrganizationSerializer, CityProblemCountSerializer, ProvinceProblemCountSerializer,
                          HandleCRCSerializer)
import jwt, datetime



class CitizenReportProblem(APIView):
    def post(self, request):
        # citizen posts a report
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        city = Cities.objects.filter(id=request.data['CityID']).first()
        if city is None:
            raise AuthenticationFailed("City not found!")
        problem = CityProblem(City=city, Information=request.data['Information'], Reporter=user, Type=request.data['Type'],
                              Picture=request.data['Picture'], Video=request.data['Video'], Longitude=request.data['Longitude'], Latitude=request.data['Latitude'], FullAdress=request.data['FullAdress'])

        problem.save()
        serializer = CityProblemSerializer(problem, context={'userID':user.id})
        return Response(serializer.data)

    def get(self, request):
        # citizen gets all his/her reports
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        problems = CityProblem.objects.filter(Reporter=user).all()
        serializer = CityProblemSerializer(problems, many=True, context={'userID':user.id})
        return Response(serializer.data)

class CitizenReportCitizen(APIView):
    def post(self, request):
        # citizen invalidates other citizen reports
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        problem = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if problem is None:
            raise AuthenticationFailed("Problem not found!")
        reportedalready = ReportCitizen.objects.filter(Reported=problem, Reporter=user).first()
        if reportedalready is not None:
            raise AuthenticationFailed("Problem already reported!")
        report = ReportCitizen(Report=request.data['Report'], Reported=problem, Reporter=user)
        report.save()
        serializer = ReportCitizenSerializer(report)
        return Response(serializer.data)

    def get(self, request):
        # citizen gets all his/her reports toward other citizens
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        CityProblemID = request.query_params.get('CityProblemID')
        if not CityProblemID:
            problems = CityProblem.objects.filter(Reporter=user).all()
            serializer = CityProblemSerializer(problems, many=True, context={'userID':user.id})
            return Response(serializer.data)
        cprobe = CityProblem.objects.filter(id=CityProblemID).first()
        if not cprobe:
            raise AuthenticationFailed("Problem not found!")
        rp = ReportCitizen.objects.filter(Reporter=user, Reported=cprobe).first()
        if not rp:
            return Response({"Answer": "you haven't reported this problem"})
        return Response({"Answer": "you have reported this problem"})

class AllCitizenReport(APIView):
    def get(self, request):
        # everybody regradless to their auth token can see all the city problems
        token = request.COOKIES.get('jwt')

        if not token:
            problems = CityProblem.objects.all()
            serializer = CityProblemSerializer(problems, many=True)
            return Response(serializer.data)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        problems = CityProblem.objects.all()
        serializer = CityProblemSerializer(problems, many=True, context={'userID':user.id})
        return Response(serializer.data)

class HandleCRC(APIView):
    def delete(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            problems = CityProblem.objects.all()
            serializer = CityProblemSerializer(problems, many=True)
            return Response(serializer.data)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type="Admin").first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        cprobeid = ReportCitizen.objects.filter(Reported__id=request.data['CityProblemID']).first()
        if not cprobeid:
            raise AuthenticationFailed("Problem ID not found!")

        cprobe = CityProblem.objects.filter(id=cprobeid.Reported.id).first()
        if not cprobe:
            raise AuthenticationFailed("Problem not found!")

        notif = Notification(Message=f'شهروند گرامی، گزارش شهری شما در مکان {cprobe.FullAdress} توسط سایر شهروندان به عنوان تخلف ثبت شده است. پس از بررسی‌های لازم، این گزارش توسط ادمین سیستم شهرسنج حذف گردید.',
                             Receiver=cprobe.Reporter,
                             CityProblem=cprobe,
                             UpdatedTo='Deleted',
                             Sender=user).save()
        cprobe.delete()
        return Response({"Answer": "Deleted Successfully!"})

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            problems = CityProblem.objects.all()
            serializer = CityProblemSerializer(problems, many=True)
            return Response(serializer.data)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type="Admin").first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        cprobeids = ReportCitizen.objects.values_list('Reported__id', flat=True)
        cprobes = CityProblem.objects.filter(id__in=cprobeids).all()
        serializer = HandleCRCSerializer(cprobes, many=True)
        return Response(serializer.data)

    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            problems = CityProblem.objects.all()
            serializer = CityProblemSerializer(problems, many=True)
            return Response(serializer.data)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type="Admin").first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cprobeid = ReportCitizen.objects.filter(Reported__id=request.data['CityProblemID']).first()
        if not cprobeid:
            raise AuthenticationFailed("Problem ID not found!")

        cprobe = CityProblem.objects.filter(id=cprobeid.Reported.id).first()
        if not cprobe:
            raise AuthenticationFailed("Problem not found!")
        rcs = ReportCitizen.objects.filter(Reported__id=cprobe.id).all()
        for rc in rcs:
            rc.delete()
        return Response({"Answer": "Deleted wrong infractions successfully!"})

class PublicReport(APIView):
    def get(self, request):
        problem = CityProblem.objects.filter(id=request.query_params.get('CityProblem_ID')).first()
        if not problem:
            raise AuthenticationFailed("Problem not found!")
        serializer = CityProblemSerializer(problem)
        return Response(serializer.data)

class MayorCityReports(APIView):
    def get(self, request):
        # mayor can get the reports in his/her terriority
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        problems = CityProblem.objects.filter(City__id__in=cities).all()
        serializer = MayorCompleteCityProblemSerializer(problems, many=True, context={'userID':user.id})
        return Response(serializer.data)

class MayorNotes(APIView):
    def get(self, request):
        # Mayor can see all his/her notes
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        CityProblemID = request.query_params.get('CityProblemID')
        if not CityProblemID:
            return Response({"error": "CityProblemID is required"}, status=400)

        try:
            cprob = CityProblem.objects.get(id=CityProblemID)
        except CityProblem.DoesNotExist:
            return Response({"error": "City Problem not found!"}, status=404)

        notes = MayorNote.objects.filter(CityProblem=cprob).all()
        serializer = NoteSerializer(notes, many=True, context={'userid': user.id})
        return Response(serializer.data)

    def post(self, request):
        # Mayor can add a note for the report
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        cityproblem = CityProblem.objects.filter(id=request.data['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("Problem not found!")

        mayorcities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        if cityproblem.City.id not in mayorcities:
            raise AuthenticationFailed("This Problem does not belong to you!")

        note = MayorNote(NoteOwner=user, Information=request.data['Information'], CityProblem=cityproblem)
        note.save()
        serializer = NoteSerializer(note, context={'userid': user.id})
        return Response(serializer.data)

    def put(self, request):
        # Mayor can update his/her note for the report
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        note = MayorNote.objects.filter(id=request.data['NoteID'], NoteOwner=user).first()
        if note is None:
            raise AuthenticationFailed("Note not found!")

        note.Information = request.data['Information']
        note.save()
        serializer = NoteSerializer(note, context={'userid': user.id})
        return Response(serializer.data)

    def delete(self, request):
        # Mayor can update his/her note for the report
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        note = MayorNote.objects.filter(id=request.data['NoteID'], NoteOwner=user).first()
        if note is None:
            raise AuthenticationFailed("Note not found!")

        note.delete()

        return Response({'success': 'note deleted successfully'})

class MayorDetermineCityProblemSituation(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        cityproblem = CityProblem.objects.filter(City__id__in=cities, id=request.data['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("city problem not found or does not belong to you!")
        newsituation = request.data['NewSituation']
        mydict = {
            'PendingReview': ' در انتظار برای بررسی می باشد',
            'UnderConsideration': ' در حال بررسی است',
            'IssueResolved': ' حل شد'
        }
        if newsituation not in mydict:
            raise AuthenticationFailed("your newsituation is not defined")
        if newsituation == cityproblem.Status:
            pass
        elif (cityproblem.Status == 'UnderConsideration' and newsituation=='PendingReview') or cityproblem.Status == 'IssueResolved':
            raise AuthenticationFailed("reverting Problem situations is prohibited!")
        else:
            notif = Notification(Message=f'مشکل گزارش شده از طرف شما توسط شهردار مربوطه{mydict[newsituation]}',
                                 Receiver=cityproblem.Reporter,
                                 Sender=user,
                                 CityProblem=cityproblem,
                                 UpdatedTo=newsituation)
            notif.full_clean()
            notif.save()
            cityproblem.Status=newsituation
            cityproblem.save()
        serializer = CityProblemSerializer(cityproblem, context={'userID':user.id})
        return Response(serializer.data)

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        CityProblemID = request.query_params.get('CityProblemID')
        cityproblem = CityProblem.objects.filter(City__id__in=cities, id=CityProblemID).first()
        if cityproblem is None:
            raise AuthenticationFailed("city problem not found or does not belong to you!")
        if cityproblem.Status ==  'PendingReview':
            resp = Response({'Status': cityproblem.Status,
                'PossibleChanges':{'PendingReview',
                                     'UnderConsideration',
                                     'IssueResolved'}})
            return resp
        elif cityproblem.situation =='UnderConsideration':
            resp = Response({'Status': cityproblem.Status,
                'PossibleChanges':{'UnderConsideration',
                                     'IssueResolved'}})
            return resp
        resp = Response({'Status': cityproblem.Status,
            'PossibleChanges':{'IssueResolved'}})
        return resp

class MayorPrioritize(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        cityproblem = CityProblem.objects.filter(City__id__in=cities, id=request.data['CityProblemID']).first()
        if cityproblem is None:
            raise AuthenticationFailed("city problem not found or does not belong to you!")
        mayorprio = MayorPriority.objects.filter(Mayor=user, CityProblem=cityproblem).first()
        if mayorprio is not None:
            mayorprio.Priority = request.data['Priority']
            mayorprio.full_clean()
            mayorprio.save()
            serializer = MayorPrioritySerializer(cityproblem, context={'userID': user.id})
            return Response(serializer.data)
        prio = MayorPriority(Mayor=user, CityProblem=cityproblem, Priority=request.data['Priority'])
        prio.full_clean()
        prio.save()
        serializer = MayorPrioritySerializer(cityproblem, context={'userID': user.id})
        return Response(serializer.data)

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        cityproblem = CityProblem.objects.filter(City__id__in=cities).all()
        serializer = MayorPrioritySerializer(cityproblem, many=True, context={'userID': user.id})
        return Response(serializer.data)

class MayorDelegate(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        cityprobe_id = request.query_params.get('CityProblemID')
        cityprobe = CityProblem.objects.filter(id=cityprobe_id).first()
        if cityprobe is None:
            raise AuthenticationFailed("city problem not found or does not belong to you!")

        organs = Organization.objects.filter(City=cityprobe.City, Owner=user).all()
        Serializer = OrganizationSerializer(organs, many=True)
        return Response(Serializer.data)

    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        city = Cities.objects.filter(id=request.data['CityID']).first()
        if not city:
            raise AuthenticationFailed("City not found!")
        organ = Organization(Type=request.data['Type'], Owner=user,
                             OrganHead_FullName=request.data['OrganHead_FullName'],
                             OrganHead_Email=request.data['OrganHead_Email'],
                             OrganHead_Number=request.data['OrganHead_Number'],
                             City=city)
        organ.full_clean()
        if len(organ.OrganHead_Number) != 11:
            raise AuthenticationFailed("PhoneNumber length should be 11!")
        if organ.OrganHead_Number[:2] != '09':
            raise AuthenticationFailed("PhoneNumber should start with 09!")
        organ.save()
        Serializer = OrganizationSerializer(organ)
        return Response(Serializer.data)

    def put(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        organ = Organization.objects.filter(id=request.data['MayorDelegate_ID'], Owner=user).first()
        if organ is None:
            raise AuthenticationFailed("Organization not found!")
        organ.Type = request.data['Type']
        organ.OrganHead_FullName = request.data['OrganHead_FullName']
        organ.OrganHead_Email = request.data['OrganHead_Email']
        organ.OrganHead_Number = request.data['OrganHead_Number']
        city = Cities.objects.filter(id=request.data['CityID']).first()
        if not city:
            raise AuthenticationFailed("City not found!")

        organ.City = city
        organ.full_clean()
        if len(organ.OrganHead_Number) != 11:
            raise AuthenticationFailed("PhoneNumber length should be 11!")
        if organ.OrganHead_Number[:2] != '09':
            raise AuthenticationFailed("PhoneNumber should start with 09!")
        organ.save()
        serializer = OrganizationSerializer(organ)
        return Response(serializer.data)

    def delete(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")

        organ = Organization.objects.filter(id=request.data['MayorDelegate_ID'], Owner=user).first()
        if organ is None:
            raise AuthenticationFailed("Organization not found!")

        organ.delete()
        return Response({'success': 'organ was deleted successfully!'})

class MayorDedicatedReportPage(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cityprobe_id = request.query_params.get('CityProblem_ID')
        problems = CityProblem.objects.filter(id=cityprobe_id).first()
        serializer = MayorCompleteCityProblemSerializer(problems, context={'userID':user.id})
        return Response(serializer.data)

class ReportCount(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Mayor').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        cities = MayorCities.objects.filter(User=user).values_list('City__id', flat=True)
        problems = CityProblem.objects.filter(City__id__in=cities).count()
        return Response({'count': problems})

class CityReportCount(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        myvar = request.query_params.get('City_ID')
        if myvar is None:
            raise AuthenticationFailed("variable name is wrong or value is null")
        city = Cities.objects.filter(id=myvar).first()
        if city is None:
            raise AuthenticationFailed("There is no such a city")
        problems = CityProblem.objects.filter(City__id=myvar).count()
        return Response({'count': problems, 'ProvinceName': city.Province.Name})

class ProvinceReportCount(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token!")

        user = User.objects.filter(id=payload['id'], Type='Citizen').first()
        if user is None:
            raise AuthenticationFailed("User not found!")
        myvar = request.query_params.get('Province_ID')
        if myvar is None:
            raise AuthenticationFailed("variable name is wrong or value is null")
        province = Provinces.objects.filter(id=myvar).first()
        if province is None:
            raise AuthenticationFailed("There is no such a city")
        problems = CityProblem.objects.filter(City__Province__id=myvar).count()
        return Response({'count': problems})

class CitiesReportCount(APIView):
    def get(self, request):
        query = Cities.objects.annotate(problems_count=Count('cityproblem')).order_by('id')
        serializer = CityProblemCountSerializer(query, many=True)
        return Response(serializer.data)

class ProvincesReportCount(APIView):
    def get(self, request):
        query = Provinces.objects.annotate(
            problems_count=Count('cities__cityproblem')
        ).order_by('Name')
        serializer = ProvinceProblemCountSerializer(query, many=True)
        return Response(serializer.data)

class ComplexReportCount(APIView):
    def get(self, request):
        myvar = request.query_params.get('Province_ID')
        if myvar is None:
            raise AuthenticationFailed("variable name is wrong or value is null")
        query = Cities.objects.filter(Province__id=myvar).annotate(problems_count=Count('cityproblem')).order_by('id')
        serializer = CityProblemCountSerializer(query, many=True)
        return Response(serializer.data)