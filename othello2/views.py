from django.http import HttpResponse
from operator import mul

def pc_turn(request):
    return HttpResponse('html')

def manual_turn(request):
    return HttpResponse('html')

# 黒=1, 白=2

class Board(object):
    # 盤面のbit(blackとwhite)
    def __init__(self, black, white):
        self.black = black or 0x0000000810000000
        self.white = white or 0x0000001008000000

    # bitのビット数をカウントする。
    @classmethod
    def count_bit(bit):
        tmp = (bit & 0x5555555555555555) + (bit >> 1 & 0x5555555555555555)
        tmp = (tmp & 0x3333333333333333) + (tmp >> 2 & 0x3333333333333333)
        tmp = (tmp & 0x0f0f0f0f0f0f0f0f) + (tmp >> 4 & 0x0f0f0f0f0f0f0f0f)
        tmp = (tmp & 0x00ff00ff00ff00ff) + (tmp >> 8 & 0x00ff00ff00ff00ff)
        tmp = (tmp & 0x0000ffff0000ffff) + (tmp >> 16 & 0x0000ffff0000ffff)
        ret = (tmp & 0x00000000ffffffff) + (tmp >> 32 & 0x00000000ffffffff)
        return ret

    # color が置ける位置のbitを取得
    def get_putable_bit(self, color):
        return 0x0000000810000000

    # color が置ける位置の数を取得
    def get_putable_count(self, color):
        return self.count_bit(self.get_putable_bit(color))

    # 盤面に対して color のおける場所が存在するか
    def is_putable(self, color):
        return bool(get_putable(color))

    def is_game_over(self):
        return not is_putable(1) and not is_putable(2)

    # bitの位置に color を置いた場合の Board オブジェクトを返却
    def put_stone(self, bit, color):
        return Board(self.black, self.white)

    # bitをボードの2次元配列に変換する。
    def bit_to_board(self):
        return [[0] * 8] * 8


class PlayerCharacter(object):
    def __init__(self, color, borad_scores=None, weingts=[1, 1, 1]):
        self.color = color
        self.borad_scores = borad_scores
        self.weingts = weingts

    def culc_borad_total_score(self, board_obj):
        bs = self.board_position_score(board_obj)
        ps = self.putable_position_score(board_obj)
        fs = self.fixed_stone_score(board_obj)
        return sum(map(mul, self.weingts, [bs, ps, fs]))

    # 盤面の位置に対する得点
    def board_position_score(self, board_obj):
        return 1

    # 盤面に石を置ける位置の数の得点
    def putable_position_score(self, board_obj):
        my_count = board_obj.get_putable_count(self.color)

    # 確定石の数の得点
    def fixed_stone_score(self, board_obj):
        return 0
