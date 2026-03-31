from django.db import models

class University(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    name = models.CharField(max_length=50)  # مثال: 2024/2025

    def __str__(self):
        return self.name
    
class Semester(models.Model):
    name = models.CharField(max_length=50)  # مثال: Fall, Spring
    term = models.IntegerField()            # 1, 2, 3
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="semesters"
    )
    def save(self, *args, **kwargs):
        # إذا هذا الفصل صار active → نطفي كل الفصول الثانية
        if self.is_active:
            Semester.objects.exclude(id=self.id).update(is_active=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

