$(function() {
  $('#passwordHelper').hide();
  $('#confirmHelper').hide();

  $('#password').click(function() { $('#passwordHelper').show(500); });
  $('#confirm').click(function() { $('#confirmHelper').show(500); });

  $('#confirm').on('input', function() {
    let reqs = [
      $(this),
      [
        ['m', '#confirmMatch', `${$('#password').val()}`]
      ]
    ];
    
    requisites(reqs);
  });

  $('#password').on('input', function() {
    let reqs = [
      $(this),
      [
        ['l', '#passwordLength', 10],
        ['m', '#passwordSpecial', /[ `!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/],
        ['m', '#passwordUpper', /[A-Z]/],
        ['m', '#passwordLower', /[a-z]/],
        ['m', '#passwordNumber', /[0-9]/]
      ]
    ];

    requisites(reqs);
  });
});

/**
  * Loops through all the provided requisites and checks whether they are
  * valid or not. sets the colour of requisite helpers depending on their
  * completion status.
  *
  * The the internal requisites array holds 3 elements
  * - [0] = 'l' for length | 'm' for match
  * - [1] = id of helper string
  * - [2] = number if [0] was 'l' | regex if [0] was 'm'
  */
function requisites(reqs) {
  let input = reqs[0].val()

  for (let req of reqs[1]) {
    let valid;

    switch (req[0]) {
      case 'l':
        valid = input.length >= req[2];
        break;
      case 'm':
        valid = !(input.match(req[2]) === null)
        break;
    }

    if (valid) {
      $(req[1]).attr('class', 'text-success');
    } else {
      $(req[1]).attr('class', 'text-danger');
    }
  }
}
