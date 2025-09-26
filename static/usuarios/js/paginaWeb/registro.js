/*VALIDACION EN TIEMPO REAL DE LA CONTRASEÑA*/
const input = document.getElementById("id_contrasena");
if (input) {
  input.addEventListener("input", () => {
    const val = input.value;
    const longitud = document.getElementById("requisito-longitud");
    const mayuscula = document.getElementById("requisito-mayuscula");
    const minuscula = document.getElementById("requisito-minuscula");
    const numero = document.getElementById("requisito-numero");
    const especial = document.getElementById("requisito-especial");

    longitud.className = val.length >= 8 ? "valido" : "invalido";
    mayuscula.className = /[A-Z]/.test(val) ? "valido" : "invalido";
    minuscula.className = /[a-z]/.test(val) ? "valido" : "invalido";
    numero.className = /\d/.test(val) ? "valido" : "invalido";
    especial.className = /[!@#$%^&*(),.?":{}|<>]/.test(val)
      ? "valido"
      : "invalido";
  });
}

/**/
