const priorityIcons = {
  0: `<i class="bi bi-chevron-double-down priority" style="color: var(--bs-blue)"></i>`,
  1: `<i class="bi bi-dash priority" style="color: var(--bs-yellow)"></i>`,
  2: `<i class="bi bi-chevron-double-up priority" style="color: var(--bs-red)"></i>`
};

const typeIcons = {
  0: `<i class="bi bi-check task-icon" style="color: white"></i>`,
  1: `<i class="bi bi-bug-fill bug-icon" style="color: white; font-size: 0.6rem"></i>`,
  2: `<i class="bi bi-bookmark-fill story-icon" style="color: white; font-size: 0.6rem"></i>`
};

function dragOver(e) {
    e.preventDefault();
}
  
function dragTask(e) {
  e.dataTransfer.setData("text", e.target.id);
}

function dropTask(e) {
  e.preventDefault();
  let ticketId = e.dataTransfer.getData("text");
  let colBody = e.target.closest(".col-body");
  let newStatus = Array.prototype.indexOf.call(colBody.closest(".row").children, colBody.closest(".col"));

  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = (e) => {
    if (e.target.readyState == 4 && e.target.status == 202) {
      colBody.appendChild(document.getElementById(ticketId));
    }
  }
  xhttp.open("PATCH", document.URL + "/tickets", true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send(JSON.stringify({ticketId: ticketId, status: newStatus}));  
}

function addTicket(ticketId, title, status, priority, type, description) {
  let newTicketElement = document.createElement("div");
  newTicketElement.id = ticketId;
  newTicketElement.classList.add("task");
  newTicketElement.setAttribute("draggable", true);
  newTicketElement.setAttribute("ondragstart", "dragTask(event)");
  newTicketElement.setAttribute("draggable", true);
  newTicketElement.setAttribute("data-bs-toggle", "modal");
  newTicketElement.setAttribute("data-bs-target", "#viewTicketModal");
  newTicketElement.innerHTML = `<p>${typeIcons[type]}<span class="task-id"> #${ticketId}</span>${priorityIcons[priority]}</p>${title}`
  $(".task-col .col-body")[status].appendChild(newTicketElement);

  newTicketElement.onclick = () => {
    $("#viewTicketModalLabel").text(title);
    $("#ticket-description").text(description);
    document.getElementById("viewTicketForm").ticketType.selectedIndex = type;
    document.getElementById("viewTicketForm").ticketPriority.selectedIndex = priority;
    document.getElementById("viewTicketForm").ticketStatus.selectedIndex = status;
  }
}

$( document ).ready(() => {
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = (e) => {
    if (e.target.readyState == 4 && e.target.status == 200) {
      let tickets = JSON.parse(e.target.responseText);
      for (let ticket of tickets) {
        addTicket(ticket.ticketId, ticket.title, ticket.status, ticket.priority, ticket.type, ticket.description);
      }
    }
  }
  xhttp.open("GET", document.URL + "/tickets", true);
  xhttp.send();

  $("#newTicketModal").on("hidden.bs.modal", (e) => {
    document.getElementById("newTicketForm").reset();
  });

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
        addTicket(ticketId, data.title, data.status, data.priority, data.type);
      }
    }
    xhttp.open("POST", document.URL + "/tickets", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })

  $("#viewTicketModal").on("hidden.bs.modal", (e) => {
    document.getElementById("viewTicketForm").reset();
  });
});
