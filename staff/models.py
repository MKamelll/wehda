from __future__ import annotations
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Address(models.Model):
    street = models.CharField(
        verbose_name=_("شارع"), max_length=255, default="", blank=True
    )
    village = models.CharField(
        max_length=255, verbose_name=_("مركز"), blank=True, default=""
    )
    city = models.CharField(
        max_length=255, verbose_name=_("مدينة"), default="دسوق", blank=True
    )
    governate = models.CharField(
        max_length=255, verbose_name=_("محافظة"), default="كفر الشيخ"
    )

    def __str__(self) -> str:
        s = f"{self.street}, " if self.street else ""
        v = f"{self.village}, " if self.village else ""
        c = f"{self.city}, " if self.city else ""
        return f"{s}{v}{c}{self.governate}"

    class Meta:
        verbose_name = _("عنوان")
        verbose_name_plural = _("عناوين")


class HealthUnit(models.Model):
    HEALTH_ADMIN_CHOICES = [
        (
            _("كفر الشيخ"),
            [
                ("desouq", _("دسوق")),
                ("kfs", _("كفر الشيخ")),
                ("mtoubs", _("مطوبس")),
                ("hamol", _("الحامول")),
                ("sidi_salem", _("سيدي سالم")),
                ("baltim", _("بلطيم")),
                ("foah", _("فوه")),
                ("kalin", _("قلين")),
                ("ryad", _("الرياض")),
                ("byala", _("بيلا")),
                ("sidi_ghazi", _("سيدي غازي")),
            ],
        ),
        (_("القاهرة"), [("bab_elsheria", _("باب الشعرية"))]),
    ]

    class HealthUnitKindChoices(models.TextChoices):
        UNIT = "unit", _("وحدة")
        HOSPITAL = "hospital", _("مستشفي")

    kind = models.CharField(
        verbose_name=_("النوع"),
        choices=HealthUnitKindChoices,
        default=HealthUnitKindChoices.UNIT,
    )
    name = models.CharField(verbose_name=_("الاسم"), max_length=255)
    code = models.CharField(
        verbose_name=_("الكود"), max_length=255, blank=True, default=""
    )
    health_admin = models.CharField(
        _("الإدارة الصحية"), max_length=255, choices=HEALTH_ADMIN_CHOICES
    )
    number_of_residents = models.PositiveIntegerField(
        _("عدد السكان"), blank=True, null=True
    )
    number_of_clinics = models.PositiveIntegerField(
        _("عدد العيادات"), blank=True, null=True
    )
    address = models.ForeignKey(
        to=Address,
        related_name="health_units",
        on_delete=models.PROTECT,
        verbose_name=_("العنوان"),
        null=True,
    )

    def __str__(self):
        return f"{self.get_kind_display()} {self.name}"

    class Meta:
        verbose_name = _("مؤسسة صحية")
        verbose_name_plural = _("مؤسسات صحية")


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
        NURSING_TECHNICIAN = "nursing_technician", _("فني تمريض")
        NURSING_SPECIALIST = "nursing_specialist", _("أخصائي تمريض")
        SENIOR_NURSING_SPECIALIST = "senior_nursing_specialist", _("أخصائي أول تمريض")
        NURSE_CONSULTANT = "nurse_consultant", _("استشاري تمريض")
        HEALTH_INSPECTOR = "health_inspector", _("مراقب صحي")
        HEALTH_REGISTER = "health_register", _("كاتب صحة")
        LAB_TECHNICIAN = "lab_technician", _("فني معمل")
        COMMUNITY_HEALTH_WORKER = "community_health_worker", _("رائدة ريفية")
        SEASONAL_WORKER = "seasonal_worker", _("عامل موسمي")
        GENERAL_REGISTER = "general_register", _("كاتب")
        GENERAL_WORKER = "general_worker", _("عامل")
        ENGINEERING_TECHNICIAN = "engineering_technician", _("فني هندسي")
        HEAD_NURSE = "head_nurse", _("رئيس التمريض")
        HEAD_PHARMACIST = "head_pharmacist", _("الصيدلي الأول")
        HEAD_OF_UNIT = "head_of_unit", _("مدير الوحدة")
        HEAD_DENTIST = "head_dentist", _("مدير الأسنان")

    class MaritalStatus(models.TextChoices):
        SINGLE = "SINGLE", _("أعزب / عزباء")
        MARRIED = "MARRIED", _("متزوج / متزوجة")
        DIVORCED = "DIVORCED", _("مطلق / مطلقة")
        WIDOWED = "WIDOWED", _("أرمل / أرملة")

    class AppointmentTypeChoices(models.TextChoices):
        BASIC = "b", _("أساسي")
        SECONDED = "s", _("انتداب")

    name = models.CharField(
        max_length=255, verbose_name=_("الاسم"), help_text="الاسم رباعي علي الأقل"
    )
    job_title = models.CharField(
        default=JobTitlesChoices.DOCTOR,
        choices=JobTitlesChoices.choices,
        verbose_name=_("الوظيفة"),
    )
    national_id = models.CharField(
        max_length=14, verbose_name=_("الرقم القومي"), help_text="تأكد من كتابة 14 رقم"
    )
    phone_number = PhoneNumberField(
        region="EG", verbose_name=_("رقم الهاتف"), help_text="تأكد من كتابة 11 رقم"
    )
    birth_date = models.DateField(
        verbose_name=_("تاريخ الميلاد"), help_text="YYYY-MM-DD"
    )
    job_start_date = models.DateField(
        verbose_name=_("تاريخ استلام العمل"),
        help_text="YYYY-MM-DD",
        null=True,
        blank=True,
    )
    first_hire_date = models.DateField(
        verbose_name=_("تاريخ أول تعيين"), help_text="YYYY-MM-DD", blank=True, null=True
    )
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
        blank=True,
        null=True,
        verbose_name=_("تاريخ انتهاء الخدمة"),
        help_text="YYYY-MM-DD",
    )
    appointment_type = models.CharField(
        choices=AppointmentTypeChoices.choices,
        verbose_name=_("أساسي/انتداب"),
        default=AppointmentTypeChoices.BASIC,
    )

    health_unit = models.ForeignKey(
        to=HealthUnit,
        verbose_name=_("الوحدة الصحية"),
        on_delete=models.CASCADE,
        related_name="employees",
    )

    address = models.ForeignKey(
        to=Address,
        related_name="employees",
        on_delete=models.PROTECT,
        verbose_name=_("العنوان"),
        null=True,
    )

    @property
    def current_grade(self) -> EmploymentGrade:
        return self.employment_grades.order_by("-date")[0]

    @property
    def current_grade_short(self) -> str:
        return str(self.current_grade).split(" ")[1]

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


class DoctorDetails(models.Model):
    class MedicalSpecialtyChoices(models.TextChoices):
        DEFAULT = "", _("اختر")
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
        choices=MedicalSpecialtyChoices.choices,
        verbose_name=_("التخصص"),
        help_text="خاص بالطبيب البشري فقط",
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
    date = models.DateField(
        verbose_name=_("تاريخ الحصول عليها"),
        null=True,
        blank=True,
        help_text="YYYY-MM-DD",
    )
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
        TRAINING_CENTER = "center", _("مركز تدريب")

    kind = models.CharField(
        default=InstitutionChoices.UNIVERSITY,
        choices=InstitutionChoices.choices,
        verbose_name=_("النوع"),
    )
    name = models.CharField(max_length=255, verbose_name=_("الاسم"))
    address = models.ForeignKey(
        to=Address,
        related_name="institutions",
        verbose_name="العنوان",
        on_delete=models.PROTECT,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.get_kind_display()} {self.name}"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("مؤسسة")
        verbose_name_plural = _("مؤسسات")


class Qualification(models.Model):
    class FieldChoices(models.TextChoices):
        DEFAULT = "", _("اختر")
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

    class QualificationChoices(models.TextChoices):
        BACHELOR = "BACHELOR", _("بكالوريوس")
        LICENTIATE = "LICENTIATE", _("ليسانس")
        PROFESSIONAL_DEGREE = "PROFESSIONAL_DEGREE", _("بكالوريوس/ليسانس مهني")

        HIGH_SCHOOL = "HIGH_SCHOOL", _("ثانوية عامة")
        AZHAR_HIGH_SCHOOL = "AZHAR_HIGH_SCHOOL", _("ثانوية أزهري")
        DIPLOMA_TRADING = "DIPLOMA_TRADING", _("دبلوم تجاري")
        DIPLOMA_NURSING = "DIPLOMA_NURSING", _("دبلوم تمريض")
        DIPLOMA_AGRICULTURAL = "DIPLOMA_AGRICULTURAL", _("دبلوم زراعي")
        DIPLOMA_INDUSTRIAL = "DIPLOMA_INDUSTRIAL", _("دبلوم صناعي")
        DIPLOMA_HOTEL = "DIPLOMA_HOTEL", _("دبلوم فندقي")
        DIPLOMA_COMMUNITY = "DIPLOMA_COMMUNITY", _("دبلوم خدمة اجتماعية")
        DIPLOMA_HEALTHCARE = "DIPLOMA_HEALTHCARE", _("دبلوم فني صحي")

        PREPARATORY_SCHOOL = "PREPARATORY_SCHOOL", _("شهادة إعدادية")
        CAN_READ = "CAN_READ", _("محو الأمية")

    employee = models.OneToOneField(
        to=Employee, on_delete=models.CASCADE, related_name="qualification"
    )
    year = models.CharField(
        verbose_name=_("سنة التخرج"),
        choices=[("", _("اختر"))]
        + [(str(i), str(i)) for i in range(1900, datetime.date.today().year + 1)],
        null=True,
        blank=True,
    )
    institution = models.ForeignKey(
        to=Institution,
        on_delete=models.PROTECT,
        related_name="qualifications",
        verbose_name=_("المؤسسة"),
        null=True,
        blank=True,
    )
    name = models.CharField(
        default=QualificationChoices.BACHELOR,
        choices=QualificationChoices.choices,
        verbose_name=_("اسم المؤهل"),
    )

    field_of_study = models.CharField(
        choices=FieldChoices.choices, verbose_name=_("مجال الدراسة"), blank=True
    )

    def __str__(self) -> str:
        return self.get_name_display()

    class Meta:
        ordering = ["-id"]
        verbose_name = _("مؤهل أساسي")
        verbose_name_plural = _("مؤهلات أساسية")


class SecondedRecord(models.Model):
    original_workplace = models.ForeignKey(
        to=HealthUnit,
        on_delete=models.PROTECT,
        verbose_name=_("مكان العمل الأصلي"),
        related_name="secondment_history",
    )
    start_date = models.DateField(
        verbose_name=_("تاريخ بدأ الانتداب"), help_text="YYYY-MM-DD"
    )
    end_date = models.DateField(
        verbose_name=_("تاريخ انتهاء الانتداب"),
        null=True,
        blank=True,
        help_text="YYYY-MM-DD",
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
    date_of_certification = models.DateField(
        verbose_name=_("تاريخ الحصول عليها"), help_text="YYYY-MM-DD"
    )
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
    name = models.CharField(max_length=255, verbose_name=_("اسم الدورة التدريبية"))
    date_of_certification = models.DateField(
        verbose_name=_("تاريخ الحصول عليها"),
        blank=True,
        null=True,
        help_text="YYYY-MM-DD",
    )
    institution = models.ForeignKey(
        to=Institution,
        verbose_name=_("مكان الحصول عليها"),
        on_delete=models.PROTECT,
        related_name="training_certifications",
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        to=Employee, on_delete=models.CASCADE, related_name="training_certifications"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("دورة تدريبية")
        verbose_name_plural = _("دورات تدريبية")
