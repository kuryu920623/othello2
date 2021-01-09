from django.core.management.base import BaseCommand
from othello2.parts.main_class import Board, PlayerCharacter as PlayerCharacterBase
from ...models import PlayerCharacters
import itertools
import json
import gc


class Command(BaseCommand):
    def handle(self, *args, **options):
        obj = BruteForce()
        obj.start()

    def add_arguments(self, parser):
        parser.add_argument('-count', dest='count', type=int, default=10)
        parser.add_argument('-limit', dest='limit', type=int, default=30)
        return parser


class PlayerCharacter(PlayerCharacterBase):
    def __init__(self, color, board_scores=None, weingts=None, recursive_depth=2, score_index=None):
        super().__init__(color, board_scores, weingts, recursive_depth)
        self.read_last_turn = 55
        self.score_index = score_index

    def init_board_scores_dict(self):
        return


class BruteForce(object):
    def __init__(self, base_player=None):
        self.players = self.init_players()

    # [[obj, p_black, p_white], obj, p_black, p_white], ...]
    def init_players(self):
        players = []
        objs = PlayerCharacters.objects.filter(is_last_gen=1).order_by('?')[:20]
        for obj in objs:
            weingts = [obj.weight1, obj.weight2, obj.weight3]
            score_index_black = [{int(key): val for key, val in dic.items()} for dic in json.loads(obj.board_score_black)]
            score_index_white = [{int(key): val for key, val in dic.items()} for dic in json.loads(obj.board_score_white)]
            p_black = PlayerCharacter(1, obj.board_scores.split(','), weingts, score_index=score_index_black)
            p_white = PlayerCharacter(-1, obj.board_scores.split(','), weingts, score_index=score_index_white)
            players.append([obj, p_black, p_white])
        return players

    def start(self):
        for _black, _white in itertools.permutations(self.players, 2):
            match_obj = PCOneMatch(_black[1], _white[2])
            win = match_obj.match()
            _black[0].match_count += 1
            _white[0].match_count += 1
            [_black, _white][win][0].win_count += 1
            [_black, _white][(win + 1) % 2][0].lose_count += 1
            _black[0].total_stone += match_obj.black_stone_count
            _white[0].total_stone += match_obj.black_stone_count
            _black[0].save()
            _white[0].save()
            del match_obj, _black, _white
            gc.collect()


class PCOneMatch(object):
    def __init__(self, black, white):
        self.board = Board(0x0000000810000000, 0x0000001008000000)
        self.players = {1: black, -1: white}

    def match(self):
        for color in itertools.cycle([1, -1]):
            self.pc_turn(color)
            if self.board.is_game_over():
                break
        self.black_stone_count = self.board.count_bit(self.board.black)
        self.white_stone_count = self.board.count_bit(self.board.white)
        if self.black_stone_count > self.white_stone_count:
            return 0
        else:
            return 1

    def pc_turn(self, color):
        if not self.board.has_legal(color):
            return
        player = self.players[color]
        put = player.get_best_move_bit(self.board)
        if put:
            self.board = self.board.put_stone(put, color)
