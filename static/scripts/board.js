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
    xhttp.onreadystatechange = (e) => {
      if (e.target.readyState == 4 && e.target.status == 201) {
        ticketId = JSON.parse(e.target.responseText).ticketId;
        let newTicketElement = document.createElement("div");
        newTicketElement.id = ticketId;
        newTicketElement.classList.add("task");
        newTicketElement.setAttribute("draggable", true);
        newTicketElement.setAttribute("ondragstart", "dragTask(event)");
        newTicketElement.setAttribute("draggable", true);
        newTicketElement.innerHTML = `<span class="task-id">#${ticketId}</span><br>${data.title}`
        $(".task-col .col-body")[data.status].appendChild(newTicketElement);
      }
    }
    xhttp.open("POST", document.URL, true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(data));
  })
});
