from django.db import models


class PlayerCharacters(models.Model):
    borad_scores = models.CharField('カンマ区切りスコア', max_length=50, unique=True, db_index=True)
    score01 = models.SmallIntegerField()
    score02 = models.SmallIntegerField()
    score03 = models.SmallIntegerField()
    score04 = models.SmallIntegerField()
    score05 = models.SmallIntegerField()
    score06 = models.SmallIntegerField()
    score07 = models.SmallIntegerField()
    score08 = models.SmallIntegerField()
    score09 = models.SmallIntegerField()
    score10 = models.SmallIntegerField()
    borad_score_black = models.TextField('黒のスコアインデックスを計算したJSON')
    borad_score_white = models.TextField('白のスコアインデックスを計算したJSON')
    weight1 = models.SmallIntegerField()
    weight2 = models.SmallIntegerField()
    weight3 = models.SmallIntegerField()
    match_count = models.IntegerField('試合数', default=0)
    win_count = models.IntegerField('勝ち数', default=0)
    lose_count = models.IntegerField('負け数', default=0)
    total_stone = models.IntegerField('試合終了時の石の数の合計', default=0)
