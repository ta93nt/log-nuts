from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
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
    food_name = models.CharField(max_length=50)
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

class FoodImage(models.Model):
    """アップロードされたファイルを表すモデル"""
    #画像ファイル
    file = models.ImageField('画像ファイル')
    #ユーザ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #食べた日付
    eat_date = models.DateField(default=timezone.now)
    #アップロード日時
    created_date = models.DateTimeField(default=timezone.now)
    # エネルギー
    energie = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 炭水化物
    carbohydrate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # たんぱく質
    protein = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 脂質
    fat = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 食塩相当量
    salt = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # タンパク質割合
    p_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 脂質割合
    f_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 炭水化物割合
    c_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # タンパク質の規定割合からの差
    p_diff = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 脂質の規定割合からの差
    f_diff = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # 炭水化物の規定割合からの差
    c_diff = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # PFC_diff
    pfc_diff = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # PFC_score
    pfc_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    #データ削除時にメディアフォルダの画像も消す
    @receiver(pre_delete)
    def delete_image(sender, instance, **kwargs):
        if 'file' in dir(instance):
            instance.file.delete(False)
    """
    def __str__(self):
        return self.file.url
    """

class PersonalLog(models.Model):
    class Meta:
         ordering = ['-date']
    """食事ログデータ"""
    #ユーザ
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 食品名 : 文字列50文字
    food_name = models.CharField(max_length=50)
    # 店舗の電話番号
    tel = models.CharField(max_length=30, null=True, blank=True)
    # 店舗名
    restaurant = models.CharField(max_length=30)
    # 購入日時
    date = models.DateTimeField(default=timezone.now)
    # 値段
    price = models.CharField(max_length=30, null=True, blank=True)
    # コード
    code = models.CharField(max_length=30, null=True, blank=True)
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
    # 料理写真id
    food_image_id = models.ForeignKey(FoodImage, on_delete=models.SET_NULL, null=True, blank=True)
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