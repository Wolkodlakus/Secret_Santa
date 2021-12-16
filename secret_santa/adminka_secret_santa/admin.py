from django.contrib import admin

from .forms import User_telegramForm,Game_in_SantaForm
from .models import User_telegram, Game_in_Santa

@admin.register(User_telegram)
class User_telegramADMIN(admin.ModelAdmin):
    list_display = ('id','external_id','name','last_name')
    form = User_telegramForm

@admin.register(Game_in_Santa)
class Game_in_SantaADMIN(admin.ModelAdmin):
    list_display = ('name_game','price_range','last_day_and_time_of_registration','draw_time')
    form = Game_in_SantaForm

