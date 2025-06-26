document.addEventListener('DOMContentLoaded', function() {

    // =================================================================
    // INICIALIZACIÓN GLOBAL (Se ejecuta en todas las páginas)
    // =================================================================

    // 1. Animate On Scroll (AOS)
    AOS.init({
        duration: 800,
        once: true,
    });

    // 2. Lógica del Loader de Página
    const pageLoader = document.getElementById('page-loader');
    if (pageLoader) {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                pageLoader.style.display = 'flex';
            });
        });
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                pageLoader.style.display = 'none';
            }
        });
    }

    // =================================================================
    // LÓGICA ESPECÍFICA DEL PANEL DE ADMINISTRACIÓN
    // =================================================================
    
    // Solo se ejecuta si encuentra el contenedor de los gráficos
    if (document.getElementById('dashboard-charts')) {
        fetch('/api/chart-data/')
            .then(response => response.json())
            .then(data => {
                // Gráfico de Reservas Mensuales
                const reservasCtx = document.getElementById('reservasMensualesChart').getContext('2d');
                new Chart(reservasCtx, {
                    type: 'bar',
                    data: {
                        labels: data.reservasMensuales.labels,
                        datasets: [{
                            label: 'Reservas por Mes',
                            data: data.reservasMensuales.data,
                            backgroundColor: 'rgba(230, 195, 138, 0.6)',
                            borderColor: 'rgba(230, 195, 138, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: { y: { beginAtZero: true } },
                        plugins: { legend: { labels: { color: 'white' } } },
                    }
                });

                // Gráfico de Servicios Populares
                const serviciosCtx = document.getElementById('serviciosPopularesChart').getContext('2d');
                new Chart(serviciosCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.serviciosPopulares.labels,
                        datasets: [{
                            data: data.serviciosPopulares.data,
                            backgroundColor: ['#e6c38a', '#D988B9', '#B0578D', '#a88fac', '#6f42c1'],
                            borderColor: 'var(--color-bg-secondary)',
                        }]
                    },
                    options: {
                        plugins: { legend: { labels: { color: 'white' } } },
                    }
                });
            });
    }

    // =================================================================
    // LÓGICA ESPECÍFICA DE LA PÁGINA DE RESERVA
    // =================================================================

    // Solo se ejecuta si encuentra el formulario de reserva
    if (document.getElementById('reserva-form')) {
        
        // 1. Obtener todos los elementos del DOM una sola vez
        const step2 = document.getElementById('step-2-time');
        const step3 = document.getElementById('step-3-confirm');
        const horariosContainer = document.getElementById('horarios-disponibles');
        const horariosWrapper = document.getElementById('horarios-container-wrapper');
        const horariosSpinner = document.getElementById('horarios-spinner');
        const sinHorariosMsg = document.getElementById('sin-horarios-msg');
        const fechaInput = document.getElementById('fecha-input');
        const submitButton = document.getElementById('submit-button');

        // 2. Estado inicial de la página
        step2.style.display = 'none';
        step3.style.display = 'none';

        // 3. Inicializar el calendario (Flatpickr)
        flatpickr(document.getElementById('calendario'), {
            inline: true,
            dateFormat: "Y-m-d",
            minDate: "today",
            locale: "es",
            onChange: function(selectedDates, dateStr) {
                if (dateStr) {
                    // Resetea y prepara la UI para mostrar los horarios
                    step2.style.display = 'block';
                    step3.style.display = 'none';
                    submitButton.disabled = true;
                    horariosWrapper.style.display = 'none';
                    
                    updateHorarios(dateStr); // Llama a la función para buscar horarios
                    fechaInput.value = dateStr;
                }
            }
        });

        // 4. Event listener para cuando se selecciona una hora
        horariosContainer.addEventListener('change', function(e) {
            if (e.target.name === 'hora') {
                step3.style.display = 'block';
                submitButton.disabled = false;
            }
        });

        // 5. Función que se comunica con Django para obtener los horarios
        function updateHorarios(fecha) {
            horariosContainer.innerHTML = '';
            horariosSpinner.style.display = 'block';
            sinHorariosMsg.style.display = 'none';
            
            // Usa la variable global 'djangoData' que definimos en las plantillas
            fetch(`${djangoData.getHorariosUrl}?fecha=${fecha}`)
                .then(response => response.json())
                .then(data => {
                    horariosSpinner.style.display = 'none';
                    horariosWrapper.style.display = 'block';
                    
                    if (data.horarios && data.horarios.length > 0) {
                        data.horarios.forEach(horario => { // "horario" es un objeto {value, display}
                            const radioLabel = document.createElement('label');
                            radioLabel.className = 'btn btn-outline-primary';
                            
                            const radioInput = document.createElement('input');
                            radioInput.type = 'radio';
                            radioInput.name = 'hora';
                            radioInput.value = horario.value; // El valor real (ej: 10:00)
                            radioInput.className = 'btn-check';
                            radioInput.id = `hora-${horario.value.replace(':', '')}`;
                            radioInput.required = true;

                            radioLabel.appendChild(radioInput);
                            radioLabel.append(horario.display); // El texto visible (ej: 10:00 - 11:00)
                            horariosContainer.appendChild(radioLabel);
                        });
                    } else {
                        sinHorariosMsg.style.display = 'block';
                    }
                });
        }
    }
});