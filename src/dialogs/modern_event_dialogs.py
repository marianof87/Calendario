"""
Modern_Event_Dialogs.py - Diálogos modernos para gestión de eventos

Este módulo implementa diálogos completamente refactorizados usando:
- Arquitectura basada en clases base abstractas
- Principios SOLID aplicados consistentemente
- Componentes reutilizables y estandarizados
- Validación robusta con feedback en tiempo real
- Logging y manejo de errores integrado
- Gestión optimizada de recursos

Reemplaza evento_dialogs.py con una implementación arquitectónicamente superior.

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import datetime
from typing import Optional, List, Dict, Any
from src.core.eventos import Evento, EventosManager
from src.utils.helpers import formatear_fecha_completa
from src.dialogs.dialog_base import BaseDialog, DialogException, DialogConstants
from src.dialogs.dialog_components import (
    FormField, TreeviewComponent, DialogHeader, 
    SmartEntry, SmartText
)


class ModernEventDialog(BaseDialog):
    """
    Diálogo moderno para agregar/editar eventos.
    
    Características:
    - Validación en tiempo real
    - Interfaz responsive
    - Feedback visual inmediato
    - Shortcuts de teclado
    - Gestión de errores robusta
    """
    
    def __init__(self, parent, evento: Optional[Evento] = None):
        """
        Inicializa el diálogo de evento.
        
        Args:
            parent: Ventana padre
            evento: Evento a editar (None para crear nuevo)
        """
        self.evento = evento
        self.is_editing = evento is not None
        
        # Campos del formulario
        self.field_titulo: Optional[FormField] = None
        self.field_fecha: Optional[FormField] = None
        self.field_hora: Optional[FormField] = None
        self.field_descripcion: Optional[FormField] = None
        
        title = "Editar Evento" if self.is_editing else "Agregar Nuevo Evento"
        super().__init__(parent, title, width=520, height=480)
    
    def _create_interface(self) -> None:
        """Crea la interfaz moderna del diálogo."""
        # Frame principal con padding
        main_frame = tb.Frame(self.window, padding=DialogConstants.MAIN_PADDING)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header del diálogo
        self._create_header(main_frame)
        
        # Formulario
        self._create_form(main_frame)
        
        # Botones
        self._create_buttons(main_frame)
        
        # Configurar focus inicial
        self._set_initial_focus()
    
    def _create_header(self, parent) -> None:
        """Crea el header del diálogo."""
        icon = "✏️" if self.is_editing else "➕"
        subtitle = f"Modificar evento existente" if self.is_editing else "Crear un nuevo evento en el calendario"
        
        header = DialogHeader(parent, self.title, subtitle, icon)
        header.pack(fill=X, pady=(0, 20))
    
    def _create_form(self, parent) -> None:
        """Crea el formulario de evento."""
        form_frame = tb.Frame(parent)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Campo Título (requerido)
        self.field_titulo = FormField(
            form_frame, 
            "Título del Evento", 
            field_type="entry",
            required=True,
            placeholder="Ingrese el título del evento...",
            bootstyle=PRIMARY,
            font=("Arial", 11)
        )
        self.field_titulo.pack(fill=X, pady=(0, 15))
        
        # Frame para fecha y hora (en la misma línea)
        datetime_frame = tb.Frame(form_frame)
        datetime_frame.pack(fill=X, pady=(0, 15))
        
        # Campo Fecha (requerido)
        fecha_frame = tb.Frame(datetime_frame)
        fecha_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        self.field_fecha = FormField(
            fecha_frame,
            "Fecha",
            field_type="entry",
            required=True,
            validation_type="date",
            placeholder="YYYY-MM-DD",
            bootstyle=INFO,
            width=12
        )
        self.field_fecha.pack(fill=X)
        
        # Botón "Hoy" para fecha
        btn_hoy = tb.Button(
            fecha_frame,
            text="Hoy",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._set_today,
            width=8
        )
        btn_hoy.pack(pady=(5, 0))
        
        # Campo Hora (opcional)
        hora_frame = tb.Frame(datetime_frame)
        hora_frame.pack(side=LEFT, fill=X, expand=True)
        
        self.field_hora = FormField(
            hora_frame,
            "Hora (Opcional)",
            field_type="entry",
            validation_type="time",
            placeholder="HH:MM",
            bootstyle=SUCCESS,
            width=8
        )
        self.field_hora.pack(fill=X)
        
        # Ejemplos de hora
        tb.Label(
            hora_frame,
            text="Ej: 14:30, 09:00",
            font=("Arial", 8),
            bootstyle=SECONDARY
        ).pack(pady=(2, 0))
        
        # Campo Descripción (opcional) con contador de caracteres
        desc_frame = tb.Frame(form_frame)
        desc_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Label y contador
        desc_header = tb.Frame(desc_frame)
        desc_header.pack(fill=X)
        
        tb.Label(
            desc_header,
            text="Descripción (Opcional)",
            font=("Arial", 10, "bold")
        ).pack(side=LEFT)
        
        self.char_counter = tb.Label(
            desc_header,
            text="0/500",
            font=("Arial", 8),
            bootstyle=SECONDARY
        )
        self.char_counter.pack(side=RIGHT)
        
        # Text widget con scrollbar
        text_frame = tb.Frame(desc_frame)
        text_frame.pack(fill=BOTH, expand=True, pady=(5, 0))
        
        self.text_descripcion = SmartText(
            text_frame,
            height=4,
            font=("Arial", 10),
            wrap=WORD,
            max_chars=500
        )
        self.text_descripcion.set_char_counter_label(self.char_counter)
        
        scrollbar_desc = tb.Scrollbar(text_frame, orient=VERTICAL, command=self.text_descripcion.yview)
        self.text_descripcion.configure(yscrollcommand=scrollbar_desc.set)
        
        self.text_descripcion.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_desc.pack(side=RIGHT, fill=Y)
        
        # Cargar datos si estamos editando
        if self.is_editing:
            self._load_event_data()
    
    def _create_buttons(self, parent) -> None:
        """Crea los botones del diálogo."""
        button_frame = self._create_button_frame(parent)
        
        accept_text = "Actualizar" if self.is_editing else "Guardar"
        self._create_standard_buttons(button_frame, accept_text, "Cancelar")
    
    def _set_today(self) -> None:
        """Establece la fecha de hoy."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.field_fecha.set_value(today)
    
    def _load_event_data(self) -> None:
        """Carga los datos del evento para edición."""
        if self.evento:
            self.field_titulo.set_value(self.evento.titulo)
            self.field_fecha.set_value(self.evento.fecha)
            if self.evento.hora:
                self.field_hora.set_value(self.evento.hora)
            if self.evento.descripcion:
                self.text_descripcion.delete("1.0", END)
                self.text_descripcion.insert("1.0", self.evento.descripcion)
    
    def _set_initial_focus(self) -> None:
        """Establece el focus inicial."""
        if self.field_titulo and self.field_titulo.input_widget:
            self.field_titulo.input_widget.focus()
    
    def _validate_input(self) -> bool:
        """Valida todos los campos del formulario."""
        errors = []
        
        # Validar título
        if not self.field_titulo.is_valid():
            errors.append(self.field_titulo.get_validation_error())
        
        # Validar fecha
        if not self.field_fecha.is_valid():
            errors.append(self.field_fecha.get_validation_error())
        else:
            # Validación adicional de fecha
            fecha_str = self.field_fecha.get_value()
            try:
                fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                # Advertir si es fecha muy antigua
                if fecha < datetime.date.today() - datetime.timedelta(days=365):
                    respuesta = Messagebox.show_question(
                        "Fecha Antigua",
                        f"La fecha seleccionada ({fecha_str}) es de hace más de un año.\n¿Desea continuar?",
                        parent=self.window
                    )
                    if respuesta != "Yes":
                        return False
            except ValueError:
                errors.append("Formato de fecha inválido")
        
        # Validar hora si se proporciona
        if self.field_hora.get_value() and not self.field_hora.is_valid():
            errors.append(self.field_hora.get_validation_error())
        
        # Validar longitud de descripción
        descripcion = self.text_descripcion.get_clean_text()
        if len(descripcion) > 500:
            errors.append("La descripción no puede exceder 500 caracteres")
        
        # Mostrar errores si existen
        if errors:
            error_message = "Se encontraron los siguientes errores:\n\n" + "\n".join(f"• {error}" for error in errors)
            self._show_validation_error(error_message)
            return False
        
        return True
    
    def _get_result(self) -> Dict[str, Any]:
        """Obtiene el resultado del diálogo."""
        descripcion = self.text_descripcion.get_clean_text()
        hora = self.field_hora.get_value()
        
        return {
            'titulo': self.field_titulo.get_value().strip(),
            'fecha': self.field_fecha.get_value().strip(),
            'hora': hora.strip() if hora else None,
            'descripcion': descripcion if descripcion else None
        }


class ModernEventListDialog(BaseDialog):
    """
    Diálogo moderno para mostrar y gestionar eventos de un día específico.
    
    Características:
    - Lista interactiva con búsqueda
    - Menú contextual avanzado
    - Actualizaciones en tiempo real
    - Estadísticas dinámicas
    - Operaciones batch
    """
    
    def __init__(self, parent, fecha: datetime.date, eventos_manager: EventosManager):
        """
        Inicializa el diálogo de lista de eventos.
        
        Args:
            parent: Ventana padre
            fecha: Fecha de los eventos a mostrar
            eventos_manager: Gestor de eventos
        """
        self.fecha = fecha
        self.eventos_manager = eventos_manager
        self.callback_actualizar: Optional[callable] = None
        
        # Componentes
        self.tree_component: Optional[TreeviewComponent] = None
        self.search_field: Optional[FormField] = None
        self.stats_label: Optional[tb.Label] = None
        
        # Datos
        self.eventos_originales: List[Evento] = []
        self.eventos_filtrados: List[Evento] = []
        
        title = f"Eventos del {formatear_fecha_completa(fecha)}"
        super().__init__(parent, title, width=720, height=580)
    
    def _create_interface(self) -> None:
        """Crea la interfaz del diálogo."""
        main_frame = tb.Frame(self.window, padding=DialogConstants.MAIN_PADDING)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        self._create_header(main_frame)
        
        # Barra de herramientas
        self._create_toolbar(main_frame)
        
        # Área de búsqueda
        self._create_search_area(main_frame)
        
        # Lista de eventos
        self._create_event_list(main_frame)
        
        # Estadísticas
        self._create_stats_area(main_frame)
        
        # Botones
        self._create_buttons(main_frame)
        
        # Cargar datos iniciales
        self._load_events()
    
    def _create_header(self, parent) -> None:
        """Crea el header del diálogo."""
        header = DialogHeader(
            parent, 
            f"📅 {formatear_fecha_completa(self.fecha)}",
            "Gestión de eventos del día seleccionado"
        )
        header.pack(fill=X, pady=(0, 15))
    
    def _create_toolbar(self, parent) -> None:
        """Crea la barra de herramientas."""
        toolbar = tb.Frame(parent)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # Botón Agregar Evento
        tb.Button(
            toolbar,
            text="➕ Nuevo Evento",
            bootstyle=SUCCESS,
            command=self._add_event
        ).pack(side=LEFT, padx=(0, 10))
        
        # Botón Actualizar
        tb.Button(
            toolbar,
            text="🔄 Actualizar",
            bootstyle=(OUTLINE, INFO),
            command=self._load_events
        ).pack(side=LEFT, padx=(0, 10))
        
        # Botón Exportar (funcionalidad futura)
        tb.Button(
            toolbar,
            text="📤 Exportar",
            bootstyle=(OUTLINE, SECONDARY),
            state="disabled"  # Por ahora deshabilitado
        ).pack(side=LEFT)
    
    def _create_search_area(self, parent) -> None:
        """Crea el área de búsqueda."""
        search_frame = tb.Frame(parent)
        search_frame.pack(fill=X, pady=(0, 15))
        
        tb.Label(
            search_frame,
            text="🔍 Buscar en eventos:",
            font=("Arial", 10, "bold")
        ).pack(anchor=W)
        
        search_input_frame = tb.Frame(search_frame)
        search_input_frame.pack(fill=X, pady=(5, 0))
        
        self.search_entry = SmartEntry(
            search_input_frame,
            placeholder="Buscar por título o descripción...",
            bootstyle=INFO
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # Bind para búsqueda en tiempo real
        self.search_entry.bind('<KeyRelease>', lambda e: self._filter_events())
        
        tb.Button(
            search_input_frame,
            text="Limpiar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._clear_search
        ).pack(side=RIGHT)
    
    def _create_event_list(self, parent) -> None:
        """Crea la lista de eventos."""
        list_frame = tb.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Configuración de columnas
        columns = {
            'hora': {'text': 'Hora', 'width': 100, 'minwidth': 80},
            'titulo': {'text': 'Título', 'width': 200, 'minwidth': 150},
            'descripcion': {'text': 'Descripción', 'width': 350, 'minwidth': 200}
        }
        
        self.tree_component = TreeviewComponent(list_frame, columns, height=15)
        self.tree_component.pack(fill=BOTH, expand=True)
        
        # Bindings
        self.tree_component.bind_double_click(self._edit_selected_event)
        self.tree_component.bind_right_click(self._show_context_menu)
    
    def _create_stats_area(self, parent) -> None:
        """Crea el área de estadísticas."""
        stats_frame = tb.Frame(parent)
        stats_frame.pack(fill=X, pady=(5, 0))
        
        self.stats_label = tb.Label(
            stats_frame,
            text="",
            font=("Arial", 9),
            bootstyle=SECONDARY
        )
        self.stats_label.pack(side=LEFT)
    
    def _create_buttons(self, parent) -> None:
        """Crea los botones del diálogo."""
        button_frame = self._create_button_frame(parent)
        
        tb.Button(
            button_frame,
            text="Cerrar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._on_cancel,
            width=DialogConstants.BUTTON_WIDTH
        ).pack(side=RIGHT)
    
    def _load_events(self) -> None:
        """Carga los eventos del día."""
        try:
            self.eventos_originales = self.eventos_manager.obtener_eventos_fecha(self.fecha)
            self.eventos_filtrados = self.eventos_originales.copy()
            self._update_event_list()
            self._update_stats()
            self.logger.info(f"Cargados {len(self.eventos_originales)} eventos para {self.fecha}")
        except Exception as e:
            self.logger.error("Error cargando eventos", e)
            self._show_error("Error", f"No se pudieron cargar los eventos: {str(e)}")
    
    def _update_event_list(self) -> None:
        """Actualiza la lista de eventos mostrada."""
        if not self.tree_component:
            return
        
        self.tree_component.clear()
        
        for evento in self.eventos_filtrados:
            hora_display = evento.hora or "Todo el día"
            desc_preview = self._get_description_preview(evento.descripcion)
            
            self.tree_component.add_item(
                [hora_display, evento.titulo, desc_preview],
                [evento.id]
            )
    
    def _get_description_preview(self, descripcion: Optional[str]) -> str:
        """Obtiene preview de la descripción."""
        if not descripcion:
            return ""
        
        if len(descripcion) <= 50:
            return descripcion
        
        return descripcion[:47] + "..."
    
    def _filter_events(self) -> None:
        """Filtra eventos según el término de búsqueda."""
        search_term = self.search_entry.get_real_value().lower().strip()
        
        if not search_term:
            self.eventos_filtrados = self.eventos_originales.copy()
        else:
            self.eventos_filtrados = [
                evento for evento in self.eventos_originales
                if (search_term in evento.titulo.lower() or 
                    (evento.descripcion and search_term in evento.descripcion.lower()))
            ]
        
        self._update_event_list()
        self._update_stats()
    
    def _clear_search(self) -> None:
        """Limpia la búsqueda."""
        self.search_entry.delete(0, END)
        self._filter_events()
    
    def _update_stats(self) -> None:
        """Actualiza las estadísticas."""
        total = len(self.eventos_originales)
        filtrados = len(self.eventos_filtrados)
        con_hora = len([e for e in self.eventos_filtrados if e.hora])
        
        if total == filtrados:
            stats_text = f"📊 {total} evento(s) • {con_hora} con hora específica"
        else:
            stats_text = f"📊 Mostrando {filtrados} de {total} eventos • {con_hora} con hora específica"
        
        if self.stats_label:
            self.stats_label.config(text=stats_text)
    
    def _add_event(self) -> None:
        """Abre diálogo para agregar nuevo evento."""
        dialog = ModernEventDialog(self.window)
        
        # Pre-establecer la fecha
        dialog.field_fecha.set_value(self.fecha.strftime("%Y-%m-%d"))
        
        result = dialog.show()
        if result:
            self._process_add_event(result)
    
    def _process_add_event(self, event_data: Dict[str, Any]) -> None:
        """Procesa la adición de un nuevo evento."""
        try:
            exito, mensaje, evento = self.eventos_manager.agregar_evento(
                titulo=event_data['titulo'],
                fecha=event_data['fecha'],
                hora=event_data['hora'],
                descripcion=event_data['descripcion']
            )
            
            if exito:
                Messagebox.show_info("Éxito", mensaje, parent=self.window)
                self._load_events()
                self.trigger_callback('update')
            else:
                self._show_error("Error", mensaje)
                
        except Exception as e:
            self.logger.error("Error agregando evento", e)
            self._show_error("Error", f"No se pudo agregar el evento: {str(e)}")
    
    def _edit_selected_event(self, event=None) -> None:
        """Edita el evento seleccionado."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        # Obtener ID del evento
        tags = self.tree_component.get_item_tags(selected_item)
        if not tags:
            return
        
        evento_id = tags[0]
        evento = self.eventos_manager.buscar_evento_por_id(evento_id)
        
        if evento:
            dialog = ModernEventDialog(self.window, evento)
            result = dialog.show()
            
            if result:
                self._process_edit_event(evento_id, result)
    
    def _process_edit_event(self, evento_id: str, event_data: Dict[str, Any]) -> None:
        """Procesa la edición de un evento."""
        try:
            # Eliminar evento actual
            self.eventos_manager.eliminar_evento(evento_id)
            
            # Crear evento actualizado
            from eventos import Evento
            evento_actualizado = Evento(
                id=evento_id,
                titulo=event_data['titulo'],
                fecha=event_data['fecha'],
                hora=event_data['hora'],
                descripcion=event_data['descripcion']
            )
            
            # Agregar evento actualizado
            self.eventos_manager.eventos.append(evento_actualizado)
            self.eventos_manager.guardar_eventos()
            
            Messagebox.show_info("Éxito", "Evento actualizado correctamente", parent=self.window)
            self._load_events()
            self.trigger_callback('update')
            
        except Exception as e:
            self.logger.error("Error editando evento", e)
            self._show_error("Error", f"No se pudo editar el evento: {str(e)}")
    
    def _show_context_menu(self, event) -> None:
        """Muestra menú contextual."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        menu = tb.Menu(self.window, tearoff=0)
        menu.add_command(label="✏️ Editar", command=self._edit_selected_event)
        menu.add_command(label="🗑️ Eliminar", command=self._delete_selected_event)
        menu.add_separator()
        menu.add_command(label="📋 Copiar título", command=self._copy_event_title)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _delete_selected_event(self) -> None:
        """Elimina el evento seleccionado."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        tags = self.tree_component.get_item_tags(selected_item)
        if not tags:
            return
        
        evento_id = tags[0]
        evento = self.eventos_manager.buscar_evento_por_id(evento_id)
        
        if evento:
            resultado = Messagebox.show_question(
                "Confirmar Eliminación",
                f"¿Está seguro que desea eliminar el evento?\n\n"
                f"Título: {evento.titulo}\n"
                f"Fecha: {evento.fecha}\n"
                f"Hora: {evento.hora or 'Todo el día'}\n\n"
                f"Esta acción no se puede deshacer.",
                parent=self.window
            )
            
            if resultado == "Yes":
                try:
                    exito, mensaje = self.eventos_manager.eliminar_evento(evento_id)
                    if exito:
                        Messagebox.show_info("Éxito", mensaje, parent=self.window)
                        self._load_events()
                        self.trigger_callback('update')
                    else:
                        self._show_error("Error", mensaje)
                except Exception as e:
                    self.logger.error("Error eliminando evento", e)
                    self._show_error("Error", f"No se pudo eliminar el evento: {str(e)}")
    
    def _copy_event_title(self) -> None:
        """Copia el título del evento al clipboard."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        values = self.tree_component.get_item_values(selected_item)
        if values and len(values) > 1:
            try:
                self.window.clipboard_clear()
                self.window.clipboard_append(values[1])  # Título está en índice 1
                Messagebox.show_info("Copiado", "Título copiado al portapapeles", parent=self.window)
            except Exception as e:
                self.logger.error("Error copiando al clipboard", e)
    
    def set_callback_actualizar(self, callback: callable) -> None:
        """Establece callback para actualizar vista principal."""
        self.set_callback('update', callback)
    
    def _validate_input(self) -> bool:
        """No hay validación para este diálogo."""
        return True
    
    def _get_result(self) -> Any:
        """No retorna resultado específico."""
        return None


class ModernSearchDialog(BaseDialog):
    """
    Diálogo moderno para búsqueda avanzada de eventos.
    
    Características:
    - Búsqueda en tiempo real
    - Filtros múltiples
    - Resultados paginados
    - Exportación de resultados
    - Historial de búsquedas
    """
    
    def __init__(self, parent, eventos_manager: EventosManager):
        """
        Inicializa el diálogo de búsqueda.
        
        Args:
            parent: Ventana padre
            eventos_manager: Gestor de eventos
        """
        self.eventos_manager = eventos_manager
        
        # Componentes
        self.search_entry: Optional[SmartEntry] = None
        self.tree_component: Optional[TreeviewComponent] = None
        self.results_label: Optional[tb.Label] = None
        
        # Datos
        self.all_events: List[Evento] = []
        self.filtered_events: List[Evento] = []
        
        super().__init__(parent, "🔍 Búsqueda Avanzada de Eventos", width=800, height=600)
    
    def _create_interface(self) -> None:
        """Crea la interfaz de búsqueda."""
        main_frame = tb.Frame(self.window, padding=DialogConstants.MAIN_PADDING)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Header
        self._create_header(main_frame)
        
        # Área de búsqueda
        self._create_search_area(main_frame)
        
        # Área de resultados
        self._create_results_area(main_frame)
        
        # Estadísticas
        self._create_stats_area(main_frame)
        
        # Botones
        self._create_buttons(main_frame)
        
        # Cargar todos los eventos
        self._load_all_events()
    
    def _create_header(self, parent) -> None:
        """Crea el header del diálogo."""
        header = DialogHeader(
            parent,
            "Búsqueda de Eventos",
            "Encuentre eventos por título, descripción o fecha",
            "🔍"
        )
        header.pack(fill=X, pady=(0, 20))
    
    def _create_search_area(self, parent) -> None:
        """Crea el área de búsqueda."""
        search_frame = tb.LabelFrame(parent, text="Criterios de Búsqueda", padding=15)
        search_frame.pack(fill=X, pady=(0, 15))
        
        # Campo de búsqueda principal
        tb.Label(
            search_frame,
            text="Término de búsqueda:",
            font=("Arial", 10, "bold")
        ).pack(anchor=W)
        
        search_input_frame = tb.Frame(search_frame)
        search_input_frame.pack(fill=X, pady=(5, 15))
        
        self.search_entry = SmartEntry(
            search_input_frame,
            placeholder="Buscar en títulos y descripciones...",
            bootstyle=INFO,
            font=("Arial", 11)
        )
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.search_entry.focus()
        
        # Bind para búsqueda en tiempo real
        self.search_entry.bind('<KeyRelease>', lambda e: self._perform_search())
        
        tb.Button(
            search_input_frame,
            text="Limpiar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._clear_search
        ).pack(side=RIGHT)
        
        # Opciones adicionales (para futuras implementaciones)
        options_frame = tb.Frame(search_frame)
        options_frame.pack(fill=X)
        
        tb.Label(
            options_frame,
            text="💡 Tip: La búsqueda se realiza automáticamente mientras escribe",
            font=("Arial", 9),
            bootstyle=SECONDARY
        ).pack(anchor=W)
    
    def _create_results_area(self, parent) -> None:
        """Crea el área de resultados."""
        results_frame = tb.LabelFrame(parent, text="Resultados", padding=10)
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Configuración de columnas
        columns = {
            'fecha': {'text': 'Fecha', 'width': 100, 'minwidth': 80},
            'hora': {'text': 'Hora', 'width': 80, 'minwidth': 60},
            'titulo': {'text': 'Título', 'width': 200, 'minwidth': 150},
            'descripcion': {'text': 'Descripción', 'width': 350, 'minwidth': 250}
        }
        
        self.tree_component = TreeviewComponent(results_frame, columns, height=18)
        self.tree_component.pack(fill=BOTH, expand=True)
        
        # Bindings para interacción
        self.tree_component.bind_double_click(self._on_result_double_click)
        self.tree_component.bind_right_click(self._show_result_context_menu)
    
    def _create_stats_area(self, parent) -> None:
        """Crea el área de estadísticas."""
        stats_frame = tb.Frame(parent)
        stats_frame.pack(fill=X, pady=(5, 0))
        
        self.results_label = tb.Label(
            stats_frame,
            text="",
            font=("Arial", 10),
            bootstyle=INFO
        )
        self.results_label.pack(side=LEFT)
    
    def _create_buttons(self, parent) -> None:
        """Crea los botones del diálogo."""
        button_frame = self._create_button_frame(parent)
        
        tb.Button(
            button_frame,
            text="Cerrar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._on_cancel,
            width=DialogConstants.BUTTON_WIDTH
        ).pack(side=RIGHT)
    
    def _load_all_events(self) -> None:
        """Carga todos los eventos disponibles."""
        try:
            self.all_events = self.eventos_manager.eventos.copy()
            self.filtered_events = self.all_events.copy()
            self._update_results()
            self.logger.info(f"Cargados {len(self.all_events)} eventos para búsqueda")
        except Exception as e:
            self.logger.error("Error cargando eventos", e)
            self._show_error("Error", f"No se pudieron cargar los eventos: {str(e)}")
    
    def _perform_search(self) -> None:
        """Realiza la búsqueda de eventos."""
        search_term = self.search_entry.get_real_value().lower().strip()
        
        if not search_term:
            self.filtered_events = self.all_events.copy()
        else:
            self.filtered_events = [
                evento for evento in self.all_events
                if (search_term in evento.titulo.lower() or
                    (evento.descripcion and search_term in evento.descripcion.lower()))
            ]
        
        # Ordenar por fecha (más recientes primero)
        self.filtered_events.sort(key=lambda e: (e.fecha, e.hora or "00:00"), reverse=True)
        
        self._update_results()
    
    def _update_results(self) -> None:
        """Actualiza los resultados mostrados."""
        if not self.tree_component:
            return
        
        self.tree_component.clear()
        
        for evento in self.filtered_events:
            hora_display = evento.hora or "Todo el día"
            desc_preview = self._get_description_preview(evento.descripcion)
            
            self.tree_component.add_item(
                [evento.fecha, hora_display, evento.titulo, desc_preview],
                [evento.id]
            )
        
        # Actualizar estadísticas
        search_term = self.search_entry.get_real_value().strip()
        total = len(self.all_events)
        found = len(self.filtered_events)
        
        if search_term:
            stats_text = f"Se encontraron {found} eventos de {total} para '{search_term}'"
        else:
            stats_text = f"Mostrando todos los eventos: {total}"
        
        if self.results_label:
            self.results_label.config(text=stats_text)
    
    def _get_description_preview(self, descripcion: Optional[str]) -> str:
        """Obtiene preview de la descripción."""
        if not descripcion:
            return ""
        
        if len(descripcion) <= 60:
            return descripcion
        
        return descripcion[:57] + "..."
    
    def _clear_search(self) -> None:
        """Limpia la búsqueda."""
        self.search_entry.delete(0, END)
        self._perform_search()
    
    def _on_result_double_click(self, event) -> None:
        """Maneja doble click en resultado."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        # Mostrar información detallada del evento
        self._show_event_details(selected_item)
    
    def _show_event_details(self, item_id: str) -> None:
        """Muestra detalles completos del evento."""
        tags = self.tree_component.get_item_tags(item_id)
        if not tags:
            return
        
        evento_id = tags[0]
        evento = self.eventos_manager.buscar_evento_por_id(evento_id)
        
        if evento:
            details = f"📅 {evento.titulo}\n\n"
            details += f"Fecha: {evento.fecha}\n"
            details += f"Hora: {evento.hora or 'Todo el día'}\n"
            
            if evento.descripcion:
                details += f"\nDescripción:\n{evento.descripcion}"
            
            Messagebox.show_info("Detalles del Evento", details, parent=self.window)
    
    def _show_result_context_menu(self, event) -> None:
        """Muestra menú contextual para resultados."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        menu = tb.Menu(self.window, tearoff=0)
        menu.add_command(label="👁️ Ver detalles", command=lambda: self._show_event_details(selected_item))
        menu.add_command(label="📋 Copiar título", command=self._copy_result_title)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _copy_result_title(self) -> None:
        """Copia el título del resultado al clipboard."""
        selected_item = self.tree_component.get_selected_item()
        if not selected_item:
            return
        
        values = self.tree_component.get_item_values(selected_item)
        if values and len(values) > 2:
            try:
                self.window.clipboard_clear()
                self.window.clipboard_append(values[2])  # Título está en índice 2
                Messagebox.show_info("Copiado", "Título copiado al portapapeles", parent=self.window)
            except Exception as e:
                self.logger.error("Error copiando al clipboard", e)
    
    def _validate_input(self) -> bool:
        """No hay validación para este diálogo."""
        return True
    
    def _get_result(self) -> Any:
        """No retorna resultado específico."""
        return None 