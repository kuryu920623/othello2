'use strict';
var infoBoard = [
  ['0', '0', '0', '0', '0', '0', '0', '0'],
  ['0', '0', '0', '0', '0', '0', '0', '0'],
  ['0', '0', '0', '0', '0', '0', '0', '0'],
  ['0', '0', '0', '1', '2', '0', '0', '0'],
  ['0', '0', '0', '2', '1', '0', '0', '0'],
  ['0', '0', '0', '0', '0', '0', '0', '0'],
  ['0', '0', '0', '0', '0', '0', '0', '0'],
  ['0', '0', '0', '0', '0', '0', '0', '0'],
]
var isGameOver = false

window.addEventListener('DOMContentLoaded', function(event){
  function startTurn(color){
    let message2 = {1: '黒番', 2: '白番'}[infoNextTurn]
    if (infoNextTurn == infoManualColor) {
        message2 += '(あなた)'
    } else {
        message2 += '(PC)'
    }
    $('p#message2').text(message2)
    if (isGameOver){
      return
    }
    if (infoManualColor==color){
      manualTurn(color)
    } else {
      pcTurn(color)
    }
  }

  function manualTurn(color){
    let blanks = $('#board tr td.blank.legal')
    blanks.on('click', function(event){
      $('#board tr td').off("click");
      let position = $(event.target).data('position')
      let url = location.origin + '/othello2/api/manual_turn'
      let params = {
        'position': position,
        'color': color,
        'board': JSON.stringify(infoBoard)
      }
      $.ajax(
        url, {data: params}
      ).done(function(data)
        {
          data = JSON.parse(data)
          updateBoard(data['board'], data['legal'])
          infoNextTurn = data['next_color']
          if (infoNextTurn==0){
            isGameOver = true
          }
          startTurn(infoNextTurn)
        }
      )
    })
  }

  function pcTurn(color){
    let url = location.origin + '/othello2/api/pc_turn'
    let params = {
      'color': color,
      'board': JSON.stringify(infoBoard)
    }
    $.ajax(
      url, {data: params}
    ).done(function(data){
      data = JSON.parse(data)
      updateBoard(data['board'], data['legal'])
      infoNextTurn = data['next_color']
      if (infoNextTurn==0){
        isGameOver = true
      }
      startTurn(infoNextTurn)
    })
  }

  function updateBoard(board, legal){
    infoBoard = board
    let tds = $('#board tr td')
    tds.removeClass('blank').removeClass('black').removeClass('white').removeClass('legal')

    let black_count = 0, white_count = 0
    for (let i = 0; i < 8; i++){
      black_count += (board[i].filter(tmp => tmp=='1')).length
      white_count += (board[i].filter(tmp => tmp=='2')).length
      for (let j = 0; j < 8; j++){
        let n = 63 - (i * 8 + j)
        let td = $('#board [data-position="' + n + '"]')
        let color = board[i][j]
        let color_str = {'0': 'blank', '1': 'black', '2': 'white'}[color]
        td.addClass(color_str)
        if (legal[i][j]=='1'){
          td.addClass('legal')
        }
      }
    }
    let message1 = '黒:' + black_count + ' | 白:' + white_count
    $('p#message1').text(message1)
  }

  startTurn(infoNextTurn)
});
