from __future__ import annotations
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Employee(models.Model):
    class ServiceStatusChoices(models.TextChoices):
        ACTIVE = "active", _("على رأس العمل")
        RESIGNED = "resigned", _("استقالة")
        RETIRED = "retired", _("تقاعد")
        TERMINATED = "terminated", _("إنهاء خدمة")
        TRANSFERRED = "transferred", _("نقل خدمات")

    class JobTitlesChoices(models.TextChoices):
        DOCTOR = "doctor", _("طبيب بشري")
        DENTIST = "dentist", _("طبيب أسنان")
        PHARMACIST = "pharmacist", _("صيدلي")
        NURSE = "nurse", _("ممرض/ة")
        HEALTH_INSPECTOR = "health_inspector", _("مراقب صحي")
        HEALTH_REGISTER = "health_register", _("كاتب صحة")
        LAB_TECHNICIAN = "lab_technician", _("فني معمل")
        COMMUNITY_HEALTH_WORKER = "community_health_worker", _("رائدة ريفية")
        SEASONAL_WORKER = "seasonal_worker", _("عامل موسمي")
        GENERAL_REGISTER = "general_register", _("كاتب")
        GENERAL_WORKER = "general_worker", _("عامل")
        ENGINEERING_TECHNICIAN = "engineering_technician", _("فني هندسي")

    class MaritalStatus(models.TextChoices):
        SINGLE = "SINGLE", _("أعزب / عزباء")
        MARRIED = "MARRIED", _("متزوج / متزوجة")
        DIVORCED = "DIVORCED", _("مطلق / مطلقة")
        WIDOWED = "WIDOWED", _("أرمل / أرملة")

    class AppointmentTypeChoices(models.TextChoices):
        BASIC = "b", _("أساسي")
        SECONDED = "s", _("انتداب")

    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    job_title = models.CharField(
        default=JobTitlesChoices.DOCTOR,
        choices=JobTitlesChoices.choices,
        verbose_name=_("الوظيفة"),
    )
    national_id = models.CharField(max_length=14, verbose_name=_("الرقم القومي"))
    phone_number = PhoneNumberField(region="EG", verbose_name=_("رقم الهاتف"))
    birth_date = models.DateField(verbose_name=_("تاريخ الميلاد"))
    job_start_date = models.DateField(verbose_name=_("تاريخ استلام العمل"))
    first_hire_date = models.DateField(verbose_name=_("تاريخ أول تعيين"))
    email = models.EmailField(
        verbose_name=_("البريد الالكتروني"), blank=True, null=True
    )

    practice_license_number = models.CharField(
        max_length=255, verbose_name=_("رقم ترخيص مزاولة المهنة"), blank=True, null=True
    )
    marital_status = models.CharField(
        default=MaritalStatus.SINGLE,
        choices=MaritalStatus.choices,
        verbose_name=_("الحالة الاجتماعية"),
    )
    work_at = models.CharField(
        max_length=255, default=_("محلة أبو علي"), verbose_name=_("مكان العمل")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    service_status = models.CharField(
        choices=ServiceStatusChoices.choices,
        default=ServiceStatusChoices.ACTIVE,
        verbose_name=_("حالة الخدمة"),
    )
    end_of_service_date = models.DateField(
        blank=True, null=True, verbose_name=_("تاريخ انتهاء الخدمة")
    )
    appointment_type = models.CharField(
        choices=AppointmentTypeChoices.choices,
        verbose_name=_("أساسي/انتداب"),
        default=AppointmentTypeChoices.BASIC,
    )

    @property
    def current_grade(self) -> EmploymentGrade | None:
        return self.employment_grades.order_by("-date").first()

    @property
    def current_secondment(self) -> SecondedRecord | None:
        if self.appointment_type == "s":
            return self.secondment_history.filter(end_date__isnull=True).first()
        return None

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("موظفين")


class Address(models.Model):
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="addresses"
    )
    village = models.CharField(
        max_length=255, verbose_name=_("مركز"), blank=True, default=""
    )
    city = models.CharField(max_length=255, verbose_name=_("مدينة"), default="دسوق")
    governate = models.CharField(
        max_length=255, verbose_name=_("محافظة"), default="كفر الشيخ"
    )

    def __str__(self) -> str:
        return f"{self.village}, {self.city}, {self.governate}"

    class Meta:
        verbose_name = _("عنوان")
        verbose_name_plural = _("عناوين")


class DoctorDetails(models.Model):
    class MedicalSpecialtyChoices(models.TextChoices):
        # --- Internal Medicine & General ---
        GENERAL_PRACTITIONER = "GP", _("General Practitioner (طبيب عام)")
        INTERNAL_MEDICINE = "INT_MED", _(
            "Internal Medicine Specialist (طبيب أمراض باطنية)"
        )
        CARDIOLOGIST = "CARD", _("Cardiologist (طبيب أمراض القلب)")
        GASTROENTEROLOGIST = "GAST", _(
            "Gastroenterologist (طبيب الجهاز الهضمي والمجاري الكبدية)"
        )
        PULMONOLOGIST = "PULM", _("Pulmonologist (طبيب أمراض الصدر والجهاز التنفسي)")
        NEUROLOGIST = "NEUR", _("Neurologist (طبيب أمراض المخ والأعصاب - باطني)")
        NEPHROLOGIST = "NEPH", _("Nephrologist (طبيب أمراض الكلى)")
        ENDOCRINOLOGIST = "ENDO", _("Endocrinologist (طبيب الغدد الصماء والسكري)")
        RHEUMATOLOGIST = "RHEUM", _("Rheumatologist (طبيب أمراض الروماتيزم والمفاصل)")
        HEMATOLOGIST = "HEMA", _("Hematologist (طبيب أمراض الدم)")
        ONCOLOGIST = "ONCO", _("Oncologist (طبيب أورام)")
        DERMATOLOGIST = "DERM", _("Dermatologist (طبيب الأمراض الجلدية)")

        # --- Surgical Specialties ---
        GENERAL_SURGEON = "GEN_SURG", _("General Surgeon (جراح عام)")
        ORTHOPEDIC_SURGEON = "ORTHO", _("Orthopedic Surgeon (جراح عظام)")
        NEUROSURGEON = "NEUR_SURG", _("Neurosurgeon (جراح مخ وأعصاب)")
        CARDIOTHORACIC_SURGEON = "CARD_SURG", _(
            "Cardiothoracic Surgeon (جراح القلب والصدر)"
        )
        PLASTIC_SURGEON = "PLAS_SURG", _("Plastic Surgeon (جراح تجميل)")
        UROLOGIST = "UROL", _("Urologist (طبيب وجراح المسالك البولية والتناسلية)")
        OPHTHALMOLOGIST = "OPHTH", _("Ophthalmologist (طبيب وجراح العيون - الرمد)")
        ENT_SPECIALIST = "ENT", _(
            "Otolaryngologist / ENT Specialist (طبيب وجراح الأذن والأنف والحنجرة)"
        )

        # --- Specialized Patient Care ---
        PEDIATRICIAN = "PED", _("Pediatrician (طبيب أطفال)")
        NEONATOLOGIST = "NEO", _("Neonatologist (طبيب حديثي الولادة والمبتسرين)")
        OB_GYN = "OBGYN", _(
            "Obstetrician and Gynecologist (طبيب أمراض النساء والتوليد)"
        )
        GERIATRICIAN = "GERI", _("Geriatrician (طبيب أمراض الشيخوخة وكبار السن)")

        # --- Diagnostic & Support Specialties ---
        RADIOLOGIST = "RAD", _("Radiologist (طبيب الأشعة والتصوير الطبي)")
        PATHOLOGIST = "PATH", _("Pathologist (طبيب علم الأمراض والتحاليل)")
        ANESTHESIOLOGIST = "ANES", _("Anesthesiologist (طبيب التخدير والعناية المركزة)")
        PSYCHIATRIST = "PSYCH", _("Psychiatrist (طبيب نفسي)")

    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="doctor_details"
    )
    speciality = models.CharField(
        choices=MedicalSpecialtyChoices.choices, verbose_name=_("التخصص")
    )

    def __str__(self):
        return f"{self.get_speciality_display()}"

    class Meta:
        verbose_name = _("تفاصيل طبيب بشري")
        verbose_name_plural = _("تفاصيل أطباء بشري")


class AddonTask(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("اسم المهمة"))
    employee = models.ForeignKey(
        to=Employee, related_name="addon_tasks", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = _("مهمة إضافية")
        verbose_name_plural = _("مهام إضافية")


class EmploymentGrade(models.Model):
    class GradeChoices(models.TextChoices):
        DEGREE_6 = "G6", _("الدرجة السادسة")
        DEGREE_5 = "G5", _("الدرجة الخامسة")
        DEGREE_4 = "G4", _("الدرجة الرابعة")
        DEGREE_3 = "G3", _("الدرجة الثالثة")
        DEGREE_2 = "G2", _("الدرجة الثانية")
        DEGREE_1 = "G1", _("الدرجة الأولى")
        DEGREE_K = "K", _("درجة كبير")

    name = models.CharField(
        choices=GradeChoices.choices,
        default=GradeChoices.DEGREE_3,
        verbose_name=_("اسم الدرجة"),
    )
    date = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="employment_grades"
    )

    def __str__(self) -> str:
        return self.get_name_display()

    class Meta:
        verbose_name = _("درجة وظيفية")
        verbose_name_plural = _("درجات وظيفية")
        ordering = ["-date"]


class Institution(models.Model):
    class InstitutionChoices(models.TextChoices):
        UNIVERSITY = "uni", _("جامعة")
        SCHOOL = "sch", _("مدرسة")
        INSTITUTION = "ini", _("معهد")

    kind = models.CharField(
        default=InstitutionChoices.UNIVERSITY,
        choices=InstitutionChoices.choices,
        verbose_name=_("النوع"),
    )
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))

    def __str__(self) -> str:
        return f"{self.get_kind_display()} {self.name}"

    class Meta:
        verbose_name = _("مؤسسة")
        verbose_name_plural = _("مؤسسات")


class FieldOfStudy(models.Model):
    class FieldChoices(models.TextChoices):
        # === 1. MEDICAL & HEALTH SECTOR ===
        HUMAN_MEDICINE = "MED_HUMAN", _("Human Medicine - الطب البشري")
        DENTISTRY = "MED_DENT", _("Dentistry - طب وجراحة الفم والأسنان")
        PHARMACY = "MED_PHARM", _("Pharmacy - الصيدلة")
        PHYSICAL_THERAPY = "MED_PHYSTH", _("Physical Therapy - العلاج الطبيعي")
        NURSING = "MED_NURS", _("Nursing - التمريض")
        APPLIED_HEALTH = "MED_APPLIED", _(
            "Applied Health Sciences - تكنولوجيا العلوم الصحية التطبيقية"
        )

        # === 2. ENGINEERING & TECHNOLOGY SECTOR ===
        ENGINEERING = "ENG_MAIN", _("Engineering - الهندسة")
        COMPUTERS_AI = "TECH_COMP_AI", _(
            "Computers, Information & AI - الحاسبات والمعلومات والذكاء الاصطناعي"
        )
        TECHNOLOGICAL_UNI = "TECH_UNI", _(
            "Technological Universities - الجامعات التكنولوجية"
        )

        # === 3. SCIENCE & AGRICULTURE SECTOR ===
        BASIC_SCIENCES = "SCI_BASIC", _("Basic Sciences - العلوم الأساسية")
        AGRICULTURE = "SCI_AGRI", _("Agriculture - الزراعة")
        FISHERIES = "SCI_FISH", _("Fisheries & Aquaculture - الثروة السمكية والمصايد")
        VETERINARY = "SCI_VET", _("Veterinary Medicine - الطب البيطري")

        # === 4. HUMANITIES, ARTS & LANGUAGES SECTOR ===
        ARTS_HUMANITIES = "ART_HUMAN", _("Arts & Humanities - الآداب")
        LANGUAGES_TRANSLATION = "ART_LANG", _(
            "Languages & Translation - الألسن واللغات والترجمة"
        )
        ARCHAEOLOGY = "ART_ARCH", _("Archaeology - الآثار")

        # === 5. SOCIAL, ADMINISTRATIVE & LEGAL SCIENCES ===
        COMMERCE_BUSINESS = "SOC_COMMERCE", _(
            "Commerce & Business Administration - التجارة وإدارة الأعمال"
        )
        LAW_SHARIA = "SOC_LAW", _("Law & Sharia - الحقوق والشريعة والقانون")
        ECONOMICS_POLSCI = "SOC_ECON_POL", _(
            "Economics & Political Science - الاقتصاد والعلوم السياسية"
        )
        MASS_COMMUNICATION = "SOC_MEDIA", _("Mass Communication & Media - الإعلام")

        # === 6. CREATIVE ARTS & DESIGN SECTOR ===
        FINE_ARTS = "CRE_FINE", _("Fine Arts - الفنون الجميلة")
        APPLIED_ARTS = "CRE_APPLIED", _("Applied Arts - الفنون التطبيقية")
        ART_MUSIC_EDUCATION = "CRE_EDU", _(
            "Art & Music Education - التربية الموسيقية والفنية"
        )

        # === 7. OTHER SPECIALIZED SECTORS ===
        EDUCATION = "SPEC_EDU", _("Education (Teacher Prep) - التربية")
        TOURISM_HOTELS = "SPEC_TOUR", _("Tourism & Hotels - السياحة والفنادق")
        PHYSICAL_EDUCATION = "SPEC_SPORTS", _("Physical Education - التربية الرياضية")
        OTHER = "OTHER", _("أخري")

    name = models.CharField(
        choices=FieldChoices,
        verbose_name=_("اسم المجال"),
        default=FieldChoices.HUMAN_MEDICINE,
    )

    def __str__(self) -> str:
        return self.get_name_display()

    class Meta:
        verbose_name = _("مجال دراسة")
        verbose_name_plural = _("مجالات الدراسة")


class Qualification(models.Model):
    class QualificationChoices(models.TextChoices):
        # المؤهلات العالية
        BACHELOR = "BACHELOR", _("بكالوريوس")
        LICENTIATE = "LICENTIATE", _("ليسانس")
        PROFESSIONAL_DEGREE = "PROFESSIONAL_DEGREE", _("بكالوريوس/ليسانس مهني")

        # المؤهلات فوق المتوسطة
        UPPER_INTERMEDIATE_TECHNICAL = "UPPER_INTERMEDIATE_TECHNICAL", _(
            "دبلوم معهد فني فوق متوسط"
        )
        UPPER_INTERMEDIATE_ADMIN = "UPPER_INTERMEDIATE_ADMIN", _(
            "دبلوم معهد إداري/سياحي فوق متوسط"
        )

        # المؤهلات المتوسطة
        HIGH_SCHOOL = "HIGH_SCHOOL", _("ثانوية عامة")
        AZHAR_HIGH_SCHOOL = "AZHAR_HIGH_SCHOOL", _("ثانوية أزهري")
        TECHNICAL_DIPLOMA_3YR = "TECHNICAL_DIPLOMA_3YR", _("دبلوم فني 3 سنوات")

        # المؤهلات أقل من متوسطة
        PREPARATORY_SCHOOL = "PREPARATORY_SCHOOL", _("شهادة إعدادية")
        TECHNICAL_DIPLOMA_5YR = "TECHNICAL_DIPLOMA_5YR", _("دبلوم فني متقدم 5 سنوات")

    employee = models.OneToOneField(
        to=Employee, on_delete=models.CASCADE, related_name="qualification"
    )
    year = models.PositiveIntegerField(
        verbose_name=_("سنة التخرج"),
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.date.today().year + 10),
        ],
        null=True,
        blank=True,
    )
    institution = models.ForeignKey(
        to=Institution,
        on_delete=models.PROTECT,
        related_name="qualifications",
        verbose_name=_("المؤسسة"),
    )
    name = models.CharField(
        default=QualificationChoices.BACHELOR,
        choices=QualificationChoices.choices,
        verbose_name=_("اسم المؤهل"),
    )

    field_of_study = models.OneToOneField(
        to=FieldOfStudy, verbose_name=_("مجال الدراسة"), on_delete=models.PROTECT
    )

    def __str__(self) -> str:
        return self.get_name_display()

    class Meta:
        verbose_name = _("مؤهل أساسي")
        verbose_name_plural = _("مؤهلات أساسية")


class SecondedRecord(models.Model):
    original_workplace = models.CharField(
        max_length=255, verbose_name=_("مكان العمل الأصلي")
    )
    start_date = models.DateField(verbose_name=_("تاريخ بدأ الانتداب"))
    end_date = models.DateField(
        verbose_name=_("تاريخ انتهاء الانتداب"), null=True, blank=True
    )
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="secondment_history"
    )

    def __str__(self) -> str:
        return f"{self.original_workplace}/{self.start_date}->{self.end_date}"

    class Meta:
        verbose_name = _("سجل الانتداب")
        verbose_name_plural = _("سجلات الانتدابات")
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                condition=models.Q(end_date__isnull=True),
                name="unique_active_secondment_per_employee",
            ),
            models.UniqueConstraint(
                fields=["employee", "start_date"],
                name="unique_secondment_start_date_per_employee",
            ),
        ]


class AdditionalDegree(models.Model):
    class DegreeChoices(models.TextChoices):
        DIPLOMA = "diploma", _("دبلومة")
        MASTER = "master", _("ماجستير")
        PHD = "phd", _("دكتوراه")
        fellowship = "fellowship", _("زمالة")

    name = models.CharField(
        default=DegreeChoices.DIPLOMA,
        choices=DegreeChoices.choices,
        verbose_name=_("الدرجة"),
    )
    field_of_study = models.OneToOneField(
        to=FieldOfStudy, verbose_name=_("مجال الدراسة"), on_delete=models.PROTECT
    )
    date_of_certification = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    institution = models.ForeignKey(
        to=Institution, related_name="additional_degrees", on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="additional_degrees"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("مؤهل إضافي")
        verbose_name_plural = _("مؤهلات إضافية")


class TrainingCertification(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    date_of_certification = models.DateField(verbose_name=_("تاريخ الحصول عليها"))
    institution = models.OneToOneField(
        to=Institution, verbose_name=_("مكان الحصول عليها"), on_delete=models.PROTECT
    )
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="training_certifications"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("دورة تدريبية")
        verbose_name_plural = _("دورات تدريبية")
