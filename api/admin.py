from django.contrib import admin
from django.db import models
from .models import Subject, Chapter, Exam, Topic,Year, StudyMaterial, Question, Option, Solution, Attempt
from markdownx.admin import MarkdownxModelAdmin
from markdownx.widgets import AdminMarkdownxWidget


class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super().__init__(model, admin_site)
        

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline, SolutionInline]
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super().__init__(model, admin_site)

admin.site.register(Subject, MyModelAdmin)
admin.site.register(Chapter, MyModelAdmin)
admin.site.register(Exam)
admin.site.register(Topic)
admin.site.register(StudyMaterial)
admin.site.register(Solution, MyModelAdmin)
admin.site.register(Attempt)
admin.site.register(Year)

admin.site.register(Question, QuestionAdmin)