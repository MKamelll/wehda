from pickle import FALSE
from typing import Any

from django import forms
from django.forms import BaseInlineFormSet, ValidationError
from django.utils.translation import gettext_lazy as _

from staff.models import (
    Address,
    DoctorDetails,
    EmploymentGrade,
    Qualification,
    SecondedRecord,
)


class DoctorDetailsFormSet(BaseInlineFormSet[DoctorDetails, Any]):
    def clean(self):
        super().clean()
        job_title = self.instance.job_title
        has_data = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )
        if job_title == "doctor" and not has_data:
            raise ValidationError("يجب إضافة تفاصيل للطبيب البشري")
        if job_title != "doctor" and has_data:
            raise ValidationError("تفاصيل الطبيب خاصة بالبشري فقط")


class SecondedRecordFormSet(BaseInlineFormSet[SecondedRecord, Any]):
    def clean(self) -> None:
        super().clean()
        appointment_type = self.instance.appointment_type
        has_data = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )

        if appointment_type == "b" and has_data:
            raise ValidationError("لا يمكن إضافة انتداب إلي موظف أساسي")
        if appointment_type == "s" and not has_data:
            raise ValidationError("يجب إضافة تفاصيل انتداب لموظف الانتداب")


class QualificationForm(forms.ModelForm[Qualification]):
    class Meta:
        model = Qualification
        fields = "__all__"

    def clean(self) -> dict[str, Any] | None:
        clean_data = super().clean()
        if not clean_data:
            return None

        name = clean_data.get("name")
        field_of_study = clean_data.get("field_of_study")

        if clean_data.get("DELETE"):
            return clean_data

        return clean_data


class QualificationFormSet(BaseInlineFormSet[Qualification, Any]):
    def clean(self) -> None:
        super().clean()
        has_qualification = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )
        if not has_qualification:
            raise ValidationError("يجب إضافة مؤهل أساسي للموظف")

        no_field_of_study = [
            "HIGH_SCHOOL",
            "AZHAR_HIGH_SCHOOL",
            "PREPARATORY_SCHOOL",
        ]

        for form in self.forms:
            name = form.cleaned_data.get("name")
            field_of_study = form.cleaned_data.get("field_of_study")

            if name and name in no_field_of_study and field_of_study:
                raise ValidationError(
                    _("لا يمكن تحديد تخصص لشهادة الثانوية العامة أو الأزهرية")
                )

            if name and name not in no_field_of_study and not field_of_study:
                raise ValidationError(_("يجب اختيار مجال الدراسة"))


class EmploymentGradeForm(forms.ModelForm):
    class Meta:
        model = EmploymentGrade
        fields = ("name", "date")

    def has_changed(self):
        return True


class EmploymentGradeFormSet(BaseInlineFormSet[EmploymentGrade, Any]):
    def clean(self) -> None:
        super().clean()
        has_grade = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )
        if not has_grade:
            raise ValidationError("يجب إضافة درجة وظيفية واحدة علي الأقل")
