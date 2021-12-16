from django.contrib import admin

from .forms import User_telegramForm
from .models import User_telegram

@admin.register(User_telegram)
class User_telegramADMIN(admin.ModelAdmin):
    list_display = ('id','external_id','name','last_name')
    form = User_telegramForm
# Register your models here.
