$(function() {
    mod_board_height()

    $(window).change(mod_board_height)

    $("tbody tr").each(function() {
        $(this).click(function() {
            window.location.href = $(this).attr('href');
        })
    })
});

function mod_board_height() {
    let offset = $('#boards-list').offset().top;
    $('#boards-list').css('height', `calc(100% - ${offset}px - 2rem)`);
}