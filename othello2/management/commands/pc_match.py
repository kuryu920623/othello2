from django.core.management.base import BaseCommand
from othello2.parts.main_class import Board, PlayerCharacter as PlayerCharacterBase
from ...models import PlayerCharacters
import itertools
import random
import json
import uuid
import datetime
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        max_generation = 100
        for _ in range(options['count']):
            winner = [PlayerCharacter(1, [100, -40, 20, 20, -60, -10, -10, 20, 10, 10], [8, 15, 0]), None]
            process_uuid = uuid.uuid4()
            start_date_time = datetime.datetime.now()
            for gen in range(1, max_generation + 1):
                obj = Tournament(winner[0])
                winner = obj.match_n()
                dic = {
                    'board_scores': ','.join(map(str, winner[0].board_scores)),
                    # 'board_score_black': json.dumps(winner[0].score_index),
                    # 'board_score_white': json.dumps(winner[1].score_index),
                    'weight1': winner[0].weights[0],
                    'weight2': winner[0].weights[1],
                    'weight3': winner[0].weights[2],
                    'generation': gen,
                    'process_uuid': process_uuid,
                }
                for num in range(1, 11):
                    key = f'score{str(num).zfill(2)}'
                    dic[key] = winner[0].board_scores[num - 1]
                pc = PlayerCharacters.objects.create(**dic)
                if (datetime.datetime.now() - start_date_time) > datetime.timedelta(minutes=options['limit']) or gen == max_generation:
                    pc.is_last_gen = True
                    pc.board_score_black = json.dumps(winner[0].score_index)
                    pc.board_score_white = json.dumps(winner[1].score_index)
                    pc.save()
                    break
                del obj, dic, pc
                # print(f'generation{str(gen).zfill(4)}', winner_black.board_scores, winner_black.weights)

    def add_arguments(self, parser):
        parser.add_argument('-count', dest='count', type=int, default=10)
        parser.add_argument('-limit', dest='limit', type=int, default=30)
        return parser


class PlayerCharacter(PlayerCharacterBase):
    def __init__(self, color, board_scores=None, weingts=None, recursive_depth=2):
        super().__init__(color, board_scores, weingts, recursive_depth)
        self.read_last_turn = 55


class Tournament(object):
    def __init__(self, base_player=None):
        self.players = [self.create_player(base_player) for i in range(16)]
        self.remain = self.players

    def create_player(self, base_player=None):
        if not base_player:
            board_scores = [random.randrange(-99, 100) for i in range(10)]
            weights = [random.randrange(1, 11) for i in range(3)]
        else:
            base_scores = base_player.board_scores
            board_scores = [i + random.randrange(-5, 6) for i in base_scores]
            base_weights = base_player.weights
            weights = [i + random.randrange(-1, 2) for i in base_weights]
        p_black = PlayerCharacter(1, board_scores, weights)
        p_white = PlayerCharacter(-1, board_scores, weights)
        # print(board_scores, weights)
        return [p_black, p_white]

    def match_n(self):
        if len(self.remain) == 1:
            return self.remain[0]
        winners = []
        for i in range(0, len(self.remain), 2):
            black = self.remain[i][0]
            white = self.remain[i + 1][1]
            match_obj = PCOneMatch(black, white)
            win = match_obj.match()
            winners.append(self.remain[i + win])
        self.remain = winners
        return self.match_n()


class PCOneMatch(object):
    def __init__(self, black, white):
        self.board = Board(0x0000000810000000, 0x0000001008000000)
        self.players = {1: black, -1: white}

    def match(self):
        for color in itertools.cycle([1, -1]):
            self.pc_turn(color)
            if self.board.is_game_over():
                break
        black_count = self.board.count_bit(self.board.black)
        white_count = self.board.count_bit(self.board.white)
        if black_count > white_count:
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
