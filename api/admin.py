from django.contrib import admin
from django.db import models
from .models import Subject, Chapter, Exam, Topic,Year, StudyMaterial, Question, Option, Solution, Attempt,DailyQuestion
from markdownx.admin import MarkdownxModelAdmin
from markdownx.widgets import AdminMarkdownxWidget


class MyModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        self.search_fields = [
            field.name for field in model._meta.fields 
            if isinstance(field, (models.CharField, models.TextField,models.BooleanField))
        ]
        super().__init__(model, admin_site)
        

class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 1

class QuestionAdmin(MyModelAdmin):
    inlines = [OptionInline, SolutionInline]
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)


admin.site.register(Subject, MyModelAdmin)
admin.site.register(Chapter, MyModelAdmin)
admin.site.register(Exam,MyModelAdmin)
admin.site.register(Topic,MyModelAdmin)
admin.site.register(StudyMaterial, MyModelAdmin)
admin.site.register(Attempt,MyModelAdmin)
admin.site.register(DailyQuestion,MyModelAdmin)
admin.site.register(Year,MyModelAdmin)
admin.site.register(Question, QuestionAdmin)