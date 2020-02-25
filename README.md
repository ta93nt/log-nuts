# log-nuts
食事ログを入力することで、栄養バランスを整える食品の推薦や栄養素の可視化をしてくれるアプリです。

# Demo
- ３種類の方法で食事ログの記録が簡単にできます。
![result](https://github.com/ta93nt/log-nuts/blob/media/demo/lognuts_200217.gif)
- 『料理画像 × 食事ログ』を組み合わせることで、料理画像あたりの栄養スコアを算出、ランキング表示します。
![result](https://github.com/ta93nt/log-nuts/blob/media/demo/image_ranking_demo.gif)

## Version
- python 3.7.6
- Django 3.0.2

## Requirement
- django-bootstrap4  1.1.1  
- django-environ     0.4.5  
- django-mathfilters 0.4.0
- Pillow 2.2.2

## Usage
`python manage.pyt runserver` を実行した後に、
<http://localhost:8000/lognuts>　へアクセス
