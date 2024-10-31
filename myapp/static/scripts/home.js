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
                // Si la subida fue exitosa, agrega la nueva fila a la tabla sin recargar la página
                const tableBody = document.querySelector("table tbody");
                const newRow = document.createElement("tr");

                newRow.innerHTML = `
                    <td>${data.fecha}</td>
                    <td><img src="${data.imagen}" alt="Radiografía" style="max-width: 100px;" /></td>
                    <td>${data.deteccion}</td>
                    <td><a href="/ver_heatmap/${pacienteId}/${data.radiografia_id}" class="btn-details">Detalles</a></td>
                `;

                tableBody.appendChild(newRow);

                // Buscar y eliminar la fila con el mensaje "No se registraron radiografías"
                const noRecordsMessage = document.querySelector("table tbody tr td[colspan='4']");
                if (noRecordsMessage) {
                    noRecordsMessage.parentElement.remove();  // Elimina la fila completa
                }
            } else {
                alert("Hubo un problema al subir la radiografía.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un error al subir la radiografía.");
        });
    });
});