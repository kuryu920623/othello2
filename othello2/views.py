from django.http import HttpResponse
from operator import mul

# 盤面情報からPCが置いた後の盤面情報と次に置ける位置を返却
def pc_turn(request):
    b = Board()
    b.get_putable_bit(1)
    return HttpResponse('html')

# 盤面情報と手動で置いた位置から、置いた後の盤面情報を返却
def manual_turn(request):
    return HttpResponse('html')

# デバッグ用
def print_bit(bit):
    tmp = format(bit, 'b').zfill(64)
    for i in range(8):
        print(tmp[i*8:i*8+8])
    print()

# 黒=1, 白=2

class Board(object):
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

    @classmethod
    def board_to_bit(board_2d):
        return 0x0000000810000000, 0x0000001008000000

    @classmethod
    def bit_to_board(self, black, white):
        return [[0] * 8] * 8

    # 盤面のbit(blackとwhite)
    def __init__(self, black=None, white=None):
        self.black = black or 0x0000000810000000
        self.white = white or 0x0000001008000000

    # color が置ける位置のbitを取得
    def get_putable_bit(self, color):
        legal_borad = 0x0000000000000000
        blank_bit = ~(self.black | self.white)

        my_bit = self.black
        opp_bit = self.white

        horizontal_watch = opp_bit & 0x7e7e7e7e7e7e7e7e
        vertical_watch = opp_bit & 0x00ffffffffffff00
        diagonal_watch = opp_bit & 0x007e7e7e7e7e7e00

        tmp = horizontal_watch & (my_bit << 1)
        for _ in range(5):
            tmp = tmp | (horizontal_watch & (tmp << 1))
        legal_borad = legal_borad | (blank_bit & (tmp << 1))
        tmp = horizontal_watch & (my_bit >> 1)
        for _ in range(5):
            tmp = tmp | (horizontal_watch & (tmp >> 1))
        legal_borad = legal_borad | (blank_bit & (tmp >> 1))

        tmp = vertical_watch & (my_bit >> 8)
        for _ in range(5):
            tmp = tmp | (vertical_watch & (tmp >> 8))
        legal_borad = legal_borad | (blank_bit & (tmp >> 8))
        tmp = vertical_watch & (my_bit << 8)
        for _ in range(5):
            tmp = tmp | (vertical_watch & (tmp << 8))
        legal_borad = legal_borad | (blank_bit & (tmp << 8))

        tmp = diagonal_watch & (my_bit >> 7)
        for _ in range(5):
            tmp = tmp | (diagonal_watch & (tmp >> 7))
        legal_borad = legal_borad | (blank_bit & (tmp >> 7))
        tmp = diagonal_watch & (my_bit << 7)
        for _ in range(5):
            tmp = tmp | (diagonal_watch & (tmp << 7))
        legal_borad = legal_borad | (blank_bit & (tmp << 7))

        tmp = diagonal_watch & (my_bit >> 9)
        for _ in range(5):
            tmp = tmp | (diagonal_watch & (tmp >> 9))
        legal_borad = legal_borad | (blank_bit & (tmp >> 9))
        tmp = diagonal_watch & (my_bit << 9)
        for _ in range(5):
            tmp = tmp | (diagonal_watch & (tmp << 9))
        legal_borad = legal_borad | (blank_bit & (tmp << 9))

        print_bit(legal_borad)
        return legal_borad

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
