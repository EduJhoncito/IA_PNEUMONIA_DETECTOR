// Obtener el modal
var modal = document.getElementById("add-patient-modal");

// Obtener el botón que abre el modal
var btn = document.getElementById("add-patient-btn");

// Obtener el <span> que cierra el modal
var span = document.getElementsByClassName("close")[0];

// Cuando el usuario hace clic en el botón, abre el modal
btn.onclick = function() {
	modal.style.display = "block";
}

// Cuando el usuario hace clic en <span> (x), cierra el modal
span.onclick = function() {
	modal.style.display = "none";
}

// Cuando el usuario hace clic fuera del modal, también lo cierra
window.onclick = function(event) {
	if (event.target == modal) {
		modal.style.display = "none";
	}
}