Sistema de Calendario en Python

- Integrantes del equipo:
  Mariano Capella
  gabriel Osemberg

- Libreria Python utilizada:
  ttkbootstrap
  https://github.com/israel-dryer/ttkbootstrap
  pip install ttkbootstrap

  ESTRUCTURA DEL SISTEMA

  /calendario_app
  ├── main.py # archivo principal que inicia la app
  ├── calendario.py # lógica para generar vista mensual/semanal
  ├── eventos.py # manejo de eventos (añadir, eliminar, cargar)
  ├── helpers.py # funciones de ayuda (formato de fecha, etc.)
  ├── data/
  │ └── eventos.json # almacenamiento de eventos

- Historias de Usuario y Cretirios de aceptacion:
- 1. Agregar evento
     Historia:
     Como usuario del calendario, quiero poder agregar un evento con una fecha y hora específicas, para recordar compromisos importantes.

Criterios de aceptación:

El sistema debe solicitar al usuario los siguientes datos:

Título del evento (obligatorio)

Fecha (en formato válido, por ejemplo: YYYY-MM-DD)

Hora (opcional; en formato HH:MM de 24 horas)

Descripción (opcional)

Si la fecha ingresada no es válida, el sistema debe mostrar un mensaje de error claro.

Si el título está vacío, debe impedir la creación y mostrar un mensaje de error.

Una vez validado, el evento debe guardarse correctamente y confirmarse con un mensaje tipo:
"Evento 'Reunión' creado para el 2025-07-01 a las 14:00."

El evento debe persistir si el sistema se cierra y se vuelve a abrir (guardado en archivo o base de datos)

- 2. Ver eventos del día
     Como usuario del calendario, quiero poder ver todos los eventos programados para un día específico, para planificar mi jornada eficientemente.

Criterios de aceptación:

El sistema debe solicitar al usuario una fecha válida.

Si no hay eventos para esa fecha, debe indicar: "No hay eventos para esta fecha."

Si hay eventos:

Mostrar título, hora (si aplica) y descripción para cada evento.

Ordenarlos cronológicamente por hora.

Si el usuario ingresa una fecha inválida, debe mostrar un mensaje de error y permitir volver a intentarlo

- 3. Eliminar evento
     Como usuario del calendario, quiero poder eliminar un evento previamente creado, para mantener actualizado mi calendario si hay cambios.

Criterios de aceptación:

El sistema debe permitir al usuario seleccionar un evento por fecha y título (o ID si se usa).

Debe mostrar un resumen del evento antes de confirmar su eliminación.

Requiere una confirmación del usuario:
"¿Está seguro que desea eliminar este evento? (S/N)"

Si se confirma, el evento debe eliminarse y mostrar un mensaje: "Evento eliminado exitosamente."

Si no se encuentra el evento, debe mostrarse un mensaje claro: "Evento no encontrado."

- 4. Editar evento
     Como usuario del calendario, quiero poder modificar la información de un evento existente, para corregir errores o cambiar detalles como la hora o el nombre.

Criterios de aceptación:

El sistema debe listar eventos por fecha o permitir búsqueda por nombre.

Una vez seleccionado, debe mostrar los detalles actuales del evento.

El usuario puede editar uno o varios de los siguientes campos:

Título

Fecha

Hora

Descripción

Cada entrada modificada debe validarse (por ejemplo, la nueva fecha debe ser válida).

Tras la edición, debe mostrarse una confirmación del cambio y guardar los nuevos datos.

- 5. Listar eventos del mes
     Como usuario del calendario, quiero poder ver un resumen de los eventos de todo un mes, para tener una visión general de mi agenda mensual.

Criterios de aceptación:

El sistema debe pedir al usuario una fecha de referencia (para determinar el mes).

El sistema debe buscar todos los eventos cuya fecha pertenezca al mismo mes y año.

Si no hay eventos, mostrar: "No hay eventos registrados en este mes."

Si hay eventos:

Listarlos agrupados por fecha.

Dentro de cada día, ordenarlos por hora.

Mostrar: Fecha → Título → Hora → Descripción.

- 6. Buscar evento por nombre
     Como usuario del calendario, quiero poder buscar un evento por su nombre, para encontrar rápidamente información específica sin revisar día por día.

Criterios de aceptación:

El sistema debe permitir ingresar una cadena de búsqueda (parcial o completa).

La búsqueda no debe ser sensible a mayúsculas/minúsculas.

Debe mostrar todos los eventos cuyo título contenga esa cadena.

Para cada resultado, debe mostrar: Fecha, Hora, Título, Descripción.

Si no hay coincidencias, debe decir: "No se encontraron eventos con ese nombre."

- 7. Ver calendario en formato mensual
     Como usuario, quiero ver un calendario visual del mes con los días resaltados que tienen eventos, para identificar fácilmente los días ocupados.

Criterios de aceptación:

El sistema debe generar una vista tipo calendario para el mes solicitado (puede ser en consola o más visual si es gráfico).

Los días con eventos deben destacarse visualmente (ej: con un asterisco, color o símbolo).

El usuario debe poder navegar entre meses (anterior/siguiente).

Si no hay eventos, mostrar el calendario en limpio.

Si hay eventos, debe haber una opción para ver los detalles de un día desde el calendario.

- 8. Notificación de eventos próximos
     Como usuario, quiero recibir una notificación o mensaje cuando un evento se aproxima, para asegurarme de no olvidarlo.

Criterios de aceptación:

El sistema debe verificar si hay eventos dentro de un rango configurable (por defecto: 24 horas).

Al iniciar el sistema o en momentos clave, debe mostrar los eventos próximos con mensajes como:
"Recordatorio: Evento 'Reunión' mañana a las 10:00"

La lógica debe considerar la hora actual del sistema.

Los eventos pasados no deben mostrarse como recordatorio.

- 9. Evitar conflictos de horario
     Como usuario, quiero recibir una advertencia si intento crear un evento que se superpone con otro, para evitar solapamientos de compromisos.

Criterios de aceptación:

Al agregar un nuevo evento con fecha y hora, el sistema debe verificar si ya hay otro evento en la misma fecha y hora.

Si se detecta conflicto, debe mostrar:
"Advertencia: Ya existe un evento en este horario. ¿Deseas continuar? (S/N)"

Si el usuario elige continuar, se permite la superposición; si no, el evento no se crea.

Debe funcionar también al editar un evento existente.

- 10. Guardar eventos entre sesiones
      Como usuario del calendario, quiero que mis eventos se guarden incluso si cierro el programa, para no perder información cuando vuelva a abrirlo.

Criterios de aceptación:

Los eventos deben persistir en un archivo local (ej. JSON, CSV, SQLite).

Al iniciar el programa, el sistema debe cargar automáticamente los eventos guardados.

Al agregar, editar o eliminar eventos, el sistema debe actualizar el archivo.

Si el archivo no existe, debe crearse uno nuevo sin errores.

La carga y guardado deben ser silenciosos y automáticos para el usuario.
