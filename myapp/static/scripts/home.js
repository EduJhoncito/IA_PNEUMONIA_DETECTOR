document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById("file-input");
    const addRadiographButton = document.getElementById("add-radiograhp-btn");

    addRadiographButton.addEventListener("click", function() {
        fileInput.click();  // Simula un clic para abrir el selector de archivos
    });

    fileInput.addEventListener("change", function() {
        const formData = new FormData();
        formData.append('radiograph_image', fileInput.files[0]);
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

                tableBody.appendChild(newRow);

                const noRecordsMessage = document.querySelector("table tbody tr td[colspan='4']");
                if (noRecordsMessage) {
                    noRecordsMessage.parentElement.remove();
                }
            } else {
                // Mostrar mensaje en caso de error
                alert(data.mensaje || "Hubo un problema al subir la radiografía.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un error al subir la radiografía.");
        });
    });
});