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
          updateBoard(data['board'])
          updateLegal(data['legal'])
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
      updateBoard(data['board'])
      updateLegal(data['legal'])
      infoNextTurn = data['next_color']
      if (infoNextTurn==0){
        isGameOver = true
      }
      startTurn(infoNextTurn)
    })
  }

  function updateBoard(board){
    infoBoard = board
    let tds = $('#board tr td')
    tds.removeClass('blank').removeClass('black').removeClass('white')
    let n = 63
    for (let row of board){
      for (let color of row){
        let selector = '#board [data-position="' + n + '"]'
        let td = $(selector)
        let color_str = {'0': 'blank', '1': 'black', '2': 'white'}[color]
        td.addClass(color_str)
        n -= 1
      }
    }
  }

  function updateLegal(legal){
    let tds = $('#board tr td')
    tds.removeClass('legal')
    let n = 63
    for (let row of legal){
      for (let color of row){
        if (color=='1'){
          let selector = '#board [data-position="' + n + '"]'
          let td = $(selector)
          td.addClass('legal')
        }
        n -= 1
      }
    }
  }

  startTurn(infoNextTurn)
});
