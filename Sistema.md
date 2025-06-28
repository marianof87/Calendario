# 🗓️ Sistema de Calendario - Especificación Técnica

**Desarrollado por:** Mariano Capella & Gabriel Osemberg  
**Tecnología:** Python + ttkbootstrap  
**Arquitectura:** Modular con principios SOLID

---

## 📖 **¿Qué hace el sistema?**

Sistema de calendario moderno con **interfaz gráfica profesional** que permite:

- ✅ **Navegación temporal** - Navegar entre meses/años con controles intuitivos
- ✅ **Gestión de eventos** - Crear, editar, eliminar y buscar eventos
- ✅ **Vista calendario** - Grilla visual con días destacados cuando tienen eventos
- ✅ **Notificaciones** - Alertas sonoras para eventos próximos y actuales
- ✅ **Temas dinámicos** - 20+ temas visuales (claros/oscuros) cambiables en tiempo real
- ✅ **Persistencia** - Eventos guardados en JSON que persisten entre sesiones

---

## 🏗️ **Diagrama de Arquitectura**

```
Calendario/
├── 📁 src/                          # Código fuente principal
│   ├── 📁 core/                     # Lógica de negocio
│   │   ├── eventos.py               # Modelo Evento + EventosManager
│   │   └── calendario_logic.py      # Lógica del calendario
│   │
│   ├── 📁 ui/                       # Interfaces gráficas
│   │   ├── calendario_ui.py         # Interfaz principal
│   │   └── theme_manager.py         # Gestor de temas
│   │
│   ├── 📁 dialogs/                  # Diálogos y componentes
│   │   ├── dialog_base.py           # Clase base abstracta
│   │   ├── dialog_components.py     # Componentes reutilizables
│   │   └── enhanced_event_dialogs.py # Diálogos modernos
│   │
│   ├── 📁 notifications/            # Sistema de notificaciones
│   │   ├── notificaciones.py        # NotificacionesManager
│   │   └── notificacion_timer.py    # Timer en tiempo real
│   │
│   └── 📁 utils/                    # Utilidades
│       └── helpers.py               # Funciones auxiliares
│
├── 📁 data/                         # Archivos de datos
│   └── eventos.json                 # Base de datos JSON
│
└── 📋 main.py                       # Punto de entrada
```

### **🔧 Principios Aplicados**

- **Separación de responsabilidades** - Cada módulo tiene un propósito específico
- **Arquitectura SOLID** - Extensible, mantenible, testeable
- **Componentes reutilizables** - UI modular con validación en tiempo real
- **Gestión robusta** - Manejo de errores, logging, memoria optimizada

---

## 👤 **Historias de Usuario**

### **1. Agregar Evento**

**Como usuario del calendario, quiero poder agregar un evento con una fecha y hora específicas, para recordar compromisos importantes.**

**Criterios de aceptación:**

- ✅ Solicitar: Título (obligatorio), Fecha (YYYY-MM-DD), Hora (HH:MM opcional), Descripción (opcional)
- ✅ Validar fecha y hora con feedback visual en tiempo real
- ✅ Mostrar error si título vacío o fecha inválida
- ✅ Confirmar creación: _"Evento 'Reunión' creado para el 2025-07-01 a las 14:00"_
- ✅ Persistir evento automáticamente en JSON

### **2. Ver Eventos del Día**

**Como usuario del calendario, quiero poder ver todos los eventos programados para un día específico, para planificar mi jornada eficientemente.**

**Criterios de aceptación:**

- ✅ Click en día del calendario abre lista de eventos
- ✅ Mostrar _"No hay eventos para esta fecha"_ si está vacío
- ✅ Ordenar eventos cronológicamente por hora
- ✅ Mostrar título, hora y descripción de cada evento
- ✅ Permitir editar/eliminar desde la lista

### **3. Eliminar Evento**

**Como usuario del calendario, quiero poder eliminar un evento previamente creado, para mantener actualizado mi calendario si hay cambios.**

**Criterios de aceptación:**

- ✅ Seleccionar evento desde lista del día
- ✅ Mostrar resumen antes de confirmar eliminación
- ✅ Solicitar confirmación: _"¿Está seguro que desea eliminar este evento?"_
- ✅ Confirmar eliminación: _"Evento eliminado exitosamente"_
- ✅ Actualizar vista automáticamente

### **4. Editar Evento**

**Como usuario del calendario, quiero poder modificar la información de un evento existente, para corregir errores o cambiar detalles.**

**Criterios de aceptación:**

- ✅ Abrir evento desde lista para edición
- ✅ Mostrar formulario con datos actuales pre-cargados
- ✅ Validar cada campo modificado (fecha, hora, título)
- ✅ Confirmar cambios y actualizar vista
- ✅ Mantener validación en tiempo real

### **5. Listar Eventos del Mes**

**Como usuario del calendario, quiero poder ver un resumen de los eventos de todo un mes, para tener una visión general de mi agenda mensual.**

**Criterios de aceptación:**

- ✅ Botón "📅 Mes" muestra todos los eventos del mes actual
- ✅ Agrupar eventos por fecha
- ✅ Ordenar por fecha y hora dentro de cada día
- ✅ Mostrar: Fecha → Título → Hora → Descripción
- ✅ Indicar si no hay eventos: _"No hay eventos registrados en este mes"_

### **6. Buscar Evento por Nombre**

**Como usuario del calendario, quiero poder buscar un evento por su nombre, para encontrar rápidamente información específica.**

**Criterios de aceptación:**

- ✅ Botón "🔍 Buscar" abre diálogo de búsqueda
- ✅ Búsqueda no sensible a mayúsculas/minúsculas
- ✅ Mostrar coincidencias en tiempo real mientras se escribe
- ✅ Mostrar: Fecha, Hora, Título, Descripción para cada resultado
- ✅ Indicar: _"No se encontraron eventos con ese nombre"_

### **7. Ver Calendario en Formato Mensual**

**Como usuario, quiero ver un calendario visual del mes con los días resaltados que tienen eventos, para identificar fácilmente los días ocupados.**

**Criterios de aceptación:**

- ✅ Vista calendario con grilla 7x6 (días de la semana)
- ✅ Días con eventos destacados visualmente
- ✅ Navegación: << < Hoy > >> (año anterior, mes anterior, hoy, mes siguiente, año siguiente)
- ✅ Día actual resaltado en color diferente
- ✅ Click en día muestra eventos específicos

### **8. Notificación de Eventos Próximos (Optimizado)**

**Como usuario, quiero recibir una notificación cuando un evento se aproxima, sin que el sistema se sobrecargue o se trabe.**

**Criterios de aceptación:**

- ✅ **Verificación inteligente** cada 60 segundos en segundo plano
- ✅ **Protección contra sobrecargas**:
  - ⏸️ Auto-pausa de 5 minutos durante eventos activos
  - 🛡️ Mínimo 30 segundos entre notificaciones
  - 🔊 Sonido ejecutado en hilo separado (no bloqueante)
- ✅ **Controles manuales disponibles**:
  - 🔔 **Test**: Botón para probar notificaciones
  - ▶️ **Reanudar**: Reanudar timer si queda pausado
  - 📊 **Stats**: Ver estadísticas del sistema
- ✅ **Solo eventos actuales** (±2 min): Evita spam de notificaciones
- ✅ **Una notificación por evento por día**: Evita duplicados

### **9. Evitar Conflictos de Horario**

**Como usuario, quiero recibir una advertencia si intento crear un evento que se superpone con otro, para evitar solapamientos de compromisos.**

**Criterios de aceptación:**

- ✅ Detectar conflictos al agregar/editar eventos con hora
- ✅ Mostrar advertencia: _"Ya existe un evento en este horario. ¿Deseas continuar?"_
- ✅ Permitir continuar si usuario confirma
- ✅ Funcionar tanto para creación como edición

### **10. Guardar Eventos entre Sesiones**

**Como usuario del calendario, quiero que mis eventos se guarden incluso si cierro el programa, para no perder información cuando vuelva a abrirlo.**

**Criterios de aceptación:**

- ✅ Persistencia automática en `data/eventos.json`
- ✅ Carga automática al iniciar aplicación
- ✅ Actualización automática en todas las operaciones CRUD
- ✅ Crear archivo si no existe, sin errores
- ✅ Proceso silencioso para el usuario

---

## 🚀 **Instalación y Uso**

```bash
# Instalar dependencia
pip install ttkbootstrap

# Ejecutar sistema
python main.py
```

**Características del sistema:**

- 🎨 **20+ temas visuales** - Claros y oscuros
- 🔊 **Notificaciones sonoras** - Windows + multiplataforma
- ⚡ **Validación en tiempo real** - Feedback inmediato
- 🏗️ **Arquitectura empresarial** - Código limpio y escalable
