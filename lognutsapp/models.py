from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone #タイムゾーンを扱うために追加

class SuggestionFoodsAnalysis(models.Model):
    class Meta:
        ordering = ['-created_date']
    """推薦食品分析データ"""
    #ユーザ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # データ挿入日時
    created_date = models.DateTimeField(default=timezone.now)
    #食べたいと思ったか
    want = models.CharField(max_length=30, null=True)
    #実際に食べたか
    action = models.CharField(max_length=30)
    # 食品名 : 文字列30桁
    food_name = models.CharField(max_length=30)
    # 店舗名 : 文字列30桁
    store = models.CharField(max_length=30)
    # サイズ : 文字列30桁
    size = models.CharField(max_length=30)
    # エネルギー
    energie = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 炭水化物
    carbohydrate = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # たんぱく質
    protein = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 脂質
    fat = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 食塩相当量
    salt = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # メニュータグ
    tag = models.CharField(max_length=30)
    # メニュータグ(日本語)
    str_tag = models.CharField(max_length=30)

class PersonalLog(models.Model):
    class Meta:
         ordering = ['-date']
    """食事ログデータ"""
    #ユーザ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 食品名 : 文字列30桁
    food_name = models.CharField(max_length=30)
    # 店舗の電話番号
    tel = models.CharField(max_length=30, null=True)
    # 店舗名
    restaurant = models.CharField(max_length=30)
    # 購入日時
    date = models.DateTimeField(default=timezone.now)
    # 値段
    price = models.CharField(max_length=30, null=True)
    # コード
    code = models.CharField(max_length=30, null=True)
    # サイズ
    size = models.CharField(max_length=30, null=True, blank=True)
    # エネルギー
    energie = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 炭水化物
    carbohydrate = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # たんぱく質
    protein = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 脂質
    fat = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # 食塩相当量
    salt = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    # データ挿入日時
    created_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.food_name

class Subject(models.Model):
    """ユーザにOneToOneの実験用カラムを追加"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    experiment_group = models.CharField(max_length=100, blank=True)

@receiver(post_save, sender=User)
def create_subject(sender, instance, created, **kwargs):
    if created:
        Subject.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_subject(sender, instance, **kwargs):
    instance.subject.save()