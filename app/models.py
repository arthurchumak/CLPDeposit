#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser

import datetime


class User(AbstractUser):
    #first_name = models.CharField(max_length=30, verbose_name='Имя')
    #last_name = models.CharField(max_length=30, verbose_name='Фамилия')
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

    def print_short(self, value):
        return "{}{}".format(round(value), self.icon)

    def print_full(self, value):
        return "{}{}".format(self.title, round(value))


class Bill(models.Model):
    client = models.ForeignKey(User, verbose_name='Клиент')
    money = models.FloatField(verbose_name='Денежная сумма')
    currency = models.ForeignKey(Currency, verbose_name='Валюта')


class Card(models.Model):
    bill=models.ForeignKey(Bill,verbose_name='Счёт')
    limit=models.FloatField(verbose_name='Лимит')


class Message(models.Model):
    message = models.CharField(max_length=300, verbose_name='Сообщение')
    header = models.CharField(max_length=100, verbose_name='Заголовок')
    readed = models.BooleanField(default=False, verbose_name='Прочитано ?')
    user = models.ForeignKey(User, verbose_name='Пользователь')
    date = models.DateField(default=datetime.date.today, verbose_name='Дата')


class Deposit(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название')
    description = models.CharField(max_length=300, verbose_name='Описание')
    percent = models.IntegerField(verbose_name='Ставка')
    min_storing_term = models.IntegerField(verbose_name='Минимальный срок хранения')
    max_storing_term = models.IntegerField(verbose_name='Максимальный срок хранения')
    pay_term = models.IntegerField(verbose_name='Период выплат')
    refill = models.BooleanField(verbose_name='Пополнение')
    partial_take = models.BooleanField(verbose_name='Частичное снятие')
    indexed = models.BooleanField(verbose_name='Индексированный')
    currency = models.ForeignKey(Currency, verbose_name='Валюта')


class Contract(models.Model):
    bill = models.ForeignKey(Bill, verbose_name='Счёт')
    deposit = models.ForeignKey(Deposit, verbose_name='Вклад')
    sign_date = models.DateTimeField(verbose_name='Дата подписания', default=datetime.datetime.now)
    term = models.IntegerField(verbose_name='Срок')
    money = models.FloatField(verbose_name='Сумма вклада')

    def calc_payment(self):
        return self.money * (self.deposit.percent / 100)

    def get_storing_term(self):
        return (datetime.datetime.now() - self.sign_date).days

    def is_active(self):
        return (datetime.date.today() > self.sign_date) and (self.get_storing_term() < self.term)


class Pay(models.Model):
    agent = models.ForeignKey(User, verbose_name='Оформитель')
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
