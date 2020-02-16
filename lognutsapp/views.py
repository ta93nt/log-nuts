from django.views import generic
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from . import models
from django.db.models import Sum

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
from decimal import Decimal, ROUND_HALF_UP
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

"""
栄養素計算のMixIn
"""
class NutsCulcMixin:
    def get_week_nut_list(self):
        """過去１週間分の栄養素を取得する"""
        week_nut_list = []
        for i_day in reversed(range(7)):
            calc_date = datetime.date.today() - datetime.timedelta(i_day)
            oneday_nut = self.get_day_nut(calc_date)
            week_nut_list.append(oneday_nut)
        return week_nut_list

    def get_day_nut(self, calc_date):
        """引数の日付の一日分の栄養素の合計を計算する"""
        end_date = calc_date + datetime.timedelta(days=1)
        day_log = PersonalLog.objects.filter(
            user=self.request.user,
            date__range = (calc_date, end_date)
        )
        day_nut = day_log.aggregate(
            energie=Sum('energie'),
            protein=Sum('protein'),
            fat=Sum('fat'),
            carbohydrate=Sum('carbohydrate'),
            salt=Sum('salt')
        )
        return day_nut

    def get_latest_nut(self, calc_hour):
        """現在時刻から引数の calc_hour 時間以内の栄養素の合計を計算する"""
        end_datetime = datetime.datetime.now()
        start_datetime = end_datetime - datetime.timedelta(hours=calc_hour)
        latest_log = PersonalLog.objects.filter(
            user=self.request.user,
            date__range = (start_datetime, end_datetime)
        )
        latest_nut = latest_log.aggregate(
            energie=Sum('energie'),
            protein=Sum('protein'),
            fat=Sum('fat'),
            carbohydrate=Sum('carbohydrate'),
            salt=Sum('salt')
        )
        return latest_nut

    def get_pfc(self, arg_nut):
        """引数の栄養素からPFCの比率を算出する"""
        if arg_nut['energie'] != None: #引数の栄養素データがある時
            #p_rateを計算
            p_rate = Decimal(
                arg_nut['protein']*4/arg_nut['energie']*100
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            #f_rateを計算
            f_rate = Decimal(
                arg_nut['fat']*9/arg_nut['energie']*100
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            #c_rateを計算
            c_rate = Decimal(
                100 - p_rate - f_rate
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            #
            return_pfc = {'p':p_rate, 'f':f_rate, 'c':c_rate }
        else:
            return_pfc = {'p':None, 'f':None, 'c':None}
        return return_pfc

    def get_pfc_diff(self, arg_pfc):
        """
        栄養素の比率{p,f,c}の辞書を引数とし、
        PFC_diffの{p_diff, f_diff, c_diff, pfc_diff}の辞書を返す
        """
        #まずp_diff, f_diff, c_diffのそれぞれを求め、リターンする辞書に格納
        ret = {
            'p_diff':self.get_diff(arg_pfc['p'], settings.P_RATE_MIN, settings.P_RATE_MAX),
            'f_diff':self.get_diff(arg_pfc['f'], settings.F_RATE_MIN, settings.F_RATE_MAX),
            'c_diff':self.get_diff(arg_pfc['c'], settings.C_RATE_MIN, settings.C_RATE_MAX)
        }
        #pfc_diff = |p_diff| + |f_diff| + |c_diff| (絶対値計算)
        ret['pfc_diff'] = abs(ret['p_diff']) + abs(ret['f_diff']) + abs(ret['c_diff'])
        return ret

    def get_diff(self, arg_rate, min_v, max_v):
        """
        入力された栄養素比率が上限・下限いないなら0
        上限・下限を超えると超えた比率をの差分を返す
        """
        if min_v <= arg_rate and arg_rate <= max_v:
            return_diff = 0
        elif arg_rate < min_v:
            return_diff = arg_rate - min_v
        elif max_v < arg_rate:
            return_diff = arg_rate - max_v
        return return_diff

    def get_suggestion_food_list(self):
        """三大栄養素バランスを整える食品のリストを取得"""
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')
        #直近のSUGGESTION_HOUR時間以内の食品の栄養素を取得
        latest_nut = self.get_latest_nut(settings.SUGGESTION_HOUR)
        #栄養素データが取得できた時(エネルギーが空じゃない時)
        if latest_nut['energie'] != None:
            latest_pfc = self.get_pfc(latest_nut)
            latest_pfc_diff = self.get_pfc_diff(latest_pfc)
            
        return 0

class TopView(generic.TemplateView):
    """Lognutsトップページ"""
    template_name = 'lognuts/top.html' 

class MypageView(OnlyYouMixin, WeekCalendarMixin, NutsCulcMixin, generic.TemplateView):
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
        #栄養素の可視化に利用する
        context['toweek_nut_list'] = self.get_week_nut_list()
        context['today_nut'] = self.get_day_nut( datetime.date.today() )
        context['today_pfc'] = self.get_pfc( context['today_nut'] )
        context['radar_pfc_point'] = {
            'p': settings.RADAR_P,
            'f': settings.RADAR_F,
            'c': settings.RADAR_C
        }
        #食事推薦に利用する
        context['suggestion_food_list'] = self.get_suggestion_food_list()
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
            mealsout_df = mealsout_df[ mealsout_df['store_name'].str.contains(form['store'].value()) ]
        if form['food'].value():
            #フォームのfoodがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ mealsout_df['food_name'].str.contains(form['food'].value()) ]
        if form['size'].value():
            #フォームのsizeがある場合、文字列を含むレコード抽出
            mealsout_df = mealsout_df[ mealsout_df['food_size'].str.contains(form['size'].value()) ]
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
