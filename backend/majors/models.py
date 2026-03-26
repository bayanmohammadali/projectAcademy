from django.db import models

from academic.models import University

class Major(models.Model):
    name = models.CharField(max_length=255)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="majors"
    )

    def __str__(self):
        return self.name