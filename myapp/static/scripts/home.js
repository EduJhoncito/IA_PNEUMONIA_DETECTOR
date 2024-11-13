document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById("file-input");
    const addRadiographButton = document.getElementById("add-radiograhp-btn");

    addRadiographButton.addEventListener("click", function() {
        fileInput.click();  // Simula un clic para abrir el selector de archivos
    });

    fileInput.addEventListener("change", function() {
        const formData = new FormData();
        formData.append('radiograph_image', fileInput.files[0]);

        // Aquí obtén el token CSRF y el ID del paciente
        formData.append('csrfmiddlewaretoken', csrftoken);

        fetch(`/agregar_radiografia/${pacienteId}`, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tableBody = document.querySelector("table tbody");

                // Crea una nueva fila con los datos de la radiografía
                const newRow = document.createElement("tr");
                newRow.innerHTML = `
                    <td>${data.fecha}</td>
                    <td><img src="${data.imagen}" alt="Radiografía" style="max-width: 100px;" /></td>
                    <td>${data.deteccion}</td>
                    <td><a href="/ver_heatmap/${pacienteId}/${data.radiografia_id}" class="btn-details">Ver</a></td>
                `;

                // Agrega la nueva fila a la tabla
                tableBody.appendChild(newRow);

                // Elimina la fila de "No se registraron radiografías" si existe
                const noRecordsMessage = document.querySelector("table tbody tr td[colspan='4']");
                if (noRecordsMessage) {
                    noRecordsMessage.parentElement.remove();
                }
            } else {
                // Si no es un éxito, muestra el mensaje que venga del backend
                alert(data.mensaje || "Hubo un problema al subir la radiografía.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un error al subir la radiografía.");
        });
    });
});
