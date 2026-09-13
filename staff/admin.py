import io
from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from weasyprint import HTML

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


@admin.action(description="PDF قوة الوحدة")
def workforce_pdf(
    model_admin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[models.Employee],
) -> HttpResponse:

    unit_name = queryset[0].health_unit.name
    health_admin = queryset[0].health_unit.get_health_admin_display()
    headers = ["الاسم", "الرقم القومي", "رقم التليفون", "ملاحظـــات"]
    html_string = render_to_string(
        "staff/pdf_template.djhtml",
        context={
            "employees": queryset,
            "headers": headers,
            "unit_name": unit_name,
            "health_admin": health_admin,
            "empty_cols": range(1),
            "page_size": "A4 portrait",
        },
    )

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="selected_employees.pdf"'

    return response


@admin.action(description="PDF قوة الوحدة برقم الصرف")
def workforce_code_pdf(
    model_admin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[models.Employee],
) -> HttpResponse:

    unit_name = queryset[0].health_unit.name
    health_admin = queryset[0].health_unit.get_health_admin_display()
    headers = ["الاسم", "الرقم القومي", "رقم التليفون", "رقم الصرف", "ملاحظـــات"]
    html_string = render_to_string(
        "staff/pdf_template.djhtml",
        context={
            "employees": queryset,
            "headers": headers,
            "unit_name": unit_name,
            "health_admin": health_admin,
            "empty_cols": range(2),
            "page_size": "A4 portrait",
        },
    )

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="selected_employees.pdf"'

    return response


@admin.action(description="xlsx العاملين بالوحدة")
def workforce_xlsx(
    model_admin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[models.Employee],
) -> FileResponse:

    unit_name = queryset[0].health_unit.name
    health_admin = queryset[0].health_unit.get_health_admin_display()

    buffer = io.BytesIO()

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.title = "العاملين"
    worksheet.views.sheetView[0].rightToLeft = True
    worksheet.append([f"الإدارة الصحية ب{health_admin}"])
    worksheet.append([f"قسم بيانات رعاية أساسية"])
    worksheet.append([f"وحدة {unit_name} الصحية"])
    worksheet.append([])
    worksheet.append([f"بيان العاملين بوحدة/ {unit_name}"])

    headers = [
        "الاسم",
        "أساسي/انتداب",
        "مكان العمل الأصلي للانتداب",
        "الدرجة",
        "الرقم القومي",
        "الوظيفة",
        "تخصص/للأطباء البشري",
        "سنة التخرج",
        "جامعة تخرج",
        "رقم التليفون",
        "تاريخ الميلاد",
        "تاريخ استلام العمل داخل الوحدة",
        "تاريخ تعيين (أول تعيين)",
        "البريد الالكتروني",
        "العنوان (محل الإقامة)",
        "درجه علميه(دبلومه-ماجستير-دكتوراه-زماله)",
        "تاريخ الحصول عليه",
        "الجامعه",
        "تدريبات التي تم الحصول عليها(دورات)",
        "مكان الحصول علي الدورات التدريبيه",
        "رقم ترخيص مزاوله مهنه",
    ]
    worksheet.append(headers)

    grey_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")

    for cell in worksheet[6]:
        cell.fill = grey_fill
        cell.font = Font(bold=True)

    yellow_fill = PatternFill(
        start_color="FFFF00", end_color="FFFF00", fill_type="solid"
    )

    worksheet.merge_cells(
        start_row=5, end_row=5, start_column=1, end_column=len(headers)
    )

    for cell in worksheet[5]:
        cell.fill = yellow_fill
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for i in queryset:
        current_secondment = i.current_secondment
        ow = current_secondment.original_workplace if current_secondment else ""
        grade = i.current_grade.get_name_display().split(" ")[1]
        doctor = i.doctor_details.first()
        speciality = doctor.get_speciality_display() if doctor else ""
        qualification = i.qualification
        year = str(qualification.year) if qualification else ""
        institution = qualification.institution
        address = i.addresses.last()
        additional_degrees = i.additional_degrees.select_related("institution")
        additional_degrees_names = "+".join([j.name for j in additional_degrees])
        additional_degrees_dates = "+".join(
            [str(j.date_of_certification) for j in additional_degrees]
        )
        additional_degrees_institutions = "+".join(
            [str(j.institution) for j in additional_degrees]
        )
        trainings = i.training_certifications.select_related("institution")
        trainings_names = "+".join([j.name for j in trainings])
        trainings_institutions = "+".join([str(j.institution or "") for j in trainings])
        row = [
            str(i.name),
            str(i.get_appointment_type_display()),
            ow,
            grade,
            str(i.national_id),
            str(i.get_job_title_display()),
            speciality,
            year,
            str(institution),
            str(i.phone_number),
            str(i.birth_date),
            str(i.job_start_date),
            str(i.first_hire_date),
            str(i.email),
            str(address),
            additional_degrees_names,
            additional_degrees_dates,
            additional_degrees_institutions,
            trainings_names,
            trainings_institutions,
            i.practice_license_number,
        ]
        worksheet.append(row)

    workbook.save(buffer)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="العاملين.xlsx")


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
    actions = [workforce_pdf, workforce_code_pdf, workforce_xlsx]
