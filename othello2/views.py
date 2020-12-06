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
    def count_bit(cls, bit):
        tmp = (bit & 0x5555555555555555) + (bit >> 1 & 0x5555555555555555)
        tmp = (tmp & 0x3333333333333333) + (tmp >> 2 & 0x3333333333333333)
        tmp = (tmp & 0x0f0f0f0f0f0f0f0f) + (tmp >> 4 & 0x0f0f0f0f0f0f0f0f)
        tmp = (tmp & 0x00ff00ff00ff00ff) + (tmp >> 8 & 0x00ff00ff00ff00ff)
        tmp = (tmp & 0x0000ffff0000ffff) + (tmp >> 16 & 0x0000ffff0000ffff)
        ret = (tmp & 0x00000000ffffffff) + (tmp >> 32 & 0x00000000ffffffff)
        return ret

    @classmethod
    def board_to_bit(cls, board_2d):
        return 0x0000000810000000, 0x0000001008000000

    def bit_to_board(self):
        return [[0] * 8] * 8

    def get_bit(self, color):
        return {1: self.black, 2: self.white}[color]

    # 盤面のbit(blackとwhite)
    def __init__(self, black, white):
        self.black = black
        self.white = white

    # color が置ける位置のbitを取得
    def get_putable_bit(self, color):
        legal_bit = 0x0
        blank_bit = ~(self.black | self.white)

        my_bit = self.get_bit(color)
        opp_bit = self.get_bit(color % 2 + 1)

        horizontal_watch = opp_bit & 0x7e7e7e7e7e7e7e7e
        vertical_watch = opp_bit & 0x00ffffffffffff00
        diagonal_watch = opp_bit & 0x007e7e7e7e7e7e00

        def update_legal_bit(watch, offset):
            ret = 0x0
            tmp = watch & (my_bit << offset)
            for _ in range(5):
                tmp |= watch & (tmp << offset)
            ret |= blank_bit & (tmp << offset)
            tmp = watch & (my_bit >> offset)
            for _ in range(5):
                tmp |= watch & (tmp >> offset)
            ret |= blank_bit & (tmp >> offset)
            return ret

        legal_bit |= update_legal_bit(horizontal_watch, 1) # 横方向
        legal_bit |= update_legal_bit(vertical_watch, 8) # 縦方向
        legal_bit |= update_legal_bit(diagonal_watch, 7) # 左下から右上
        legal_bit |= update_legal_bit(diagonal_watch, 9) # 右下から左上

        return legal_bit

    # color が置ける位置の数を取得
    def get_putable_count(self, color):
        return self.count_bit(self.get_putable_bit(color))

    # 盤面に対して color のおける場所が存在するか
    def is_putable(self, color):
        return bool(get_putable(color))

    # 次の一手が何手目になるか
    def get_turn(self):
        return cls.count_bit(self.black | self.while) - 3

    def is_game_over(self):
        return not is_putable(1) and not is_putable(2)

    # bitの位置に color を置いた場合の Board オブジェクトを返却
    def put_stone(self, put_bit, color):
        horizontal_mask = 0x7e7e7e7e7e7e7e7e
        vertical_mask = 0xffffffffffffffff
        my_bit = self.get_bit(color)
        opp_bit = self.get_bit(color % 2 + 1)

        def reverse_right(mask, offset):
            opp_bit_mask = opp_bit & mask
            move_tmp1 = (put_bit >> offset) & opp_bit_mask
            move_tmp2 = (my_bit << offset) & opp_bit_mask
            for i in range(5):
                move_tmp1 |= (move_tmp1 >> offset) & opp_bit_mask
                move_tmp2 |= (move_tmp2 << offset) & opp_bit_mask
            return move_tmp1 & move_tmp2
        def reverse_left(mask, offset):
            opp_bit_mask = opp_bit & mask
            move_tmp1 = (put_bit << offset) & opp_bit_mask
            move_tmp2 = (my_bit >> offset) & opp_bit_mask
            for i in range(5):
                move_tmp1 |= (move_tmp1 << offset) & opp_bit_mask
                move_tmp2 |= (move_tmp2 >> offset) & opp_bit_mask
            return move_tmp1 & move_tmp2

        move_all = 0x0
        move_all |= reverse_right(horizontal_mask, 1)
        move_all |= reverse_left(horizontal_mask, 1)
        move_all |= reverse_right(horizontal_mask, 7)
        move_all |= reverse_left(horizontal_mask, 7)
        move_all |= reverse_right(vertical_mask, 8)
        move_all |= reverse_left(vertical_mask, 8)
        move_all |= reverse_right(horizontal_mask, 9)
        move_all |= reverse_left(horizontal_mask, 9)

        new_black = (self.black ^ move_all) | (put_bit * (color % 2))
        new_white = (self.white ^ move_all) | (put_bit * (color - 1))
        return Board(new_black, new_white)

    def print_board(self):
        borad = [[str(i) + str(j) for j in range(8)] for i in range(8)]
        black = format(self.black, 'b').zfill(64)
        white = format(self.white, 'b').zfill(64)
        i = 0
        for i in range(8):
            row = []
            for j in range(8):
                n = i * 8 + j
                if black[n] == '1':
                    word = 'b '
                elif white[n] == '1':
                    word = 'w '
                else:
                    word = str(63 - n).zfill(2)
                row.append(word)
            print(' '.join(row))
        print()

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

b = Board(0x0000000810000000, 0x0000001008000000)
while True:
    b.print_board()
    li = input('pos,color >>> ').split(',')
    pos = 2 ** int(li[0])
    color = {'1': 1, 'b': 1, '2': 2, 'w': 2}[li[1]]
    b = b.put_stone(pos, color)
