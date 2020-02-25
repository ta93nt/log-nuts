from django.views import generic
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from . import models
from django.db.models import Sum, Q

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
    Subject, PersonalLog, FoodImage
)

#フォーム
from .forms import (
    LoginForm, SearchForm, ManualForm, HistoryForm, ImageUploadForm
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
context作成を補助するミックスイン
"""
class ContextMixin:
    def get_personal_log_columns(self):
        columns = [
            '食べた日時', 
            'レストラン名', 
            'メニュー名', 
            'サイズ', 
            'カロリー', 
            'タンパク質', 
            '脂質', 
            '炭水化物', 
            '食塩相当量'
        ]
        return columns
    def get_personal_log_from_df(self, input_record):
        """
        データフレームと外食食品DBのidを受け取り、
        食事ログを返す
        """
        p_log = PersonalLog()
        p_log.user = self.request.user
        p_log.restaurant = input_record.store_name
        p_log.size = input_record.food_size
        p_log.food_name = input_record.food_name
        p_log.energie = input_record.calorie
        p_log.carbohydrate = dec_conv(input_record.carbohydrate)
        p_log.protein = dec_conv(input_record.protein)
        p_log.fat = dec_conv(input_record.fat)
        p_log.salt = dec_conv(input_record.salt)
        return p_log
    def get_personal_log_from_post(self, post):
        """
        リクエストのPOSTを受け取り、
        食事ログを作成して返す
        """
        p_log = PersonalLog()
        p_log.user = self.request.user
        p_log.restaurant = post['restaurant']
        p_log.date = post['date']
        p_log.size = post['size']
        p_log.food_name = post['food_name']
        p_log.energie = post['energie']
        p_log.carbohydrate = post['carbohydrate']
        p_log.protein = post['protein']
        p_log.fat = post['fat']
        p_log.salt = post['salt']
        return p_log
    def get_personal_log_from_queryset(self, query):
        """
        食べた物のクエリリストを受け取り、
        食事ログを作成して返す
        """
        p_log = PersonalLog()
        p_log.user = self.request.user
        p_log.restaurant = query.restaurant
        p_log.size = query.size
        p_log.food_name = query.food_name
        p_log.energie = query.energie
        p_log.carbohydrate = query.carbohydrate
        p_log.protein = query.protein
        p_log.fat = query.fat
        p_log.salt = query.salt
        p_log.date = datetime.datetime.now()
        return p_log

"""
栄養素計算のMixIn
"""
class NutsCulcMixin:
    def get_week_nut_list(self):
        """過去１週間分の栄養素辞書(1日分)のリスト(7要素)を取得する"""
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
        """
        引数の栄養素からPFCの比率を算出する
        必要条件: 辞書型で energie, protein, fat が存在している
        """
        if arg_nut['energie'] != None: #引数の栄養素データがある時
            #p_rateを計算
            p_rate = dec_conv(arg_nut['protein']*4/arg_nut['energie']*100)
            #f_rateを計算
            f_rate = dec_conv(arg_nut['fat']*9/arg_nut['energie']*100)
            #c_rateを計算
            c_rate = dec_conv(100 - p_rate - f_rate)
            #返り値の辞書を作成
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

    def sort_large_diff(self, pfc_diff):
        """
        入力されたPFC_diffの辞書の中のp_diff, f_diff, c_diff
        バリューの絶対値が大きい順に並べ替え、キー(カラム名)のリストを出力する
        """
        abs_dict = {}  #p_diff, f_diff, c_diffの絶対値の辞書
        for k, v in pfc_diff.items():
            abs_dict[k] = abs(v)
        large_list = []
        for k, v in sorted(abs_dict.items(), key=lambda x: -x[1]):
            large_list.append(k)
        #pfc_diffが含まれていれば削除
        if 'pfc_diff' in large_list:
            large_list.remove('pfc_diff')
        return large_list
    
    def get_menu_tag_query(self):
        """
        推薦する食品のメニュータグの絞り込みのクエリを作成する
        """
        menu_tag_list = settings.MENU_TAG_LIST
        ret_query = ''
        for m in menu_tag_list:
            ret_query = ret_query + "menu_tag=='{}'|".format(m)
        ret_query = ret_query[:-1] #最後の余分な文字列'|'を削除
        return ret_query

    def get_suggestion_food_list(self):
        """三大栄養素バランスを整える食品のリストを取得"""
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL)
        #直近のSUGGESTION_HOUR時間以内の食品の栄養素を取得
        latest_nut = self.get_latest_nut(settings.SUGGESTION_HOUR)
        #栄養素データが取得できた時(エネルギーが空じゃない時)
        if latest_nut['energie'] != None:
            latest_pfc = self.get_pfc(latest_nut)
            latest_pfc_diff = self.get_pfc_diff(latest_pfc)
            #remain_energie(残りのエネルギー)の初期値として栄養所要量のエネルギー基準を取得
            remain_energie = settings.ENERGIE_BORDER
            #摂取したエネルギーを減算する
            remain_energie = remain_energie - latest_nut['energie']
            large_pfc_list = self.sort_large_diff(latest_pfc_diff)
            menu_tag_query = self.get_menu_tag_query()
            #残りのエネルギーを超えず、メニュータグに合致した料理を抽出
            suggest_df = mealsout_df.query(
                'calorie<{} & ({})'.format(remain_energie,menu_tag_query)
            )
            if latest_pfc_diff['pfc_diff'] == 0:
                #pfc_diff=0の時(すでに栄養バランスが良い場合には栄養バランスの良い食品を推薦)
                suggest_foods = suggest_df.query(
                    "pfc_diff==0"
                ).sample(n=settings.FOOD_SUGGESTION_NUM)
            else:
                #pfc_diff≠0の時(栄養バランスを整える食品を推薦)
                after_array = [] #推薦候補のdfに追加するdfを格納する配列
                for s_id, ene, pro, fat, car in zip(suggest_df['id'], suggest_df['calorie'], suggest_df['protein'], suggest_df['fat'], suggest_df['carbohydrate']):
                    #推薦後(推薦する栄養 + 直近の栄養)の栄養を計算
                    after_nut = {}
                    after_nut['energie'] =      dec_conv(ene) + latest_nut['energie']
                    after_nut['protein'] =      dec_conv(pro) + latest_nut['protein']
                    after_nut['fat'] =          dec_conv(fat) + latest_nut['fat']
                    after_nut['carbohydrate'] = dec_conv(car) + latest_nut['carbohydrate']
                    #推薦後(推薦食品を食べた場合)のPFCの比率を取得
                    after_pfc = self.get_pfc( after_nut )
                    #推薦後のPFC_diffを取得
                    pfc_diff = self.get_pfc_diff( after_pfc )
                    after_pfc_diff = {
                        'id':s_id, #dfのmergeに使用するidを辞書に追加
                        'after_p':after_pfc['p'],
                        'after_f':after_pfc['f'],
                        'after_c':after_pfc['c'],
                        'after_p_diff':pfc_diff['p_diff'],
                        'after_f_diff':pfc_diff['f_diff'],
                        'after_c_diff':pfc_diff['c_diff'],
                        'after_pfc_diff':pfc_diff['pfc_diff']
                    }
                    #処理の高速化のために配列に格納 -> df変換をする
                    after_array.append(after_pfc_diff)
                #推薦食品のdfに推薦後のpfc_diffのdfを内部結合する
                if len(suggest_df.index) > 0 :
                    suggest_df = pd.merge(suggest_df, pd.DataFrame.from_dict(after_array), on='id', how='inner')
                    suggest_foods = suggest_df.sort_values('after_pfc_diff').head(settings.FOOD_SUGGESTION_NUM)
                else:
                    suggest_foods = suggest_df
        else:
            suggest_foods =  pd.DataFrame()
        return suggest_foods
    def get_top_suggestion(self, suggest_df):
        nut_dict = {}
        if suggest_df.empty: #推薦食品dfが空の時
            nut_dict = {
                'food_name':None,
                'p':None,
                'f':None,
                'c':None
            }
        else:
            row = suggest_df.head(1).to_dict(orient='list')
            nut_dict = {
                'food_name':row['food_name'].pop(),
                'p':row['after_p'].pop(),
                'f':row['after_f'].pop(),
                'c':row['after_c'].pop(),
            }
        return nut_dict
    def adjust_rate_minus_zero(self, arg_pfc):
        if arg_pfc['c'] is not None:
            if arg_pfc['c']<0 : arg_pfc['c'] = 0 
        return arg_pfc
    def judge_pfc_score(self, pfc_diff):
        #pfc_diff -> pfc_scoreへ変換する
        pfc_score_section_df = pd.read_csv(settings.PFC_SCORE_SECTION_URL)
        if pfc_diff == 0:
            #100点の時
            pfc_score = 100
        elif pfc_score_section_df.at[100, 'section_min'] < pfc_diff:
            #0点の時
            pfc_score = 0
        #0点 < pfc_score < 100点 の時
        for s_index, s_item in pfc_score_section_df.iterrows():
            if s_item.section_min < pfc_diff <= s_item.section_max:
                pfc_score = s_item.pfc_score
                #pfc_scoreをdecimal型に変換
                pfc_score = Decimal(pfc_score).quantize(
                    Decimal('0.1'), rounding=ROUND_HALF_UP
                )
        return pfc_score

"""
グローバル関数
"""
#floatを2桁のDecimal型に変換する
def dec_conv(float_num):
    decimal_num = Decimal(float_num).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    return decimal_num

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
        #推薦する食事のリスト
        context['suggestion_food_list'] = self.get_suggestion_food_list()
        #１番目に推薦された食事の栄養情報を辞書として取得
        context['top_suggestion_pfc'] = self.get_top_suggestion(context['suggestion_food_list'])

        #pfcのrateのcが0以下の時,0に修正
        context['today_pfc'] = self.adjust_rate_minus_zero(context['today_pfc'])
        context['top_suggestion_pfc'] = self.adjust_rate_minus_zero(context['top_suggestion_pfc'])
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
    template_name = 'lognuts/log_input/search_input.html'
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
        context['columns'] = ['食べた', 'レストラン名', '食品名', 'サイズ']
        context['search_foods'] = mealsout_df
        return render(self.request, 'lognuts/log_input/search_list.html', context)

class SearchConfirm(OnlyYouMixin, ContextMixin, generic.TemplateView):
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')
        post = self.request.POST
        m_id_list = post.getlist('mealout_id', None)
        p_log_list = []
        for m_id in m_id_list:
            input_record = mealsout_df[ (mealsout_df['id'] == int(m_id)) ].iloc[0]
            p_log = self.get_personal_log_from_df(input_record)
            p_log_list.append(p_log)
        context['p_log_list'] = p_log_list
        context['columns'] = self.get_personal_log_columns()
        self.request.session['m_id_list'] = m_id_list #セッションに外食食品DBのidリストを保存
        return render(self.request, 'lognuts/log_input/search_confirm.html', context)

class SearchComplete(OnlyYouMixin, ContextMixin, generic.TemplateView):
    """食事ログをDBに格納して、結果を表示する"""
    template_name = 'lognuts/log_input/search_complete.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #外食食品DBをNaN->''としてデータフレーム化
        mealsout_df = pd.read_csv(settings.MEALSOUT_NUTS_URL).fillna('')
        p_log_list = []
        if 'm_id_list' in self.request.session:
            m_id_list = self.request.session['m_id_list']
            for m_id in m_id_list:
                input_record = mealsout_df[ (mealsout_df['id'] == int(m_id)) ].iloc[0]
                p_log = self.get_personal_log_from_df(input_record)
                p_log_list.append(p_log)
                p_log.save() #食事ログを保存
            context['p_log_list'] = p_log_list
        context['columns'] = self.get_personal_log_columns()
        return context

class ManualInput(OnlyYouMixin, ContextMixin, generic.FormView):
    """手動入力フォームからの入力を扱う"""
    template_name = 'lognuts/log_input/manual_input.html'
    form_class = ManualForm
    def form_invalid(self, form, **kwargs):
        ''' バリデーションに失敗した時 '''
        return super().form_invalid(form)
    def form_valid(self, form, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.request.POST
        self.request.session['post'] = self.request.POST #セッションにPOSTデータを保存
        context['p_log'] = self.get_personal_log_from_post(post)
        context['columns'] = self.get_personal_log_columns()
        return render(self.request, 'lognuts/log_input/manual_confirm.html', context)

class ManualComplete(OnlyYouMixin, ContextMixin, generic.TemplateView):
    """フォームの内容をDBに格納して、結果を表示する"""
    template_name = 'lognuts/log_input/manual_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'post' in self.request.session:
            session_post = self.request.session['post']
            p_log = self.get_personal_log_from_post(session_post)
            p_log.save()
            context['p_log'] = p_log
            context['columns'] = self.get_personal_log_columns()
        return context

class HistoryInput(OnlyYouMixin, ContextMixin, generic.TemplateView):

    def get(self, request, *args, **kwargs):
        """食事ログの履歴のリストを表示する"""
        self.template_name = 'lognuts/log_input/history_list.html'
        context = super().get_context_data(**kwargs)
        context['personal_log_history'] = PersonalLog.objects.filter(
            user=self.request.user,
        ).order_by('date')
        context['columns'] = ['食べた', 'レストラン名', '食品名', 'サイズ']
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """食事ログの入力確認画面を表示する"""
        self.template_name = 'lognuts/log_input/history_confirm.html'
        context = super().get_context_data(**kwargs)
        self.request.session['post'] = self.request.POST #セッションにPOSTデータを保存
        post = self.request.POST
        p_id_list = post.getlist('personal_log_id', None)
        p_log_list = []
        for p_id in p_id_list:
            p_log_queryset = PersonalLog.objects.filter(id=p_id).first()
            p_log = self.get_personal_log_from_queryset(p_log_queryset)
            p_log_list.append(p_log)
        context['columns'] = self.get_personal_log_columns()
        context['p_log_list'] = p_log_list
        self.request.session['p_id_list'] = p_id_list #セッションに食事ログidリストを保存
        return self.render_to_response(context)

class HistoryComplete(OnlyYouMixin, ContextMixin, generic.TemplateView):
    """フォームの内容をDBに格納して、結果を表示する"""
    template_name = 'lognuts/log_input/history_complete.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'p_id_list' in self.request.session:
            p_id_list = self.request.session['p_id_list']
            p_log_list = []
            for p_id in p_id_list:
                p_log_queryset = PersonalLog.objects.filter(id=p_id).first()
                p_log = self.get_personal_log_from_queryset(p_log_queryset)
                p_log_list.append(p_log)
                p_log.save() #食事ログを保存
            context['columns'] = self.get_personal_log_columns()
            context['p_log_list'] = p_log_list
        return context

class DiaryView(OnlyYouMixin, NutsCulcMixin, ContextMixin, generic.TemplateView):
    """日付ごとのページ"""
    template_name = 'lognuts/diary.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #食事ログの画像
        context['food_image_list'] = FoodImage
        #１日の食事ログのを取得
        context['log_columns'] = self.get_personal_log_columns()
        year,month,day = ( 2000+self.kwargs.get('year'),self.kwargs.get('month'),self.kwargs.get('day') ) 
        select_date = datetime.datetime(year, month, day)
        context['PersonalLog'] = PersonalLog.objects.values('date', 'food_name').filter(
            user=self.request.user
        )
        context['day_p_log_list'] = PersonalLog.objects.values(
            'date', 'restaurant', 'food_name', 'size', 'energie', 'carbohydrate',
            'protein', 'fat', 'salt'
        ).filter(
            user=self.request.user, date__date=select_date
        )
        #栄養素の可視化に利用する
        context['day_info'] = {
            'year':year,
            'month':month,
            'day':day
        }
        context['day_nut'] = self.get_day_nut( select_date )
        context['day_pfc'] = self.get_pfc( context['day_nut'] )
        context['radar_pfc_point'] = {
            'p': settings.RADAR_P,
            'f': settings.RADAR_F,
            'c': settings.RADAR_C
        }
        #pfcのrateのcが0以下の時,0に修正
        context['day_pfc'] = self.adjust_rate_minus_zero(context['day_pfc'])
        #その日付の画像を取得
        context['food_image_list'] = FoodImage.objects.filter(
            user=self.request.user, eat_date=select_date
        ).all()
        return context

class ImageUpload(OnlyYouMixin, generic.CreateView):
    model = FoodImage
    form_class = ImageUploadForm
    template_name = 'lognuts/image_upload.html'
    def get_initial(self):
        return {'user': self.request.user}
    def get_success_url(self):
        ret_reverse = reverse_lazy('lognuts:image_add_food', kwargs={
            'pk': self.kwargs['pk'],
            'year': self.kwargs['year'],
            'month': self.kwargs['month'],
            'day': self.kwargs['day'],
            })
        self.request.session['image_pk'] = self.object.id
        return ret_reverse
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] =   2000+self.kwargs.get('year')
        context['month'] =  self.kwargs.get('month')
        context['day'] =    self.kwargs.get('day')
        return context

class ImageAddFood(OnlyYouMixin, NutsCulcMixin, ContextMixin, generic.TemplateView):
    template_name = 'lognuts/image_add_food.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year,month,day = ( self.kwargs.get('year'),self.kwargs.get('month'),self.kwargs.get('day') ) 
        context['year'] =   year
        context['month'] =  month
        context['day'] =    day
        select_date = datetime.datetime(year, month, day)
        #画像のURLをDBに追加
        upload_image = FoodImage.objects.filter(
            pk=self.request.session['image_pk']
        ).first()
        upload_image.eat_date = select_date
        upload_image.save()
        context['upload_image'] = upload_image
        #該当する年月日の食事ログを取得
        context['log_columns'] = self.get_personal_log_columns()
        context['day_p_log_list'] = PersonalLog.objects.values(
            'id', 'date', 'restaurant', 'food_name', 'size', 'energie', 'carbohydrate',
            'protein', 'fat', 'salt'
        ).filter(
            user=self.request.user, date__date=select_date
        )
        return context

class ImageComplete(OnlyYouMixin, NutsCulcMixin, ContextMixin, generic.TemplateView):
    template_name = 'lognuts/image_complete.html'
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        #アップロードした画像を取得
        upload_image = FoodImage.objects.filter(
            pk=self.request.session['image_pk']
        ).first()
        #食事ログのidリストを取得
        p_id_list = self.request.POST.getlist('mealout_id')
        #食事ログのリストを取得
        p_log_list = []
        for p_id in p_id_list:
            p_log = PersonalLog.objects.filter(id=p_id).first()
            # 食事画像のidを追加して食事ログを更新
            p_log.food_image_id = upload_image
            p_log.save()
            p_log_list.append(p_log)
        context['columns'] = self.get_personal_log_columns()
        context['p_log_list'] = p_log_list
        #アップロードした画像に栄養情報を付与
        upload_image.energie = 0
        upload_image.protein = 0
        upload_image.fat = 0
        upload_image.carbohydrate = 0
        upload_image.salt = 0
        for p_log in p_log_list:
            upload_image.energie += p_log.energie
            upload_image.protein += p_log.protein
            upload_image.fat += p_log.fat
            upload_image.carbohydrate += p_log.carbohydrate
            upload_image.salt += p_log.salt
        #付与された栄養情報からp,f,cの比率を計算
        img_nut = {
            'energie':upload_image.energie,
            'protein':upload_image.protein,
            'fat':upload_image.fat
        }
        img_pfc = self.get_pfc(img_nut)
        upload_image.p_rate = img_pfc['p']
        upload_image.f_rate = img_pfc['f']
        upload_image.c_rate = img_pfc['c']
        #p,f,cの比率からpfc_diffを算出
        img_pfc_diff = self.get_pfc_diff(img_pfc)
        upload_image.p_diff = img_pfc_diff['p_diff']
        upload_image.f_diff = img_pfc_diff['f_diff']
        upload_image.c_diff = img_pfc_diff['c_diff']
        upload_image.pfc_diff = img_pfc_diff['pfc_diff']
        upload_image.pfc_score = self.judge_pfc_score(img_pfc_diff['pfc_diff'])
        upload_image.save()
        return self.render_to_response(context)

class ImageRanking(OnlyYouMixin, NutsCulcMixin, ContextMixin, generic.TemplateView):
    template_name = 'lognuts/image_ranking.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #アップロードした画像を取得
        #その日付の画像を取得
        food_images = FoodImage.objects.all().order_by('pfc_diff')
        food_list = []
        for f in food_images:
            p_log = PersonalLog.objects.all().filter(
                food_image_id=f
            )
            food_list.append( (f, p_log) )
        context['food_list'] = food_list
        return context
