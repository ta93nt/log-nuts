# log-nuts
食事ログを入力することで、栄養バランスを整える食品の推薦や栄養素の可視化をしてくれるアプリです。
[https://lognuts.herokuapp.com/lognuts/](https://lognuts.herokuapp.com/lognuts/)

## Demo Log-Input
- ３種類の方法で食事ログの記録が簡単にできます。
![result](https://github.com/ta93nt/log-nuts/blob/media/demo/lognuts_200217.gif)

## Demo Image-Ranking
- 『料理画像 × 食事ログ』を組み合わせることで、料理画像あたりの栄養スコアを算出、ランキング表示します。
![result](https://github.com/ta93nt/log-nuts/blob/media/demo/image_ranking_demo.gif)

## Version
- python 3.7.6
- Django 3.0.2

## Requirement
- asgiref==3.2.3
- beautifulsoup4==4.8.2
- certifi==2019.11.28
- chardet==3.0.4
- Django==3.0.3
- django-bootstrap4==1.1.1
- django-environ==0.4.5
- django-mathfilters==0.4.0
- docopt==0.6.2
- idna==2.9
- mysqlclient==1.4.6
- numpy==1.18.1
- pandas==1.0.0
- Pillow==7.0.0
- pipreqs==0.4.10
- protobuf==3.11.2
- python-dateutil==2.8.1
- pytz==2019.3
- requests==2.23.0
- six==1.13.0
- soupsieve==1.9.5
- sqlparse==0.3.0
- urllib3==1.25.8
- yarg==0.1.9

## Usage
`python manage.pyt runserver` を実行した後に、
<http://localhost:8000/lognuts>　へアクセス
