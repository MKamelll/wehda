from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from staff import models
from staff.forms import (
    AddressForm,
    AddressFormSet,
    DoctorDetailsFormSet,
    EmploymentGradeForm,
    EmploymentGradeFormSet,
    QualificationForm,
    QualificationFormSet,
    SecondedRecordFormSet,
)


# Register your models here.
@admin.register(models.Institution)
class InstituitionAdmin(admin.ModelAdmin[models.Institution]):
    search_fields = ("name",)

    def has_module_permission(self, _request: HttpRequest) -> bool:
        return False


class AddressInline(admin.StackedInline[models.Address, models.Employee]):
    model = models.Address
    formset = AddressFormSet
    form = AddressForm
    can_delete = True
    extra = 0


@admin.register(models.HealthUnit)
class HealthUnitAdmin(admin.ModelAdmin[models.HealthUnit]):
    list_display = (
        "name",
        "code",
        "health_admin",
        "number_of_residents",
        "number_of_clinics",
    )

    search_fields = ("name", "code", "health_admin")

    inlines = [AddressInline]


class DoctorDetailsInline(admin.StackedInline[models.DoctorDetails, models.Employee]):
    model = models.DoctorDetails
    formset = DoctorDetailsFormSet
    can_delete = True
    extra = 0
    max_num = 1


class QualificationInline(admin.StackedInline[models.Qualification, models.Employee]):
    model = models.Qualification
    formset = QualificationFormSet
    form = QualificationForm
    can_delete = True
    extra = 0
    autocomplete_fields = ["institution"]


class EmploymentGradeInline(
    admin.StackedInline[models.EmploymentGrade, models.Employee]
):
    model = models.EmploymentGrade
    formset = EmploymentGradeFormSet
    form = EmploymentGradeForm
    can_delete = True
    extra = 0


class AddonTaskInline(admin.StackedInline[models.AddonTask, models.Employee]):
    model = models.AddonTask
    can_delete = True
    extra = 0


class SecondedRecordInline(admin.StackedInline[models.SecondedRecord, models.Employee]):
    model = models.SecondedRecord
    formset = SecondedRecordFormSet
    ordering = ("-start_date",)
    can_delete = False
    extra = 0


class AdditionalDegreeInline(
    admin.StackedInline[models.AdditionalDegree, models.Employee]
):
    model = models.AdditionalDegree
    extra = 0
    can_delete = True
    autocomplete_fields = ["institution"]


class TrainingCertificationInline(
    admin.StackedInline[models.TrainingCertification, models.Employee]
):
    model = models.TrainingCertification
    extra = 0
    can_delete = True
    autocomplete_fields = ["institution"]


@admin.register(models.Employee)
class EmployeeModelAdmin(admin.ModelAdmin[models.Employee]):
    list_display = ("name", "job_title", "appointment_type", "is_active")

    list_filter = ("appointment_type", "job_title")

    search_fields = ("name", "national_id", "addon_tasks__name")
    inlines = [
        AddressInline,
        QualificationInline,
        EmploymentGradeInline,
        DoctorDetailsInline,
        SecondedRecordInline,
        AdditionalDegreeInline,
        TrainingCertificationInline,
        AddonTaskInline,
    ]
