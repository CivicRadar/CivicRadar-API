from django.db import models
from Authentication.models import User
import uuid

class MayorReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Mayor = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField(auto_now_add=True)
    problem_status_pie_chart = models.ImageField(upload_to='charts/problem_status/', null=True, blank=True)
    problem_type_bar_chart = models.ImageField(upload_to='charts/problem_type/', null=True, blank=True)
    engagement_bar_chart = models.ImageField(upload_to='charts/engagement/', null=True, blank=True)
    resolved_over_time_line_chart = models.ImageField(upload_to='charts/resolved_over_time/', null=True, blank=True)
    transition_time_bar_chart = models.ImageField(upload_to='charts/transition_time/', null=True, blank=True)

