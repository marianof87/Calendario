✅ Fase 1: Interfaz base con ttkbootstrap
Crear ventana principal (Window).

Agregar un contenedor para mostrar el mes actual en formato de grilla.

Usar componentes ttkbootstrap.Label, Button, Frame.

✅ Fase 2: Navegación
Agregar botones tipo <<, <, Hoy, >, >> para moverse por meses y años.

Usar datetime para calcular el mes a mostrar.

✅ Fase 3: Visualización de días
Crear un grid de 7x6 que represente el mes (con calendar.monthcalendar).

Cada celda debe tener:

Número del día

Color diferente si hay eventos (usando estilos ttkbootstrap)

Posibilidad de hacer clic

✅ EXTRA: Selector de temas dinámico
Implementar combobox con 20+ temas de ttkbootstrap organizados por categorías (claro/oscuro).

Cambio de tema en tiempo real sin reiniciar la aplicación.

Título dinámico que muestra el tema actual.

✅ REFACTORIZACIÓN: Separación de responsabilidades
Dividir el código monolítico en módulos especializados:

- main.py: Solo punto de entrada de la aplicación
- calendario_ui.py: Interfaz gráfica y widgets
- calendario_logic.py: Lógica de navegación y generación del calendario
- theme_manager.py: Gestión completa de temas
- helpers.py: Funciones de utilidad para fechas
- eventos.py: Sistema de gestión de eventos (preparado para Fase 4)
- data/eventos.json: Almacenamiento persistente de datos

Aplicación de principios SOLID y buenas prácticas de desarrollo.

Documentación completa con docstrings en español.

Type hints para mejor mantenibilidad del código.

⏳ Fase 4: Gestión de eventos
Al hacer clic en un día, abrir una nueva ventana (modal) para:

Ver eventos

Agregar uno nuevo (con título y descripción)

Borrar eventos existentes

Guardar los eventos en archivo .json en data/eventos.json

⏳ Fase 5: Refinamiento visual
Estilos personalizados (Bootstyle: primary, info, success, etc.)

Iconos o colores para días actuales y días con eventos.

Oscurecer días que no pertenecen al mes actual.

PRÓXIMAS MEJORAS PLANIFICADAS:

- Integración del sistema de eventos con la UI
- Ventanas modales para gestión de eventos por día
- Indicadores visuales de días con eventos
- Búsqueda y filtrado de eventos
- Notificaciones de eventos próximos
- Exportación/importación de eventos
- Configuración de recordatorios
