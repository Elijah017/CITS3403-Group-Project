let global = this;
let map = [];

$(function() {
    mod_board_height();

    $(".search-bar").on("input", search_for_board);

    $(window).change(mod_board_height);

    $("tbody tr").each(function() {
        map.push({ name: $(this).find('.boardname-col').text(), id: `#${$(this).attr('id')}` });
        $(this).click(function(event) {
            if (event.target.id === "") {
                window.location.href = $(this).attr('href');
            }
        });
    });

    $(".dropdown-item").each(function() {
        if ($(this).has("#disp-inact").length === 1) {
            $(this).click(handle_inactive_filter);
        }
        else if ($(this).has('#disp-mine').length === 1) {
            $(this).click(handle_my_boards);
        }
        else if ($(this).has('#disp-others').length === 1) {
            $(this).click(handle_other_boards);
        }
    });
});

function mod_board_height() {
    let list_offset = $('#boards-list').offset().top;
    let table_offset = $('.boards-table').offset().top;
    $('#boards-list').css('height', `calc(100% - ${list_offset}px - 2rem)`);
    $('.boards-table tbody').css('height', `calc(${table_offset}px + 33rem)`);
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
            if (!$("#disp-inact").is(":checked")) { $(row).hide(); }
        },
    });
}

function handle_other_boards(event) {
    handle_checkbox(event, '#disp-others');
    console.log("clicked other boards");
}

function handle_my_boards(event) {
    handle_checkbox(event, '#disp-mine');
    console.log('clicked my boards');
}

function handle_inactive_filter(event) {
    handle_checkbox(event, '#disp-inact');
    for (let row in map) {
        row = map[row]
        if (!$("#disp-inact").is(":checked")) { $(row.id).hide(); }
        else { try_show_row(map[row]); }
    }
    console.log("clicked");
}

function handle_checkbox(event, check_id) {
    if (event.target.id === "") { event.preventDefault(); }
    let checkbox = $(check_id);
    let checked;
    let target_class = $(event.target).attr('class');
    if (target_class !== "form-check-input") {
        checked = !checkbox.is(":checked");
    } else {
        checked = checkbox.is(":checked");
    }
    checkbox.prop('checked', checked);
}

function search_for_board() {
    const search_string = $(".search-bar").val().toString();
    const length = search_string.length;

    for (let row in map) {
        row = map[row];
        let comp_str;
        const name_len = row.name.length;

        if (length < name_len) {
            comp_str = row.name.slice(0, length);
        }
        else if (name_len === length) { comp_str = row.name; }
        else { comp_str = ""; }

        if (comp_str.toLowerCase() === search_string.toLowerCase()) { try_show_row(row); }
        else { $(row.id).hide(); }
    }
}

function try_show_row(row) {
    let jqRow = $(row.id);
    if (!jqRow.is(":hidden")) { return; }

    // get the state of the row
    let active = jqRow.find(".board-state-col").text();
    let owner = jqRow.find(".board-owner-col").text();

    // get the state of the filters
    let factive = !$("#disp-inact").is(":checked");
    let fmine = $("#disp-mine").is(":checked");
    let fothers = $("#disp-others").is(":checked");

    let valid = 0;
    if (owner === "Me" && fmine) { valid = valid | 0b1; }
    else if (owner !== "Me" && fothers) { valid = valid | 0b1; }
    if (active === "Active" && factive) { valid = valid | 0b10; }
    else if (active === "Inactive" && !factive) { valid = valid | 0b10; }

    if (valid === 0b11) { jqRow.css('display', 'table'); }
}