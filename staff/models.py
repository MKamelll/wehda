from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    national_id = models.PositiveIntegerField(
        verbose_name=_("الرقم القومي"),
        validators=[MaxValueValidator(999_999_999_999_99)],
    )

    phone_number = PhoneNumberField(region="EG", verbose_name=_("رقم الهاتف"))
    birth_date = models.DateField(verbose_name=_("تاريخ الميلاد"))
    job_start_date = models.DateField(verbose_name=_("تاريخ استلام العمل"))
    first_hire_date = models.DateField(verbose_name=_("تاريخ أول تعيين"))
    email = models.EmailField(
        verbose_name=_("البريد الالكتروني"), blank=True, null=True
    )
    address = models.CharField(max_length=255, verbose_name=_("العنوان"))
    practice_license_number = models.IntegerField(
        verbose_name=_("رقم ترخيص مزاولة المهنة"), blank=True, null=True
    )
    social_status = models.CharField(max_length=50, verbose_name=_("الحالة الاجتماعية"))
    work_at = models.CharField(
        max_length=255, default=_("محلة أبو علي"), verbose_name=_("مكان العمل")
    )

    class Meta:
        verbose_name = _("الموظف")
        verbose_name_plural = _("الموظفين")


class Doctor(models.Model):
    employee = models.OneToOneField(
        to=Employee, related_name="doctor_details", on_delete=models.CASCADE
    )
    speciality = models.CharField(max_length=255, verbose_name=_("التخصص"))

    class Meta:
        verbose_name = _("الطبيب البشري")
        verbose_name_plural = _("الأطباء البشري")


class Nurse(models.Model):
    employee = models.OneToOneField(
        to=Employee, related_name="nurse_details", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("الممرضة")
        verbose_name_plural = _("الممرضات")


class NurseAddonJob(models.Model):
    nurse = models.ForeignKey(
        to=Nurse, related_name="nurse_addon_job", on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = _("المهمة الإضافية للممرضة")
        verbose_name_plural = _("المهمات الإضافية للممرضات")


class Dentist(models.Model):
    employee = models.OneToOneField(
        to=Employee, related_name="dentist_details", on_delete=models.CASCADE
    )


class EmploymentGrade(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    date = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    employee = models.ForeignKey(
        to=Employee, on_delete=models.PROTECT, related_name="employment_grade"
    )

    class Meta:
        verbose_name = _("الدرجة الوظيفية")
        verbose_name_plural = _("الدرجات الوظيفية")


class Institution(models.Model):
    class InstitutionChoices(models.TextChoices):
        UNIVERSITY = "uni", _("جامعة")
        SCHOOL = "sch", _("مدرسة")
        INSTITUTION = "ini", _("معهد")

    kind = models.CharField(choices=InstitutionChoices.choices, verbose_name=_("النوع"))
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))

    class Meta:
        verbose_name = _("المؤسسة")
        verbose_name_plural = _("المؤسسات")


class Degree(models.Model):
    employee = models.ForeignKey(
        to=Employee, on_delete=models.PROTECT, related_name="graduation"
    )
    year = models.PositiveIntegerField(
        verbose_name="السنة",
        blank=True,
        null=True,
        validators=[MaxValueValidator(9999)],
    )
    institution = models.ForeignKey(
        to=Institution, on_delete=models.PROTECT, related_name="graduation"
    )
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))

    class Meta:
        verbose_name = _("المؤهل الأساسي")
        verbose_name_plural = _("المؤهلات الأساسية")


class SecondedDetails(models.Model):
    original = models.CharField(max_length=255, verbose_name=_("مكان عملها الأصلي"))
    date = models.DateField(verbose_name=_("تاريخ الانتداب"))
    employee = models.OneToOneField(
        to=Employee, on_delete=models.PROTECT, related_name="seconded_details"
    )

    class Meta:
        verbose_name = _("تفاصيل الانتداب")
        verbose_name_plural = _("تفاصيل الانتدابات")


class EmploymentStatus(models.Model):
    class EmploymentChoices(models.TextChoices):
        basic = "b", _("أساسي")
        seconded = "s", _("انتداب")

    employee = models.OneToOneField(
        to=Employee, on_delete=models.PROTECT, related_name="employment_type"
    )
    status = models.CharField(
        choices=EmploymentChoices.choices, verbose_name=_("أساسي/انتداب")
    )

    class Meta:
        verbose_name = _("حالة العمالة")
        verbose_name_plural = _("حالات العمالة")


class AdditionalDegree(models.Model):
    class DegreeChoices(models.TextChoices):
        DIPLOMA = "diploma", _("دبلومة")
        MASTER = "master", _("ماجستير")
        PHD = "phd", _("دكتوراه")
        fellowship = "fellowship", _("زمالة")

    degree = models.CharField(choices=DegreeChoices.choices, verbose_name=_("الدرجة"))
    field_of_study = models.CharField(max_length=255, verbose_name=_("مجال الدراسة"))
    date_of_certification = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    institution = models.CharField(max_length=255, verbose_name=_("المؤسسة/الجامعة"))
    employee = models.ForeignKey(
        to=Employee, on_delete=models.PROTECT, related_name="additional_degrees"
    )

    class Meta:
        verbose_name = _("المؤهل الإضافي")
        verbose_name_plural = _("المؤهلات الإضافية")


class TrainingCertification(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    date_of_certification = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    institution = models.CharField(max_length=255, verbose_name=_("مكان الحصول عليها"))
    employee = models.ForeignKey(
        to=Employee, on_delete=models.PROTECT, related_name="training_certifications"
    )

    class Meta:
        verbose_name = _("الدورة التدريبية")
        verbose_name_plural = _("الدورات التدريبية")
