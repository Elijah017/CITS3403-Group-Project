$(function() {
    mod_board_height()

    $(window).change(mod_board_height)
});

function mod_board_height() {
    let offset = $('#boards-list').offset().top;
    $('#boards-list').css('height', `calc(100% - ${offset}px - 2rem)`);
}