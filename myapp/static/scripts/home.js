document.addEventListener('DOMContentLoaded', function() {
    const addRadiographBtn = document.getElementById('add-radiograhp-btn');
    const fileInput = document.getElementById('file-input');

    // Verificamos si los elementos necesarios existen antes de añadir los eventos
    if (addRadiographBtn && fileInput) {
        // Al hacer clic en el botón "Agregar radiografía", abrimos el explorador de archivos
        addRadiographBtn.addEventListener('click', function(event) {
            event.preventDefault();
            fileInput.click();  // Esto debería abrir el explorador de archivos
        });

        // Cuando el archivo es seleccionado, se captura el evento "change"
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('radiograph_image', file);

                // Enviar el archivo a través de una solicitud POST a Django
                fetch(`/agregar_radiografia/${pacienteId}`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrftoken  // Aquí agregamos el token CSRF obtenido desde la plantilla
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remover la fila que contiene el mensaje "No hay radiografías para este paciente."
                        const emptyMessageRow = document.querySelector('tr td[colspan="3"]');
                        if (emptyMessageRow) {
                            emptyMessageRow.parentNode.removeChild(emptyMessageRow);
                        }

                        // Agregar la nueva fila a la tabla automáticamente con la información de la radiografía
                        const newRow = `
                            <tr>
                                <td>${data.fecha}</td>
                                <td><img src="data:image/png;base64,${data.imagen}" width="50" /></td>
                                <td>Pendiente</td>
                            </tr>
                        `;
                        document.querySelector('table tbody').innerHTML += newRow;
                    } else {
                        alert('Error al subir la radiografía');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Hubo un problema al subir la radiografía');
                });
            }
        });
    }
});
