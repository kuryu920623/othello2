from django.http import HttpResponse
from django.shortcuts import render
import json
from othello2.parts.main_class import PlayerCharacter, Board


# 盤面情報からPCが置いた後の盤面情報と次に置ける位置を返却
def pc_turn(request):
    params = request.GET
    color = int(params['color']) * -2 + 3
    list2D = json.loads(params['board'])
    black, white = Board.list2D2bit(list2D)
    board_obj = Board(black, white)
    pc = PlayerCharacter(color)
    bit = pc.get_best_move_bit(board_obj)
    board_obj = board_obj.put_stone(bit, color)
    if board_obj.has_legal(-color):
        next_color = int((color + 3) / 2)
        legal = board_obj.bit2list2D(board_obj.get_legal_bit(-color), 0)
    elif board_obj.has_legal(color):
        next_color = int((-color + 3) / 2)
        legal = board_obj.bit2list2D(board_obj.get_legal_bit(color), 0)
    else:
        next_color = 0
        legal = [(['0'] * 8)] * 8
    ret = {
        'board': board_obj.bit2list2D(),
        'next_color': next_color,
        'legal': legal,
    }
    return HttpResponse(json.dumps(ret))


# 盤面情報と手動で置いた位置から、置いた後の盤面情報を返却
# リクエストは　1,2 だけど こっちでは 1,-1
def manual_turn(request):
    params = request.GET
    color = int(params['color']) * -2 + 3
    pos = 1 << int(params['position'])
    list2D = json.loads(params['board'])
    black, white = Board.list2D2bit(list2D)
    board_obj = Board(black, white)
    board_obj = board_obj.put_stone(pos, color)
    if board_obj.has_legal(-color):
        next_color = int((color + 3) / 2)
        legal = board_obj.bit2list2D(board_obj.get_legal_bit(-color), 0)
    elif board_obj.has_legal(color):
        next_color = int((-color + 3) / 2)
        legal = board_obj.bit2list2D(board_obj.get_legal_bit(color), 0)
    else:
        next_color = 0
        legal = [(['0'] * 8)] * 8
    ret = {
        'board': board_obj.bit2list2D(),
        'next_color': next_color,
        'legal': legal,
    }
    return HttpResponse(json.dumps(ret))


def menu(request):
    return render(request, 'othello2/menu.html', {})


def play(request):
    color = request.POST['color']
    num_color = {'black': 1, 'white': 2}[color]
    return render(request, 'othello2/play.html', {'color': num_color})
