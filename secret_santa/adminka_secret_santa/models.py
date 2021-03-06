from django.db import models
from django.utils import timezone

#import secret_santa.adminka_secret_santa.models

class Game_in_Santa(models.Model):
    organizer = models.ForeignKey(
        to='adminka_secret_santa.User_telegram',
        verbose_name='Организатор игры',
        on_delete=models.PROTECT,
    )
    id_game = models.IntegerField(
        verbose_name='ID игры',
        default=0
    )
    name_game = models.TextField(
        verbose_name='Название игры',
    )
    price_range = models.TextField(
        verbose_name='Диапазон стоимости подарка',
        blank=True
    )

    last_day_and_time_of_registration = models.DateTimeField(
        verbose_name='Последний день и час регистрации',
        blank=True
    )

    draw_time = models.DateTimeField(
        verbose_name='Дата и время раздачи подарков',
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='Когда создана игра',
        default=timezone.now
    )
    draw = models.BooleanField(
        verbose_name='Был ли розыгрыш',
        default=False
    )
    #gamers = models.ManyToManyField(User_telegram)
    def __str__(self):
        return f'Игра #{self.pk} {self.name_game} от {self.organizer}. {self.price_range} до {self.last_day_and_time_of_registration}. Раздача {self.draw_time}'

    class Meta:
        verbose_name = 'Игра в Тайного Санту'
        verbose_name_plural = 'Игры в Тайного Санту'

class Interest(models.Model):
    name = models.CharField("Категория для подарка", max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Интерес"
        verbose_name_plural = "Интересы"


class Wishlist(models.Model):
    name = models.CharField("Название подарка", max_length=100)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, null=True, verbose_name="Категория")
    price = models.PositiveIntegerField("Цена подарка", null=True)
    image_url = models.CharField(blank=True, max_length=255, null=True, verbose_name='Ссылка на картинку')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Вишлист"
        verbose_name_plural = "Вишлисты"



class User_telegram(models.Model):
    external_id = models.PositiveIntegerField( #id в телеграм
        verbose_name='ID пользователя в telegram',
        unique=True
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )

    last_name = models.TextField(
        verbose_name='Фамилия пользователя',
    )
    username = models.TextField(
        verbose_name='Никнейм пользователя',
    )
    telephone_number = models.CharField(
        verbose_name="Телефонный номер",
        max_length=12,
    ) #Заменить?
    wishlist_user = models.ManyToManyField(
        Wishlist,
        verbose_name="Вишлист пользователя",
        blank=True
    )
    interest_user = models.ManyToManyField(
        Interest,
        verbose_name='Интересы пользователя',
        blank=True
    )
    wishes_user = models.TextField(
        verbose_name='Пожелания пользователя',
        blank=True,
    )
    games = models.ManyToManyField(
        Game_in_Santa,
        blank=True,
        verbose_name='Игры пользователя'
    )
    letter = models.TextField("Письмо Санте", blank=True)

    def __str__(self):
        return f'#{self.external_id} {self.name} {self.last_name} '

    class Meta:
        verbose_name = 'Профиль пользователя телеграмма'
        verbose_name_plural = 'Профили пользователей телеграмма'

class Toss_up(models.Model):
    game = models.ForeignKey(
        Game_in_Santa,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Игра в Тайного Санту"
    )
    donators = models.ManyToManyField(
        User_telegram,

        related_name="donator",
        verbose_name="Кто дарит"
    )
    donees = models.ManyToManyField(
        User_telegram,

        related_name="whom",
        verbose_name="Кому дарит",
    )

    class Meta:
        verbose_name = "Жеребьевка"
        verbose_name_plural = "Жеребьевки"



