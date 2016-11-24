from django.db import models
from django.contrib.auth.models import AbstractUser

import datetime


class User(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    father_name = models.CharField(max_length=30, verbose_name='Отчество')
    passport_id = models.CharField(max_length=14, verbose_name='Идентификационный номер')
    phone = models.CharField(max_length=13, verbose_name='Телефон')
    address = models.CharField(max_length=50, verbose_name='Адрес')
    birthday = models.DateField(null=True, blank=True, verbose_name='Дата рождения')

    def get_full_name(self):
        return self.username if self.is_superuser else "{} {} {}".format(self.last_name, self.first_name, self.father_name)

    def get_short_name(self):
        return self.username if self.is_superuser else "{} {}. {}.".format(self.last_name, self.first_name[:1], self.father_name[:1])

    def get_age(self):
        from datetime import date
        return (date.today() - self.birthday).days // 365


class Currency(models.Model):
    title = models.CharField(max_length=3, verbose_name='Название')
    icon = models.CharField(max_length=1, verbose_name='Значок')

    def __str__(self):
        return self.title


class Bill(models.Model):
    client = models.ForeignKey(User, verbose_name='Клиент')
    money = models.FloatField(verbose_name='Денежная сумма')
    currency = models.ForeignKey(Currency, verbose_name='Валюта')

class Deposit(models.Model):

    Types = (
        ('Вклад до востребования', 'Вклад до востребования'),
        ('Сберегательный вклад', 'Сберегательный вклад'),
    )

    title = models.CharField(max_length=30, verbose_name='Название')
    description = models.CharField(max_length=300, verbose_name='Описание')
    depositType = models.CharField(max_length=30,choices=Types, verbose_name='Тип')
    percent = models.IntegerField(verbose_name='Ставка')
    percent_for_early_withdrawal=models.IntegerField(verbose_name='Ставка при преждевременном снятии',blank=True)
    #is_floating_rate=models.BooleanField(verbose_name='Плавающая ставка')
    currency = models.ForeignKey(Currency, verbose_name='Валюта')
    min_amount=models.FloatField(verbose_name='Минимальная сумма')
    duration=models.IntegerField(verbose_name='Срок хранения')
    is_refill=models.BooleanField(verbose_name='Возможность пополнения')
    min_refill = models.FloatField(verbose_name='Минимальное пополнение',blank=True)
    pay_period_in_months = models.FloatField(verbose_name='Период выплат')
    is_capitalization=models.BooleanField(verbose_name='Капитализация')
    is_early_withdrawal=models.BooleanField(verbose_name='Возможность преждевременного снятия')
    minimum_balance=models.FloatField(verbose_name='Неснижаемый остаток', blank=True)
    binding_currency=models.ForeignKey(Currency,related_name="BindingCurrency", verbose_name='Валюта привязки',blank=True)
    is_archive=models.BooleanField(verbose_name='Капитализация',default=False,editable=False)

    def getCurrencyTitle(self):
        return self.currency.title



class Contract(models.Model):
    bill = models.ForeignKey(Bill, verbose_name='Счёт пользователя')
    deposit_bill=models.FloatField(verbose_name='Депозитный счет')
    deposit = models.ForeignKey(Deposit, verbose_name='Вид дипозита')
    percent = models.FloatField(verbose_name='Ставка')

    #start_exchange_rate=models.FloatField(verbose_name='начальный курс')
    #final_exchange_rate = models.FloatField(verbose_name='конечный курс')

    bonuce=models.FloatField(verbose_name='Бонусная индексированная ставка', default=0)
    sign_date = models.DateTimeField(verbose_name='Дата подписания', default=datetime.datetime.now)
    end_date = models.DateTimeField(verbose_name='Дата окончания')
    is_prolongation=models.BooleanField(verbose_name='Пролонгация')

    def get_storing_term(self):
        return (datetime.datetime.now() - self.sign_date).days

    def calculate_bonuce(self):
        self.bonuce=((self.final_exchange_rate/self.start_exchange_rate)*100-100)*360/360


class ActionType(models.Model):
    description=models.CharField(max_length=300, verbose_name='Описание')


class Action(models.Model):
    actionType=models.ForeignKey(ActionType, verbose_name='Тип действия')
    contract = models.ForeignKey(Contract, verbose_name='Договор')
    datetime = models.DateTimeField(verbose_name='Дата', default=datetime.datetime.now)
    money = models.FloatField(verbose_name='Денежная сумма')




class ExchangeRate(models.Model):
    date = models.DateField(verbose_name='Дата', default=datetime.date.today)
    from_currency = models.ForeignKey(Currency, verbose_name='Эталон', related_name="from_currency")
    to_currency = models.ForeignKey(Currency, verbose_name='Валюта', related_name="to_currency")
    index = models.FloatField(verbose_name='Кросс-курс')

    def calc(self, value):
        return value * self.index
