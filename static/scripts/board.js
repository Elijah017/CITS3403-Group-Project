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

const types = {
  0: "TASK",
  1: "BUG",
  2: "STORY"
};

const priorities = {
  0: "LOW",
  1: "MEDIUM",
  2: "HIGH"
};

const statuses = {
  0: "ON HOLD",
  1: "TO DO",
  2: "IN PROGRESS",
  3: "TESTING",
  4: "READY FOR QA",
  5: "DONE"
}

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

function getTicketHistory(ticketId, callback_fn) {
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = (e) => {
    if (e.target.readyState == 4 && e.target.status == 200) {
      callback_fn(JSON.parse(e.target.responseText));
    }
  }
  xhttp.open("GET", document.URL + "/history/" + ticketId, true);
  xhttp.send();
}

function addHistoryRecord(record) {
  let recordDiv = document.createElement("div");
  recordDiv.classList.add("history-record");
  let dt = new Date(record.timestamp);
  let dtOptions = { year: 'numeric', month: 'long', day: 'numeric' };
  recordDiv.innerHTML = `
    <span class="history-username">${record.user}</span>
    <span class="history-timestamp">${dt.toLocaleString("en-GB", dtOptions)} at ${dt.toLocaleTimeString()}</span>
  `;

  if (record.type != null) {
    recordDiv.innerHTML += `<br><i>• Changed type to ${types[record.type]}</i>`;
  }
  if (record.priority != null) {
    recordDiv.innerHTML += `<br><i>• Changed priority to ${priorities[record.priority]}</i>`;
  }
  if (record.status != null) {
    recordDiv.innerHTML += `<br><i>• Changed status to ${statuses[record.status]}</i>`;
  }
  if (record.comment != null) {
    console.log(record)
    recordDiv.innerHTML += "<br>" + record.comment;
  }
  if (record.type == null & record.priority == null & record.status == null & record.comment == null) {
    recordDiv.innerHTML += `<br><i>Created ticket #${record.ticketId}</i>`;
  }
  
  document.getElementById("ticketHistory").appendChild(recordDiv);
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
  newTicketElement.innerHTML = `
    <p>
      <span class="type-icon">${typeIcons[type]}</span>
      <span class="ticket-id"> #${ticketId}</span>
      <span class="priority-icon">${priorityIcons[priority]}</span>
      <br>
      ${title}   
    </p>`
  $(".task-col .col-body")[status].appendChild(newTicketElement);

  newTicketElement.onclick = async () => {
    let form = document.getElementById("viewTicketForm");
    $("#viewTicketModalLabel").html(`#<span id="ticketId">${ticketId}</span> ${title}`);
    $("div#ticketDescription").text(description);
    form.ticketType.selectedIndex = type;
    form.ticketPriority.selectedIndex = priority;
    form.ticketStatus.selectedIndex = status;
    getTicketHistory(ticketId, (history) => {
        for (let record of history) {
          addHistoryRecord(record);
        }
    })
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
        addTicket(ticketId, data.title, data.status, data.priority, data.type, data.description);
      }
    }
    xhttp.open("POST", document.URL + "/tickets", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })

  $("#viewTicketModal").on("hidden.bs.modal", (e) => {
    document.getElementById("viewTicketForm").reset();
    document.getElementById("ticketHistory").innerHTML = "";
  });

  $("#viewTicketModal").on("submit", (e) => {
    e.preventDefault();
    let data = {
      ticketId: parseInt($("#viewTicketModal #ticketId").text()),
      type: parseInt(e.target.ticketType.value),
      priority: parseInt(e.target.ticketPriority.value),
      status: parseInt(e.target.ticketStatus.value),
      comment: e.target.ticketComment.value == "" ? null : e.target.ticketComment.value
    };

    e.target.ticketComment.value = "";

    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = (e) => {
      if (e.target.readyState == 4 && e.target.status == 202) {
        $(`#${data.ticketId}.task span.type-icon`).html(typeIcons[data.type]);
        $(`#${data.ticketId}.task span.priority-icon`).html(priorityIcons[data.priority]);
        document.getElementsByClassName("task-col")[data.status]
          .getElementsByClassName("col-body")[0]
          .appendChild(document.getElementById(data.ticketId));
      }
    }
    xhttp.open("PATCH", document.URL + "/tickets", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })
});
