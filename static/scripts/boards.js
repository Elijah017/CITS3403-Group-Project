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
        if ($(this).has("#disp-inact").length === 1) {
            t = $(this)
            $(this).click(handle_inactive_filter);
        }
    });
});

function mod_board_height() {
    let offset = $('#boards-list').offset().top;
    $('#boards-list').css('height', `calc(100% - ${offset}px - 2rem)`);
}

function change_board_state(uri, id) {
    row = `#board${id}-row`;
    $.ajax({
        url: `${uri}`,
        method: 'PATCH',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({
            delete: $(`${row} .board-state-col`).text() === "Active"
        }),
        success: function() {
            location.reload();
        },
    });
}

function handle_inactive_filter(e) {
    if (e.target.id === "") { e.preventDefault(); }
    checkbox = $("#disp-inact");
    checked = !checkbox.is(":checked");
    checkbox.prop('checked', checked);
}