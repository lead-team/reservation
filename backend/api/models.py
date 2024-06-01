from django.db import models
from django.contrib.auth.models import AbstractUser
import django_jalali.db.models as jmodels
# Create your models here.

class User(AbstractUser):
    profile=models.ImageField(upload_to='profiles/',blank=True,null=True,default='defaults/user.png',verbose_name='پروفایل')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

class ShiftType(models.TextChoices):
    A='A','A'
    B='B','B'
    C='C','C'
    D='D','D'

    def get_values(self):
        return [choice.value for choice in self]


class Shift(models.Model):
    shift_name = models.CharField(max_length=100, choices=ShiftType.choices,verbose_name='نوع شیفت')

    class Meta:
        verbose_name='شیفت'
        verbose_name_plural='شیفت ها'
    def __str__(self) -> str:
        return self.shift_name

class WorkFlow(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='work_flows')
    shift=models.ForeignKey(Shift,on_delete=models.CASCADE,related_name='work_flows')

    class Meta:
        verbose_name='ساعت کاری'
        verbose_name_plural='ساعت کاری ها'


class ShiftManager(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name='کاربر')
    shift=models.OneToOneField(Shift,on_delete=models.CASCADE,verbose_name="شیفت")

    class Meta:
        verbose_name='مدیر شیفت'
        verbose_name_plural='مدیران شیفت'


class SupervisorRecord(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name="کاربر")
    supervisor=models.ForeignKey(ShiftManager,on_delete=models.CASCADE,verbose_name="منصوب کننده")
    from_date=jmodels.jDateField(verbose_name='از تاریخ')
    to_date=jmodels.jDateField(verbose_name='تا تاریخ')

    class Meta:
        verbose_name="مسیولیت"
        verbose_name_plural='مسیولیت ها'




class FoodType(models.TextChoices):
    TYPE1="چلو","چلو"
    TYPE2="خوراک","خوراک"
    TYPE3="پلو","پلو"
    DIET="غذای رژیمی","غذای رژیمی"
    DESSERT="دسر","دسر"
    DRINK="نوشیدنی","نوشیدنی"
    TYPE4="غیره","غیره"

    def get_values(self):
        return [choice.value for choice in self]

class Food(models.Model):
    name=models.CharField(max_length=100,verbose_name="نام غذا")
    type=models.CharField(max_length=100,choices=FoodType.choices,verbose_name="نوع غذا")


    class Meta:
        verbose_name='غذا'
        verbose_name_plural='غذا ها'

    def __str__(self) -> str:
        return self.name


class DailyMeal(models.TextChoices):
    LUNCH="ناهار","ناهار"
    DINNER="شام","شام"

    def get_values(self):
        return [choice.value for choice in self]


class Meal(models.Model):
    food1=models.ForeignKey(Food,on_delete=models.CASCADE,verbose_name="غذای 1",related_name="first_meals")
    food2=models.ForeignKey(Food,on_delete=models.CASCADE,verbose_name="غذای 2",related_name="second_meals")
    diet=models.ForeignKey(Food,on_delete=models.CASCADE,related_name="diet_meals",null=True,blank=True,verbose_name="غذای رژیمی")
    dessert=models.ForeignKey(Food,on_delete=models.CASCADE,related_name="dessert_meals",null=True,blank=True,verbose_name="دسر")
    daily_meal=models.CharField(max_length=50,choices=DailyMeal.choices,verbose_name="وعده غذا")

    class Meta:
        verbose_name="وعده"
        verbose_name_plural="وعده ها"

    def __str__(self) -> str:
        return f"food1:{self.food1} | food2:{self.food2} |"


class Drink(models.Model):
    name=models.CharField(max_length=100,verbose_name="نام")
    meal=models.ForeignKey(Meal,related_name="drinks",on_delete=models.CASCADE,verbose_name="وعده")

    class Meta:
        verbose_name="نوشیدنی"
        verbose_name_plural="نوشیدنی ها"




class ShiftMeal(models.Model):
    meal=models.ForeignKey(Meal,on_delete=models.CASCADE,verbose_name="وعده")
    date=jmodels.jDateField(verbose_name='تاریخ')
    shift=models.ForeignKey(Shift,on_delete=models.CASCADE,verbose_name="شیفت",related_name="shift_meals")

    class Meta:
        verbose_name="وعده شیفت"
        verbose_name_plural="وعده های شیفت"
    





