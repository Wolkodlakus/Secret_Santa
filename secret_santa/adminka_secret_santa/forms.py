from django import forms

from .models import User_telegram, Game_in_Santa

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

class Game_in_SantaForm(forms.ModelForm):
    class Meta:
        model = Game_in_Santa
        fields = (
            'organizer',
            'name_game',
            'price_range',
            'last_day_and_time_of_registration',
            'draw_time',
        )
        widgets = {
            'name': forms.TextInput,
            'last_name': forms.TextInput,
        }