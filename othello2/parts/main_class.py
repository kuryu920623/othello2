import itertools
from operator import mul
from django.conf import settings


class BaseTools(object):
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
    def iter_bit(cls, bit):
        while bit:
            yield bit & -bit
            bit &= bit - 1

    @classmethod
    def bit2list(cls, bit, length):
        li = [i for i in cls.iter_str_bit(bit, length)]
        return li

    @classmethod
    def iter_str_bit(cls, bit, length):
        for i in range(length):
            yield 1 & (bit >> (length - 1 - i))


class Board(BaseTools):
    def get_bit(self, color):
        return {1: self.black, -1: self.white}[color]

    # 盤面のbit(blackとwhite)
    def __init__(self, black, white):
        self.black = black
        self.white = white

    # color が置ける位置のbitを取得
    def get_legal_bit(self, color):
        legal_bit = 0x0
        blank_bit = ~(self.black | self.white)

        my_bit = self.get_bit(color)
        opp_bit = self.get_bit(-color)

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

        legal_bit |= update_legal_bit(horizontal_watch, 1)  # 横方向
        legal_bit |= update_legal_bit(vertical_watch, 8)  # 縦方向
        legal_bit |= update_legal_bit(diagonal_watch, 7)  # 左下から右上
        legal_bit |= update_legal_bit(diagonal_watch, 9)  # 右下から左上

        return legal_bit

    # color が置ける位置の数を取得
    def get_legal_count(self, color):
        return self.count_bit(self.get_legal_bit(color))

    # 盤面に対して color のおける場所が存在するか
    def has_legal(self, color):
        return bool(self.get_legal_count(color))

    # 次の一手が何手目になるか
    def get_turn(self):
        return self.count_bit(self.black | self.white) - 3

    def is_game_over(self):
        return not self.has_legal(1) and not self.has_legal(-1)

    def reverse_right(self, mask, offset, my_bit, opp_bit, put_bit):
        opp_bit_mask = opp_bit & mask
        move_tmp1 = (put_bit >> offset) & opp_bit_mask
        move_tmp2 = (my_bit << offset) & opp_bit_mask
        for i in range(5):
            move_tmp1 |= (move_tmp1 >> offset) & opp_bit_mask
            move_tmp2 |= (move_tmp2 << offset) & opp_bit_mask
        return move_tmp1 & move_tmp2

    def reverse_left(self, mask, offset, my_bit, opp_bit, put_bit):
        opp_bit_mask = opp_bit & mask
        move_tmp1 = (put_bit << offset) & opp_bit_mask
        move_tmp2 = (my_bit >> offset) & opp_bit_mask
        for i in range(5):
            move_tmp1 |= (move_tmp1 << offset) & opp_bit_mask
            move_tmp2 |= (move_tmp2 >> offset) & opp_bit_mask
        return move_tmp1 & move_tmp2

    # bitの位置に color を置いた場合の Board オブジェクトを返却
    def put_stone(self, put_bit, color):
        horizontal_mask = 0x7e7e7e7e7e7e7e7e
        vertical_mask = 0xffffffffffffffff
        my_bit = self.get_bit(color)
        opp_bit = self.get_bit(-color)

        move_all = 0x0
        move_all |= self.reverse_right(horizontal_mask, 1, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_left(horizontal_mask, 1, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_right(horizontal_mask, 7, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_left(horizontal_mask, 7, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_right(vertical_mask, 8, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_left(vertical_mask, 8, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_right(horizontal_mask, 9, my_bit, opp_bit, put_bit)
        move_all |= self.reverse_left(horizontal_mask, 9, my_bit, opp_bit, put_bit)

        new_black = (self.black ^ move_all) | (put_bit * (color + 1) >> 1)
        new_white = (self.white ^ move_all) | (put_bit * (-color + 1) >> 1)
        return Board(new_black, new_white)

    def bit2list2D(self, black=None, white=None):
        # 空白:0, 黒:1, 白:2
        black = format(black or self.black, 'b').zfill(64)
        white = format(white or self.white, 'b').zfill(64).replace('1', '2')
        board = []
        for i in range(8):
            row = []
            for j in range(8):
                n = i * 8 + j
                row.append(str(int(black[n]) or int(white[n]) or 0))
            board.append(row)
        return board

    @classmethod
    def list2D2bit(self, list2D):
        # 空白:0, 黒:1, 白:2
        list1D = ''.join(list(itertools.chain.from_iterable(list2D)))
        black_str = list1D.replace('2', '0')
        white_str = list1D.replace('1', '0').replace('2', '1')
        return int(black_str, 2), int(white_str, 2)

    def print_board(self):
        black = format(self.black, 'b').zfill(64)
        white = format(self.white, 'b').zfill(64)
        i = 0
        for i in range(8):
            row = []
            for j in range(8):
                n = i * 8 + j
                if black[n] == '1':
                    word = '● '
                elif white[n] == '1':
                    word = '○ '
                else:
                    word = str(63 - n).zfill(2)
                row.append(word)
            print(' '.join(row))
        print()


class PlayerCharacter(BaseTools):
    def __init__(self, color, borad_scores=None, weights=settings.BASE_WEIGHTS, recursive_depth=6):
        self.color = color
        self.borad_scores = borad_scores or settings.BASE_BOARD_SCORE
        self.weights = weights
        self.recursive_depth = recursive_depth
        self.borad_score_dict = self.__init_borad_scores_dict()
        self.read_last_turn = 50

    def __init_borad_scores_dict(self):
        self.score_index = []
        for i in range(4):
            pos_score = [
                [0, 1, 2, 3, 3, 2, 1, 0],
                [1, 4, 5, 6, 6, 5, 4, 1],
                [2, 5, 7, 8, 8, 7, 5, 2],
                [3, 6, 8, 9, 9, 8, 6, 3],
            ][i]
            pos_score = [self.borad_scores[i] for i in pos_score]
            dic = {}
            for b_or_w in range(0b100000000):
                li = [single_bit for single_bit in self.iter_bit(b_or_w)]
                mask_range = 1 << len(li)
                for mask in range(mask_range):
                    mask_li = self.bit2list(mask, len(li))
                    black = sum(map(mul, mask_li, li))
                    white = b_or_w - black
                    index = (white << 8) | black
                    li2 = [b - w for b, w in zip(self.bit2list(black, 8), self.bit2list(white, 8))]
                    dic[index] = sum(map(mul, pos_score, li2)) * self.color
            self.score_index.append(dic)

    def get_preferred_score(self, color, score1, score2):
        return max(score1, score2) if (self.color + color) else min(score1, score2)

    def is_iter_done(self, color, ret_score, score_upper_level):
        return ret_score >= score_upper_level if (self.color + color) else ret_score <= score_upper_level

    def get_best_move_bit(self, start_board_obj):
        culculator = self.recursive
        if start_board_obj.get_turn() > self.read_last_turn:
            culculator = self.recursive_last
        move_bit = None
        score_top_level = -(1 << 20)
        self.count = 0
        for bit_top in self.iter_bit(start_board_obj.get_legal_bit(self.color)):
            obj2 = start_board_obj.put_stone(bit_top, self.color)
            score_bottom_level = culculator(obj2, -self.color, score_upper_level=score_top_level, depth=1)
            if score_top_level < score_bottom_level:
                score_top_level = score_bottom_level
                move_bit = bit_top
        return move_bit

    def recursive(self, board_obj, color, score_upper_level, depth):
        if depth > self.recursive_depth - 1:
            return self.culc_borad_total_score(board_obj)
        legal_bits = board_obj.get_legal_bit(color)
        ret_score = -(1 << 20) * color * self.color

        if not legal_bits:
            legal_bits_opp = board_obj.get_legal_bit(-color)
            if not legal_bits_opp:
                return (self.count_bit(board_obj.black) - self.count_bit(board_obj.white)) * (1 << 21) * self.color
            else:
                return self.recursive(board_obj, -color, ret_score, depth + 1)

        for bit in self.iter_bit(legal_bits):
            # print(depth + 1, color, bit_to_number(bit))
            self.count += 1
            next_board_obj = board_obj.put_stone(bit, color)
            score = self.recursive(next_board_obj, -color, ret_score, depth + 1)
            ret_score = self.get_preferred_score(color, ret_score, score)
            if self.is_iter_done(color, ret_score, score_upper_level):
                return ret_score

        return ret_score

    def recursive_last(self, board_obj, color, score_upper_level, depth):
        legal_bits = board_obj.get_legal_bit(color)
        ret_score = -(1 << 20) * color * self.color
        if not legal_bits:
            legal_bits_opp = board_obj.get_legal_bit(-color)
            if not legal_bits_opp:
                return (self.count_bit(board_obj.black) - self.count_bit(board_obj.white)) * self.color
            else:
                return self.recursive_last(board_obj, -color, ret_score, depth)

        for bit in self.iter_bit(legal_bits):
            self.count += 1
            next_board_obj = board_obj.put_stone(bit, color)
            score = self.recursive_last(next_board_obj, -color, ret_score, depth)
            ret_score = self.get_preferred_score(color, ret_score, score)
            if self.is_iter_done(color, ret_score, score_upper_level):
                return ret_score

        return ret_score

    def culc_borad_total_score(self, board_obj):
        bs = self.board_position_score(board_obj)
        ps = self.legal_position_score(board_obj)
        fs = self.fixed_stone_score(board_obj)
        return sum(map(mul, self.weights, [bs, ps, fs]))

    def culc_stones(self, board_obj):
        return (self.count_bit(board_obj.black) - self.count_bit(board_obj.white)) * self.color

    # 盤面の位置に対する得点
    def board_position_score(self, board_obj):
        total = 0
        for row in range(8):
            mask = 0x00000000000000ff << (8 * row)
            bit = ((board_obj.black & mask) | ((board_obj.white & mask) << 8)) >> (8 * row)
            total += self.score_index[row if row <= 3 else 7 - row][bit]
        return total

    # 盤面に石を置ける位置の数の得点
    def legal_position_score(self, board_obj):
        return (board_obj.get_legal_count(1) - board_obj.get_legal_count(-1)) * self.color

    # 確定石の数の得点
    def fixed_stone_score(self, board_obj):
        return 0
