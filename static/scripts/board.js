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

$(function() {
   console.log('test');
});
