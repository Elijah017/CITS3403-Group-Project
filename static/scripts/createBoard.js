$(function() {
    $("#create-board").submit((e) => {
        e.preventDefault();
        const vis = $("#visibility").find(":selected").text();
        const name = $("#boardname").val();
        const desc = $("#board-description").val();
        const path = $("#create-board").attr('path');

        $.ajax({
            url: path,
            method: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                visibility: vis,
                boardname: name,
                description: desc,
            }),
            statusCode: {
                200: function() {
                    window.location.href = '/boards/';
                } 
            }
        });
    })
})
