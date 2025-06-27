# 🗓️ Sistema de Calendario en Python

**Desarrollado por:** Mariano Capella & Gabriel Osemberg

Un sistema de calendario moderno y profesional desarrollado en Python con interfaz gráfica usando `ttkbootstrap`. El proyecto está diseñado con arquitectura modular, separación de responsabilidades y buenas prácticas de desarrollo.

## 📋 Características Principales

### ✅ **Implementado**

- 🎨 **Interfaz moderna** con ttkbootstrap
- 🧭 **Navegación completa** entre meses y años
- 📅 **Vista de calendario** con grilla visual de días
- 🎯 **Selector de temas** dinámico (20+ temas disponibles)
- 🌓 **Temas claros y oscuros** organizados por categorías
- 🔄 **Cambio de tema en tiempo real** sin reiniciar
- 🏗️ **Arquitectura modular** con separación de responsabilidades
- 📚 **Documentación completa** con docstrings
- 🔒 **Type hints** para mejor mantenibilidad

### ⏳ **En desarrollo (Fase 4)**

- 📝 Gestión completa de eventos
- 🪟 Ventanas modales para eventos por día
- 🔍 Búsqueda y filtrado de eventos
- 🔔 Notificaciones de eventos próximos

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**
- **ttkbootstrap** - Interfaz gráfica moderna
- **datetime/calendar** - Manejo de fechas
- **JSON** - Persistencia de datos
- **typing** - Type hints para mejor código

## 📦 Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd Calendario

# Instalar dependencias
pip install ttkbootstrap

# Ejecutar la aplicación
python main.py
```

## 🏗️ Arquitectura del Sistema

El proyecto está organizado en módulos especializados siguiendo principios SOLID:

```
Calendario/
├── main.py              # 🚀 Punto de entrada de la aplicación
├── calendario_ui.py     # 🎨 Interfaz gráfica y widgets
├── calendario_logic.py  # 🧠 Lógica de navegación y calendario
├── theme_manager.py     # 🎭 Gestión completa de temas
├── helpers.py          # 🔧 Funciones de utilidad para fechas
├── eventos.py          # 📝 Sistema de gestión de eventos
├── data/               # 📁 Directorio de datos
│   └── eventos.json    # 💾 Almacenamiento de eventos
├── flujo.md           # 📋 Flujo de desarrollo y progreso
├── Sistema.md         # 📖 Especificaciones y criterios
└── README.md          # 📚 Este archivo
```

### 📖 **Descripción de Módulos**

#### `main.py` - Punto de Entrada

- Inicialización de la aplicación
- Configuración de ventana principal
- Manejo de errores globales

#### `calendario_ui.py` - Interfaz Gráfica

- Creación y gestión de widgets
- Layout y disposición de componentes
- Interacción usuario-interfaz
- Renderizado del calendario visual

#### `calendario_logic.py` - Lógica del Calendario

- Navegación entre meses y años
- Generación de matriz del calendario
- Manejo de fechas especiales
- Callbacks de actualización

#### `theme_manager.py` - Gestión de Temas

- 20+ temas organizados (claros/oscuros)
- Aplicación dinámica de temas
- Validación y manejo de errores
- Información de temas

#### `helpers.py` - Utilidades

- Formateo de fechas en español
- Validaciones de fecha
- Funciones de navegación
- Utilidades generales

#### `eventos.py` - Gestión de Eventos

- Clase `Evento` con dataclass
- Persistencia en JSON
- CRUD completo de eventos
- Búsqueda y filtrado

## 🎨 Temas Disponibles

### 🌞 **Temas Claros**

- litera, cosmo, flatly, journal, lumen, minty
- pulse, sandstone, united, yeti, morph, simplex
- cerculean, spacelab

### 🌙 **Temas Oscuros**

- solar, superhero, darkly, cyborg, vapor, slate

## 🚀 Uso de la Aplicación

### Controles de Navegación

- **<<** - Año anterior
- **<** - Mes anterior
- **Hoy** - Volver al mes actual
- **>** - Mes siguiente
- **>>** - Año siguiente

### Selector de Temas

- Dropdown con temas organizados
- Cambio instantáneo al seleccionar
- Título de ventana actualizado dinámicamente

### Calendario Visual

- Grilla de 7x6 con días del mes
- Día actual destacado en verde
- Fines de semana en amarillo
- Click en días para eventos (Fase 4)

## 👨‍💻 Para Desarrolladores

### Estructura de Clases Principales

```python
# Interfaz principal
class CalendarioUI:
    - Gestión de widgets
    - Eventos de UI
    - Interacción con lógica

# Lógica del calendario
class CalendarioLogic:
    - Navegación de fechas
    - Generación de calendario
    - Callbacks de actualización

# Gestión de temas
class ThemeManager:
    - Lista de temas disponibles
    - Aplicación dinámica
    - Validaciones

# Gestión de eventos (Fase 4)
class EventosManager:
    - CRUD de eventos
    - Persistencia JSON
    - Búsqueda y filtrado
```

### Principios Aplicados

- **Single Responsibility**: Cada módulo tiene una responsabilidad específica
- **Open/Closed**: Fácil extensión sin modificar código existente
- **Dependency Inversion**: Uso de callbacks e interfaces
- **Type Hints**: Código auto-documentado y mantenible
- **Documentación**: Docstrings completos en español

## 📈 Progreso del Proyecto

- ✅ **Fase 1**: Interfaz base con ttkbootstrap
- ✅ **Fase 2**: Navegación completa
- ✅ **Fase 3**: Visualización de días
- ✅ **EXTRA**: Selector de temas dinámico
- ✅ **REFACTORIZACIÓN**: Separación de responsabilidades
- ⏳ **Fase 4**: Gestión de eventos (en desarrollo)
- ⏳ **Fase 5**: Refinamiento visual

## 🔄 Próximas Mejoras

- 📝 Integración del sistema de eventos con la UI
- 🪟 Ventanas modales para gestión de eventos
- 🎨 Indicadores visuales de días con eventos
- 🔍 Búsqueda avanzada de eventos
- 🔔 Sistema de notificaciones
- 📤 Exportación/importación de eventos
- ⚙️ Configuración de recordatorios

## 🤝 Contribución

Este es un proyecto académico enfocado en aprender buenas prácticas de desarrollo:

1. **Branching Strategy**: Usar branches para nuevas features
2. **Code Review**: Revisar cambios antes de merge
3. **Testing**: Probar funcionalidades antes de commit
4. **Documentation**: Mantener documentación actualizada

## 📝 Licencia

Proyecto académico - Sistemas - UPC
Desarrollado con fines educativos.

---

**¿Preguntas o sugerencias?**
Contacta a los desarrolladores: Mariano Capella & Gabriel Osemberg
