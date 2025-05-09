from rest_framework import serializers
from Authentication.models import User, Notification, CityProblemReaction, CityProblem, Comment, CommentReaction
import datetime
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField, F, Value, CharField
from django.db.models import Count, Case, When, IntegerField, F, Subquery, OuterRef
from datetime import timedelta
from calendar import monthrange

class NotoficationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    Message = serializers.CharField()
    CityProblemID = serializers.IntegerField(source='CityProblem.id')
    Date = serializers.DateTimeField()
    Seen = serializers.BooleanField()
    SenderID = serializers.CharField(source='Sender.id')
    SenderFullName = serializers.CharField(source='Sender.FullName')

class CityProblemReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityProblemReaction
        fields = ['Like']

class PointsSerializer(serializers.Serializer):
    Sum_of_Reports = serializers.SerializerMethodField()
    Sum_of_Points = serializers.SerializerMethodField()
    Monthly_Points = serializers.SerializerMethodField()
    Users_Ranking = serializers.SerializerMethodField()
    User_Rank = serializers.IntegerField(read_only=True)  # Set as read_only to prevent input

    class Meta:
        fields = ['Sum_of_Reports', 'Sum_of_Points', 'Monthly_Points', 'Users_Ranking', 'User_Rank']

    def get_Sum_of_Reports(self, obj):
        return CityProblem.objects.filter(Reporter=obj).count()

    def get_Sum_of_Points(self, obj):
        likes = CityProblemReaction.objects.filter(CityProblem__Reporter=obj, Like=True).count()
        dislikes = CityProblemReaction.objects.filter(CityProblem__Reporter=obj, Like=False).count()
        return likes - dislikes

    def get_Monthly_Points(self, obj):
        now = timezone.now()
        result = {}
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        for i in range(5):
            month_start = current_month_start
            if i > 0:
                month_start = (current_month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            year, month = month_start.year, month_start.month
            _, last_day = monthrange(year, month)
            month_end = month_start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            reactions = CityProblemReaction.objects.filter(
                CityProblem__Reporter=obj,
                Date__gte=month_start,
                Date__lte=month_end
            )

            likes = reactions.filter(Like=True).count()
            dislikes = reactions.filter(Like=False).count()

            month_key = month_start.strftime('%Y-%m')
            result[month_key] = likes - dislikes
            current_month_start = month_start

        return result

    def get_Users_Ranking(self, obj):
        # Get points for users with CityProblem records and Type='Citizen'
        points_data = CityProblem.objects.filter(
            Reporter__Type='Citizen'
        ).values('Reporter').annotate(
            likes=Count(Case(When(cityproblemreaction__Like=True, then=1), output_field=IntegerField())),
            dislikes=Count(Case(When(cityproblemreaction__Like=False, then=1), output_field=IntegerField())),
            points=F('likes') - F('dislikes'),
        )

        # Create a dictionary to store points for users with problems
        user_points = {data['Reporter']: data['points'] for data in points_data}

        # Get all Citizen users
        citizen_users = User.objects.filter(Type='Citizen')

        # Build a list of all users with their points
        all_users = []
        for user in citizen_users:
            points = user_points.get(user.id, 0)  # Default to 0 if no points
            picture_url = user.Picture.url if user.Picture else None
            all_users.append({
                'id': user.id,
                'FullName': user.FullName,  # Directly access FullName field
                'Picture': picture_url,
                'points': points,
                'is_current_user': user.id == obj.id
            })

        # Sort users by points in descending order
        all_users.sort(key=lambda x: x['points'], reverse=True)

        # Assign ranks
        result = []
        rank = 1
        previous_points = None
        user_rank = None

        for user in all_users:
            points = user['points']
            # Update rank if points differ
            if previous_points is not None and points != previous_points:
                rank = len(result) + 1
            previous_points = points
            result.append({
                'FullName': user['FullName'],
                'Picture': user['Picture'],
                'points': points,
                'rank': rank,
                'is_current_user': user['is_current_user']
            })
            # Store rank for current user
            if user['is_current_user']:
                user_rank = rank

        # Store user_rank for User_Rank field
        self._user_rank = user_rank if user_rank is not None else rank

        return result

    def to_representation(self, instance):
        # Override to_representation to include User_Rank
        ret = super().to_representation(instance)
        ret['User_Rank'] = getattr(self, '_user_rank', None)
        return ret

class CommentOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    SenderName = serializers.CharField(source='Sender.FullName')
    SenderPicture = serializers.ImageField(source='Sender.Picture')
    SenderType = serializers.CharField(source='Sender.Type')
    Content = serializers.CharField()
    HasOwnership = serializers.SerializerMethodField()

    def get_HasOwnership(self, obj):
        if 'userid' in self.context:
            user = User.objects.filter(id=self.context['userid']).first()
            if user is None:
                return None
            return user.id == obj.Sender.id
        return None

class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    SenderName = serializers.CharField(source='Sender.FullName')
    SenderPicture = serializers.ImageField(source='Sender.Picture')
    SenderType = serializers.CharField(source='Sender.Type')
    Content = serializers.CharField()
    Replies = serializers.SerializerMethodField()
    Likes = serializers.SerializerMethodField()
    DisLikes = serializers.SerializerMethodField()
    HasOwnership = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'SenderName', 'SenderPicture', 'Content', 'Reply', 'Likes', 'DisLikes', 'HasOwnership']

    def get_Replies(self, obj):
        # if obj.IsAReply:
        #     comment = Comment.objects.filter(CityProblem=obj.CityProblem,id=obj.ReplyID).first()
        #     if comment is None:
        #         return None
        #     user = User.objects.filter(id=self.context['userid']).first()
        #     if not user:
        #         return CommentOnlySerializer(comment).data
        #     return CommentOnlySerializer(comment, context={'userid':user.id}).data
        # return None
        comments = Comment.objects.filter(CityProblem=obj.CityProblem, ReplyID=obj.id).all()
        user = User.objects.filter(id=self.context['userid']).first()
        if not user:
            return CommentOnlySerializer(comments, many=True).data
        return CommentOnlySerializer(comments, many=True, context={'userid': user.id}).data

    def get_Likes(self, obj):
        return CommentReaction.objects.filter(Comment=obj, Like=True).count()

    def get_DisLikes(self, obj):
        return CommentReaction.objects.filter(Comment=obj, Like=False).count()

    def get_HasOwnership(self, obj):
        if 'userid' in self.context:
            user = User.objects.filter(id=self.context['userid']).first()
            if user is None:
                return None
            return user.id == obj.Sender.id
        return None

class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ['Like']