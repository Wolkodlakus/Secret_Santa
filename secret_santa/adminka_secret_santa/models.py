from django.db import models


class User_telegram(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя в telegram',
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )
    last_name = models.TextField(
        verbose_name='Фамилия пользователя',
    )
    telephone_number = models.CharField(max_length=12) #Заменить?
    vishlist_user = models.TextField(
        verbose_name='Вишлист пользователя',
    )
    interests_user = models.TextField(
        verbose_name='Интересы пользователя',
    )
    wishes_user = models.TextField(
        verbose_name='Пожелания пользователя',
    )
    #games = models.ManyToManyField(Game_in_Santa)

    def __str__(self):
        return f'#{self.external_id} {self.name} {self.last_name} '

    class Meta:
        verbose_name = 'Профиль пользователя телеграмма'
        verbose_name_plural = 'Профили пользователей телеграмма'


class Game_in_Santa(models.Model):
    organizer = models.ForeignKey(
        to='adminka_secret_santa.User_telegram',
        verbose_name='Организатор игры',
        on_delete=models.PROTECT,
    )
    price_range = models.TextField(
        verbose_name='Диапазон стоимости подарка',
    )
    last_day_and_time_of_registration = models.DateTimeField(
        verbose_name='Последний день и час регистрации'
    )
    draw_time = models.DateTimeField(
        verbose_name='Дата и время раздачи подарков'
    )
    #gamers = models.ManyToManyField(User_telegram)
    def __str__(self):
        return f'Игра {self.pk} от {self.organizer}. {self.price_range} до {self.last_day_and_time_of_registration}. Раздача {self.draw_time}'

    class Meta:
        verbose_name = 'Игра в Тайного Санту'
        verbose_name_plural = 'Игры в Тайного Санту'
