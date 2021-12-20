from django.contrib import admin

from .forms import User_telegramForm,Game_in_SantaForm
from .models import User_telegram, Game_in_Santa, Toss_up, Wishlist

@admin.register(User_telegram)
class User_telegramADMIN(admin.ModelAdmin):
    list_display = ('external_id','name','last_name','username', 'phone')
    form = User_telegramForm

@admin.register(Game_in_Santa)
class Game_in_SantaADMIN(admin.ModelAdmin):
    list_display = ('name_game', 'id_game', 'price_range','last_day_and_time_of_registration','draw_time')
    readonly_fields = ('created_at',)
    form = Game_in_SantaForm

@admin.register(Toss_up)
class Toss_upADMIN(admin.ModelAdmin):
    list_display = ('game', 'donator', 'donee')

@admin.register(Wishlist)
class WishlistADMIN(admin.ModelAdmin):
    list_display = ('name', 'interest', 'price')