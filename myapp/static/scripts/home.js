document.getElementById('add-radiograhp-btn').addEventListener('click', function () {
    document.getElementById('file-input').click();  // Abre el cuadro de diálogo de archivo
});

document.getElementById('file-input').addEventListener('change', function () {
    const formData = new FormData();
    formData.append('radiograph_image', this.files[0]);

    // Añadir el token CSRF
    formData.append('csrfmiddlewaretoken', csrftoken);

    // Realiza la petición AJAX para enviar el archivo
    fetch(`/agregar_radiografia/${pacienteId}`, {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Elimina el mensaje "No se registraron radiografías" si existe
            const noRadiographsRow = document.querySelector('.container-table tbody tr td[colspan="3"]');
            if (noRadiographsRow) {
                noRadiographsRow.parentNode.remove();  // Remueve la fila que dice "No se registraron radiografías"
            }

            // Crear una nueva fila con la información de la radiografía
            const newRow = document.createElement('tr');

            // Columna de la fecha
            const dateCell = document.createElement('td');
            dateCell.textContent = data.fecha;
            newRow.appendChild(dateCell);

            // Columna de la imagen de la radiografía
            const imageCell = document.createElement('td');
            const imgElement = document.createElement('img');
            imgElement.src = data.imagen;  // URL de la imagen recién subida
            imgElement.style.maxWidth = '100px';
            imageCell.appendChild(imgElement);
            newRow.appendChild(imageCell);

            // Columna de la detección
            const detectionCell = document.createElement('td');
            detectionCell.textContent = data.deteccion;
            newRow.appendChild(detectionCell);

            // Columna del botón "Detalles"
            const detailsCell = document.createElement('td');
            const detailsButton = document.createElement('a');
            detailsButton.textContent = 'Detalles';
            detailsButton.href = `/ver_heatmap/${pacienteId}/${data.radiografia_id}`;
            detailsButton.className = 'btn-details';
            detailsCell.appendChild(detailsButton);
            newRow.appendChild(detailsCell);

            // Añadir la nueva fila a la tabla
            document.querySelector('.container-table tbody').appendChild(newRow);

            alert('Radiografía subida con éxito');
        } else {
            alert('Hubo un problema al subir la radiografía');
        }
    })
    .catch(error => {
        console.error('Error al subir la radiografía:', error);
        alert('Ocurrió un problema al subir la radiografía.');
    });
});