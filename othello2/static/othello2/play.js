window.addEventListener('DOMContentLoaded', function(event){
    blanks = $('#board tr td.blank')
    blanks.on('click', function(event){
        position = $(event.target).data('position')
        $.ajax(
            location.domain,
            {
                position: position
            }
        ).done(
            console.log()
        )
    })
});
