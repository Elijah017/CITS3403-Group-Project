$(function() {
    mod_board_heigth()

    $(window).change(mod_board_heigth)
});

function mod_board_heigth() {
    let offset = $('#boards-list').offset().top;
    $('#boards-list').css('height', `calc(100% - ${offset}px - 2rem)`);
}