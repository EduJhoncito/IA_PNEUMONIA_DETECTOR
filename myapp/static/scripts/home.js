document.addEventListener('DOMContentLoaded', function() {
    const addRadiographBtn = document.getElementById('add-radiograhp-btn');
    const fileInput = document.getElementById('file-input');

    addRadiographBtn.addEventListener('click', function(event) {
        event.preventDefault();
        fileInput.click(); // Abre el explorador de archivos
    });

    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('radiograph_image', file);

            fetch(`/agregar_radiografia/${pacienteId}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}' // Incluye el token CSRF
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Agrega la nueva fila en la tabla automáticamente con la información de la radiografía
                    const newRow = `
                        <tr>
                            <td>${data.fecha}</td>
                            <td><img src="data:image/png;base64, ${data.imagen}" width="50" /></td>
                            <td>${data.deteccion}</td>
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
});
