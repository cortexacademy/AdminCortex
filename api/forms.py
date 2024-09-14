from django import forms
from django.core.exceptions import ValidationError
from .models import Question, Option, Solution

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        question = self.instance

        if not question.pk:
            if not hasattr(question, 'options') or not question.options.exists():
                raise ValidationError("You must add at least one option.")

            if not question.options.filter(is_correct=True).exists():
                raise ValidationError("At least one option must be marked as correct.")

            if not Solution.objects.filter(question=question).exists():
                raise ValidationError("A solution must be added.")
        
        return cleaned_data
