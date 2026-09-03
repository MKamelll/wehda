from typing import Any

from django import forms
from django.forms import BaseInlineFormSet, ValidationError
from django.utils.translation import gettext_lazy as _

from staff.models import EmploymentGrade, Qualification, SecondedRecord, Speciality


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

        no_field_of_study = [
            "HIGH_SCHOOL",
            "AZHAR_HIGH_SCHOOL",
            "PREPARATORY_SCHOOL",
        ]

        if name and name in no_field_of_study and field_of_study:
            self.add_error(
                "field_of_study",
                _("لا يمكن تحديد تخصص لشهادة الثانوية العامة أو الأزهرية"),
            )

        if name and name not in no_field_of_study and not field_of_study:
            self.add_error("field_of_study", _("هذا الحقل مطلوب للمؤهلات العليا"))

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


class EmploymentGradeFormSet(BaseInlineFormSet[EmploymentGrade, Any]):
    def clean(self) -> None:
        super().clean()
        has_grade = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )
        if not has_grade:
            raise ValidationError("يجب إضافة درجة وظيفية واحدة علي الأقل")


class SpecialityFormSet(BaseInlineFormSet[Speciality, Any]):
    def clean(self) -> None:
        super().clean()
        job_title = self.instance.job_title

        has_speciality = any(
            form.cleaned_data and not form.cleaned_data.get("DELETE", False)
            for form in self.forms
        )

        if job_title == "doctor" and not has_speciality:
            raise ValidationError("يجب إضافة تخصص للطبيب البشري")
        if job_title != "doctor" and has_speciality:
            raise ValidationError("التخصص للطبيب البشري فقط")
