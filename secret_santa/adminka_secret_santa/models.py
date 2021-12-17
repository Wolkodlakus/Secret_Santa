from django.db import models

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
    )
    last_day = models.TextField(
        verbose_name='Дата окончания регистрации',
    )
    last_day_and_time_of_registration = models.TextField(
        verbose_name='Последний день и час регистрации'
    )
    draw_day = models.TextField(
        verbose_name='Дата раздачи подарков'
    )
    draw_time = models.DateTimeField(
        verbose_name='Дата и время раздачи подарков'
    )
    #gamers = models.ManyToManyField(User_telegram)
    def __str__(self):
        return f'Игра #{self.pk} {self.name} от {self.organizer}. {self.price_range} до {self.last_day_and_time_of_registration}. Раздача {self.draw_time}'

    class Meta:
        verbose_name = 'Игра в Тайного Санту'
        verbose_name_plural = 'Игры в Тайного Санту'

class User_telegram(models.Model):
    external_id = models.PositiveIntegerField(
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
    telephone_number = models.CharField(max_length=12) #Заменить?
    vishlist_user = models.TextField(
        verbose_name='Вишлист пользователя',
        blank=True,
    )
    interests_user = models.TextField(
        verbose_name='Интересы пользователя',
        blank=True,
    )
    wishes_user = models.TextField(
        verbose_name='Пожелания пользователя',
        blank=True,
    )
    games = models.ManyToManyField(Game_in_Santa, blank=True)

    def __str__(self):
        return f'#{self.external_id} {self.name} {self.last_name} '

    class Meta:
        verbose_name = 'Профиль пользователя телеграмма'
        verbose_name_plural = 'Профили пользователей телеграмма'



