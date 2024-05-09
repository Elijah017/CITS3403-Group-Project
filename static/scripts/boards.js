$(function() {
    mod_board_height();

    $(window).change(mod_board_height);

    $("tbody tr").each(function() {
        $(this).click(function(event) {
            if (event.target.id === "") {
                window.location.href = $(this).attr('href');
            }
        });
    });

    $(".dropdown-item").each(function() {
        $(this).change(function(e) { console.log($(this)); $(this).stopImmediatePropagation(); });
    });
});

function mod_board_height() {
    let offset = $('#boards-list').offset().top;
    $('#boards-list').css('height', `calc(100% - ${offset}px - 2rem)`);
}

function change_board_state(uri, id) {
    row = `#board${id}-row`;
    col = $(`${row} .board-state-col`).text()
    if ( col === "Active") {
        $.ajax({
            url: `${uri}`,
            method: 'PATCH',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                delete: true
            }),
        });
    } else {
        $.ajax({
            url: `${uri}`,
            method: 'PATCH',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                delete: false
            }),
        });
    }
    location.reload();
}