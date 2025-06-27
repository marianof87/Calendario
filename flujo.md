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

✅ Fase 4: Gestión de eventos
COMPLETADA - Sistema completo de gestión de eventos implementado:

**Funcionalidades implementadas:**

- ✅ Agregar evento: Ventana modal con formulario completo (título, fecha, hora, descripción)
- ✅ Ver eventos del día: Click en día abre ventana con lista de eventos
- ✅ Eliminar evento: Menú contextual y confirmación de eliminación
- ✅ Editar evento: Doble-click para editar eventos existentes
- ✅ Listar eventos del mes: Botón "📅 Mes" muestra todos los eventos del mes
- ✅ Buscar evento por nombre: Ventana de búsqueda con filtrado en tiempo real
- ✅ Ver calendario en formato mensual: Indicadores visuales de días con eventos
- ✅ Notificación de eventos próximos: Sistema de notificaciones al inicio
- ✅ Evitar conflictos de horario: Validación y alertas de conflictos
- ✅ Guardar eventos entre sesiones: Persistencia en data/eventos.json

**Módulos agregados:**

- evento_dialogs.py: Ventanas modales para CRUD de eventos (645 líneas)
- notificaciones.py: Sistema de notificaciones y validaciones (509 líneas)
- Integración completa con calendario_ui.py (691 líneas actualizada)

**Características técnicas:**

- Sistema de validaciones robusto (fechas, horas, conflictos)
- Indicadores visuales: días con eventos en rojo + contador "(N)"
- Menús contextuales con clic derecho
- Notificaciones de eventos próximos (24h y 1h)
- Tooltips informativos en días con eventos
- Búsqueda instantánea por título de evento
- Confirmaciones de eliminación
- Manejo profesional de errores

⏳ Fase 5: Refinamiento visual
Estilos personalizados (Bootstyle: primary, info, success, etc.)

Iconos o colores para días actuales y días con eventos.

Oscurecer días que no pertenecen al mes actual.

PRÓXIMAS MEJORAS PLANIFICADAS:

- Refinamiento visual avanzado
- Temas personalizados adicionales
- Configuración de recordatorios personalizados
- Exportación/importación de eventos (CSV, iCal)
- Estadísticas y reportes de eventos
- Integración con calendarios externos
- Modo vista semanal y anual
