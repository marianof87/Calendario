"""
Enhanced_Event_Dialogs.py - Diálogos modernos para gestión de eventos

Este módulo implementa diálogos completamente refactorizados usando:
- Arquitectura basada en clases base abstractas
- Principios SOLID aplicados consistentemente
- Componentes reutilizables y estandarizados
- Validación robusta con feedback en tiempo real

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import datetime
from typing import Optional, List, Dict, Any
from src.core.eventos import Evento, EventosManager
from src.utils.helpers import formatear_fecha_completa
from src.dialogs.dialog_base import BaseDialog, DialogConstants
from src.dialogs.dialog_components import FormField, TreeviewComponent, DialogHeader, SmartEntry, SmartText


class EnhancedEventDialog(BaseDialog):
    """Diálogo moderno para agregar/editar eventos."""
    
    def __init__(self, parent, evento: Optional[Evento] = None):
        self.evento = evento
        self.is_editing = evento is not None
        
        # Campos del formulario
        self.field_titulo: Optional[FormField] = None
        self.field_fecha: Optional[FormField] = None
        self.field_hora: Optional[FormField] = None
        self.text_descripcion: Optional[SmartText] = None
        self.char_counter: Optional[tb.Label] = None
        
        title = "Editar Evento" if self.is_editing else "Agregar Nuevo Evento"
        super().__init__(parent, title, width=520, height=480)
    
    def _create_interface(self) -> None:
        """Crea la interfaz moderna del diálogo."""
        main_frame = tb.Frame(self.window, padding=DialogConstants.MAIN_PADDING)
        main_frame.pack(fill=BOTH, expand=True)
        
        self._create_header(main_frame)
        self._create_form(main_frame)
        self._create_buttons(main_frame)
        self._set_initial_focus()
    
    def _create_header(self, parent) -> None:
        """Crea el header del diálogo."""
        icon = "✏️" if self.is_editing else "➕"
        subtitle = "Modificar evento existente" if self.is_editing else "Crear un nuevo evento"
        
        header = DialogHeader(parent, self.title, subtitle, icon)
        header.pack(fill=X, pady=(0, 20))
    
    def _create_form(self, parent) -> None:
        """Crea el formulario de evento."""
        form_frame = tb.Frame(parent)
        form_frame.pack(fill=BOTH, expand=True)
        
        # Campo Título
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
        
        # Campos fecha y hora
        datetime_frame = tb.Frame(form_frame)
        datetime_frame.pack(fill=X, pady=(0, 15))
        
        # Fecha
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
        
        # Botón "Hoy"
        btn_hoy = tb.Button(
            fecha_frame,
            text="Hoy",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._set_today,
            width=8
        )
        btn_hoy.pack(pady=(5, 0))
        
        # Hora
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
        
        # Descripción
        desc_frame = tb.Frame(form_frame)
        desc_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
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
        
        # Text widget
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
        
        scrollbar = tb.Scrollbar(text_frame, orient=VERTICAL, command=self.text_descripcion.yview)
        self.text_descripcion.configure(yscrollcommand=scrollbar.set)
        
        self.text_descripcion.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Cargar datos si estamos editando
        if self.is_editing:
            self._load_event_data()
    
    def _create_buttons(self, parent) -> None:
        """Crea los botones del diálogo."""
        # Crear frame para botones con separador
        separator = tb.Separator(parent, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(15, 10))
        
        button_frame = tb.Frame(parent)
        button_frame.pack(fill=X, pady=(0, 10))
        
        # Crear botones manualmente para asegurar visibilidad
        accept_text = "Actualizar" if self.is_editing else "Guardar"
        
        # Botón Cancelar (izquierda)
        btn_cancel = tb.Button(
            button_frame,
            text="Cancelar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._on_cancel,
            width=12
        )
        btn_cancel.pack(side=LEFT)
        
        # Botón Guardar/Actualizar (derecha)
        btn_accept = tb.Button(
            button_frame,
            text=accept_text,
            bootstyle=SUCCESS,
            command=self._on_accept,
            width=12
        )
        btn_accept.pack(side=RIGHT)
        
        # Configurar bindings de teclado
        self.window.bind('<Return>', lambda e: self._on_accept())
        self.window.bind('<Escape>', lambda e: self._on_cancel())
    
    def _set_today(self) -> None:
        """Establece la fecha de hoy."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.field_fecha.set_value(today)
    
    def _load_event_data(self) -> None:
        """Carga los datos del evento para edición."""
        if self.evento:
            # Verificar si self.evento es un objeto válido o string
            if hasattr(self.evento, 'titulo'):
                self.field_titulo.set_value(self.evento.titulo)
                self.field_fecha.set_value(self.evento.fecha)
                if hasattr(self.evento, 'hora') and self.evento.hora:
                    self.field_hora.set_value(self.evento.hora)
                if hasattr(self.evento, 'descripcion') and self.evento.descripcion:
                    self.text_descripcion.delete("1.0", END)
                    self.text_descripcion.insert("1.0", self.evento.descripcion)
            else:
                # Si self.evento es string u otro tipo, registrar error
                self.logger.error(f"Evento inválido recibido: {type(self.evento)} - {self.evento}")
                self.evento = None  # Reset para evitar más errores
    
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
        
        # Validar hora si se proporciona
        if self.field_hora.get_value() and not self.field_hora.is_valid():
            errors.append(self.field_hora.get_validation_error())
        
        # Validar descripción
        descripcion = self.text_descripcion.get_clean_text()
        if len(descripcion) > 500:
            errors.append("La descripción no puede exceder 500 caracteres")
        
        if errors:
            error_message = "Se encontraron errores:\n\n" + "\n".join(f"• {error}" for error in errors)
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