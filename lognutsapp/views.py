from django.views import generic
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from . import models

#ミックスイン
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)

#ログイン・ログアウト関連
from django.contrib.auth.views import (
    LoginView, LogoutView
)

#モデル
from .models import (
    Subject, PersonalLog
)

#フォーム
from .forms import (
    LoginForm, SearchForm
)

#ライブラリ
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP #Decimal変換の際に利用
import calendar
import datetime
from collections import deque


"""
カスタムミックスイン
"""
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True
    # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
    def test_func(self):
        user = self.request.user
        return user.pk == int(self.kwargs['pk']) or user.is_superuser


class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup_calendar(self):
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)  # リスト内の要素を右に1つずつ移動...なんてときは、dequeを使うと中々面白いです
        return week_names

class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self, date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)

    def get_next_month(self, date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)
        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current_month),
            'month_current': current_month,
            'month_previous': self.get_previous_month(current_month),
            'month_next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data

class WeekCalendarMixin(BaseCalendarMixin):
    """週間カレンダーの機能を提供するMixin"""
    def get_week_days(self):
        """その週の日を全て返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()
        for week in self._calendar.monthdatescalendar(date.year, date.month):
            if date in week:  # 週ごとに取り出され、中身は全てdatetime.date型。該当の日が含まれていれば、それが今回表示すべき週です
                return week
    def get_week_calendar(self):
        """週間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        days = self.get_week_days()
        first = days[0]
        last = days[-1]
        calendar_data = {
            'now': datetime.date.today(),
            'week_days': days,
            'week_previous': first - datetime.timedelta(days=7),
            'week_next': first + datetime.timedelta(days=7),
            'week_names': self.get_week_names(),
            'week_first': first,
            'week_last': last,
        }
        return calendar_data

class TopView(generic.TemplateView):
    """Lognutsトップページ"""
    template_name = 'lognuts/top.html' 

class MypageView(OnlyYouMixin, WeekCalendarMixin, generic.TemplateView):
    """Lognutsマイページ"""
    model = User
    template_name = 'lognuts/mypage.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_week_calendar()
        context.update(calendar_context)
        context['calendar_col'] = ['日付', '食事ログ']
        context['PersonalLog'] = PersonalLog.objects.values('date', 'food_name').filter(
            user=self.request.user
        )
        return context

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'lognuts/login.html'

class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'lognuts/top.html'

class SearchInput(OnlyYouMixin, generic.FormView):
    """検索入力のフォームからの入力を扱う"""
    form_class = SearchForm
    template_name = 'lognuts/search_input.html'

    def form_invalid(self, form):
        ''' バリデーションに失敗した時 '''
        return super().form_invalid(form)

    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')

        if form['store'].value():
            #フォームのstoreがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['store_name'].str.contains(form['store'].value()) 
            ]
        if form['food'].value():
            #フォームのfoodがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['food_name'].str.contains(form['food'].value()) 
            ]
        if form['size'].value():
            #フォームのsizeがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ 
                mealsout_df['food_size'].str.contains(form['size'].value()) 
            ]
        context['columns'] = ['レストラン名', '食品名', 'サイズ']
        context['search_foods'] = mealsout_df
        return render(self.request, 'lognuts/search_confirm.html', context)

class SearchComplete(OnlyYouMixin, generic.TemplateView):
    template_name = 'lognuts/search_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')
        context['columns'] = [
            'データ挿入日時', 'レストラン名', 'メニュー名', 'サイズ', 'カロリー', '炭水化物', 'タンパク質', '脂質', '食塩相当量'
        ]

        if self.kwargs['id']:
            #合致したレコードをpandas seriesとして取り出す
            input_record =  mealsout_df[ (mealsout_df['id'] == self.kwargs['id']) ].iloc[0]
            p_log = PersonalLog()
            print(input_record.protein)
            p_log.user = self.request.user
            p_log.restaurant = input_record.store_name
            p_log.size = input_record.food_size
            p_log.food_name = input_record.food_name
            p_log.energie = input_record.calorie
            p_log.carbohydrate = dec_conv(input_record.carbohydrate)
            p_log.protein = dec_conv(input_record.protein)
            p_log.fat = dec_conv(input_record.fat)
            p_log.salt = dec_conv(input_record.salt)
            context['p_log'] = p_log
            p_log.save()

        return context

#floatを2桁のDecimal型に変換する
def dec_conv(float_num):
    decimal_num = Decimal(float_num).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    return decimal_num
