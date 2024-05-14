function dragOver(e) {
    e.preventDefault();
  }
  
  function dragTask(e) {
    e.dataTransfer.setData("text", e.target.id);
  }
  
  function dropTask(e) {
    e.preventDefault();
    var data = e.dataTransfer.getData("text");
    e.target.closest(".col-body").appendChild(document.getElementById(data));
  }

$( document ).ready(() => {
  $("#newTicketModal").on("submit", (e) => {
    e.preventDefault();
    let data = {
      type: parseInt(e.target.ticketType.value),
      title: e.target.ticketTitle.value,
      priority: parseInt(e.target.ticketPriority.value),
      status: parseInt(e.target.ticketStatus.value),
      description: e.target.ticketDescription.value 
    };

    $("#newTicketModal [data-bs-dismiss='modal']").click();
    e.target.reset();

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", document.URL, false);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })
});
