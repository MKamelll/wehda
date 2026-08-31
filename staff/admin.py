from django.contrib import admin

from staff import models


# Register your models here.
class AdditionalDegreeInline(
    admin.TabularInline[models.AdditionalDegree, models.Employee]
):
    model = models.AdditionalDegree
    extra = 0


class TrainingCertificationInline(
    admin.TabularInline[models.TrainingCertification, models.Employee]
):
    model = models.TrainingCertification
    extra = 0


@admin.register(models.Employee)
class EmployeeModelAdmin(admin.ModelAdmin[models.Employee]):
    inlines = [AdditionalDegreeInline, TrainingCertificationInline]
