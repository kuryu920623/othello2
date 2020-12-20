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

window.addEventListener('DOMContentLoaded', function(event){

  function manualTurn(){
    let blanks = $('#board tr td.blank')
    blanks.on('click', function(event){
      let position = $(event.target).data('position')
      let url = location.origin + '/othello2/api/manual_turn'
      let params = {
        'position': position,
        'color': infoNextTurn,
        'board': JSON.stringify(infoBoard)
      }
      $.ajax(
        url, {data: params}
      ).done(function(data)
        {
          data = JSON.parse(data)
          updateBoard(JSON.parse(data['board']))
          infoNextTurn = data['next_color']
        }
      )
    })
  }
  function pcTurn(){

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

  manualTurn()
});
