from django import forms

from .models import User_telegram

class User_telegramForm(forms.ModelForm):

    class Meta:
        model = User_telegram
        fields = (
            'external_id',
            'name',
            'last_name',
            'telephone_number',
            'vishlist_user',
            'interests_user',
            'wishes_user',
        )
        widgets = {
            'name': forms.TextInput,
            'last_name': forms.TextInput,
        }
