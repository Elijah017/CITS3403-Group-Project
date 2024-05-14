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

function addTicket(ticketId, title, status) {
  let newTicketElement = document.createElement("div");
  newTicketElement.id = ticketId;
  newTicketElement.classList.add("task");
  newTicketElement.setAttribute("draggable", true);
  newTicketElement.setAttribute("ondragstart", "dragTask(event)");
  newTicketElement.setAttribute("draggable", true);
  newTicketElement.innerHTML = `<span class="task-id">#${ticketId}</span><br>${title}`
  $(".task-col .col-body")[status].appendChild(newTicketElement);
}

$( document ).ready(() => {
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = (e) => {
    if (e.target.readyState == 4 && e.target.status == 200) {
      let tickets = JSON.parse(e.target.responseText);
      for (let ticket of tickets) {
        addTicket(ticket.ticketId, ticket.title, ticket.status);
      }
    }
  }
  xhttp.open("GET", document.URL + "/tickets", true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send();

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
    xhttp.onreadystatechange = (e) => {
      if (e.target.readyState == 4 && e.target.status == 201) {
        ticketId = JSON.parse(e.target.responseText).ticketId;
        addTicket(ticketId, data.title, data.status);
      }
    }
    xhttp.open("POST", document.URL + "/tickets", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })
});
