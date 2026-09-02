from typing import Any
from xml.dom import ValidationErr

from django.forms import BaseInlineFormSet, ValidationError

from staff.models import SecondedRecord, Speciality


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


class SpecialityFormSet(BaseInlineFormSet[Speciality, Any]):
    def clean(self) -> None:
        super().clean()
        job_title = self.instance.job_title

        if job_title == "doctor" and not hasattr(self.instance, "speciality"):
            raise ValidationError("يجب إضافة تخصص للطبيب البشري")
        if job_title != "doctor" and hasattr(self.instance, "speciality"):
            raise ValidationError("التخصص للطبيب البشري فقط")
