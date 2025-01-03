from django.contrib import admin
from django.db import models
from .models import (
    Diamond,
    Subject,
    Chapter,
    Exam,
    Topic,
    Year,
    StudyMaterial,
    Question,
    Option,
    Solution,
    Attempt,
    DailyQuestion,
    Image,
    UserProfile,
    Tag,
    RecentUpdate,
    UpcomingPlan,
)
from markdownx.admin import MarkdownxModelAdmin
from markdownx.widgets import AdminMarkdownxWidget
from django.utils.html import format_html
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.contrib.auth.models import Permission
from .forms import QuestionAdminForm


class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminMarkdownxWidget},
    }

    def __init__(self, model, admin_site):
        all_fields = [field.name for field in model._meta.fields]
        self.list_display = [self.truncate_field(field) for field in all_fields]
        self.search_fields = [
            field.name
            for field in model._meta.fields
            if isinstance(
                field, (models.CharField, models.TextField, models.BooleanField)
            )
        ]
        self.list_filter = [
            field.name
            for field in model._meta.fields
            if isinstance(
                field, (models.BooleanField, models.ForeignKey, models.DateTimeField)
            )
        ]
        self.ordering = ["-id"]
        self.change_list_template = "admin/change_list.html"
        # self.save_on_top = True

        super().__init__(model, admin_site)

    def truncate_field(self, field_name):
        def truncated_value(obj):
            value = getattr(obj, field_name, "")
            length = 50
            if isinstance(value, str) and len(value) > length:
                return format_html("{}...", value[:length])
            return value

        truncated_value.short_description = field_name
        return truncated_value


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1


class QuestionAdmin(MyModelAdmin):
    inlines = [OptionInline, SolutionInline]

    # form = QuestionAdminForm
    # list_display = [
    #     'id', 'subject', 'chapter', 'topic', 'has_options', 'has_correct_option', 'solution_summary'
    # ]
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_filter = [
            ("subject", RelatedOnlyFieldListFilter),
            ("chapter", RelatedOnlyFieldListFilter),
            ("topic", RelatedOnlyFieldListFilter),
            ("years", RelatedOnlyFieldListFilter),
        ] + self.list_filter


class ExamAdmin(MyModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_filter = [
            ("subjects", RelatedOnlyFieldListFilter),
        ] + self.list_filter


class ChaptersAdmin(MyModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_filter = [
            ("subjects", RelatedOnlyFieldListFilter),
        ] + self.list_filter


class StudyMaterialAdmin(MyModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_filter = [
            ("year", RelatedOnlyFieldListFilter),
            ("exam", RelatedOnlyFieldListFilter),
            ("subject", RelatedOnlyFieldListFilter),
        ] + self.list_filter


class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "uploaded_at", "image_preview", "copy_url_link")
    readonly_fields = ("image_preview", "copy_url_link")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.image.url,
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Image Preview"

    def copy_url_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="#" onclick="copyUrl(\'{}\')">Copy URL</a>', obj.image.url
            )
        return ""

    copy_url_link.short_description = "Copy URL"


admin.site.register(Subject, MyModelAdmin)
admin.site.register(Chapter, ChaptersAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Topic, MyModelAdmin)
admin.site.register(StudyMaterial, StudyMaterialAdmin)
admin.site.register(Attempt, MyModelAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(DailyQuestion, MyModelAdmin)
admin.site.register(Year, MyModelAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserProfile, MyModelAdmin)
admin.site.register(Permission)
admin.site.register(Diamond, MyModelAdmin)
admin.site.register(Tag, MyModelAdmin)
admin.site.register(RecentUpdate, MyModelAdmin)
admin.site.register(UpcomingPlan, MyModelAdmin)
