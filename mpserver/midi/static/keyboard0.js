 
let Keyboard = window.SimpleKeyboard.default;

let myKeyboard = new Keyboard({
  onChange: input => onChange(input),
  onKeyPress: button => onKeyPress(button)
});


function onChange(input) {
  document.querySelector(".input").value = input;
  console.log("Input changed", input);
}


function onKeyPress(button) {
  console.log("Button pressed", button);
}
