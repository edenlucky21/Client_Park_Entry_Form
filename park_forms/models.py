from django.db import models
import json
from django.utils import timezone


class ParkEntryForm(models.Model):
    FORM_TYPES = [
        ('tourist', 'Tourist'),
        ('transit', 'Transit'),
        ('student', 'Student'),
    ]

    VISITOR_TYPES = [
        ('FNR', 'Foreign Non-Resident'),
        ('FR', 'Foreign Resident'),
        ('ROA', 'Rest of Africa'),
        ('EAC', 'East African Community'),
        ('CHILD', 'Child'),
    ]

    form_type = models.CharField(max_length=20, choices=FORM_TYPES)
    visitor_type = models.CharField(max_length=10, choices=VISITOR_TYPES)
    data = models.JSONField()  # Store structured form data
    date_submitted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.form_type} - {self.visitor_type} - {self.date_submitted.date()}"

    class Meta:
        ordering = ['-date_submitted']