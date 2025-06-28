"""
Dialog_Components.py - Componentes reutilizables para diálogos

Este módulo contiene:
- Componentes UI estandarizados para diálogos
- Widgets especializados con validación integrada
- Factory patterns para creación de componentes
- Mixins para funcionalidades específicas

Elimina duplicación de código y asegura consistencia
en todos los diálogos del sistema.

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional, List, Callable, Dict, Any
from datetime import datetime, date
import re


class ValidationMixin:
    """Mixin para agregar capacidades de validación a widgets."""
    
    def __init__(self):
        self.validation_rules: List[Callable] = []
        self.error_message = ""
    
    def add_validation_rule(self, rule: Callable[[str], bool], error_message: str) -> None:
        """Agrega regla de validación."""
        self.validation_rules.append((rule, error_message))
    
    def validate(self, value: str) -> bool:
        """Valida el valor según las reglas establecidas."""
        for rule, message in self.validation_rules:
            if not rule(value):
                self.error_message = message
                return False
        self.error_message = ""
        return True
    
    def get_validation_error(self) -> str:
        """Retorna el último mensaje de error de validación."""
        return self.error_message


class SmartEntry(tb.Entry, ValidationMixin):
    """Entry con validación integrada y feedback visual."""
    
    def __init__(self, parent, placeholder: str = "", validation_type: str = "text", **kwargs):
        """
        Inicializa SmartEntry.
        
        Args:
            parent: Widget padre
            placeholder: Texto placeholder
            validation_type: Tipo de validación ('text', 'email', 'date', 'time')
            **kwargs: Argumentos adicionales para Entry
        """
        super().__init__(parent, **kwargs)
        ValidationMixin.__init__(self)
        
        self.placeholder = placeholder
        self.validation_type = validation_type
        self.original_bootstyle = kwargs.get('bootstyle', PRIMARY)
        
        self._setup_placeholder()
        self._setup_validation()
        self._setup_bindings()
    
    def _setup_placeholder(self) -> None:
        """Configura placeholder."""
        if self.placeholder:
            self.insert(0, self.placeholder)
            self.configure(bootstyle=(SECONDARY,))
            self._placeholder_active = True
        else:
            self._placeholder_active = False
    
    def _setup_validation(self) -> None:
        """Configura validación según el tipo."""
        if self.validation_type == "email":
            self.add_validation_rule(
                lambda x: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x) is not None,
                "Formato de email inválido"
            )
        elif self.validation_type == "date":
            self.add_validation_rule(
                lambda x: self._validate_date(x),
                "Formato de fecha inválido (YYYY-MM-DD)"
            )
        elif self.validation_type == "time":
            self.add_validation_rule(
                lambda x: self._validate_time(x),
                "Formato de hora inválido (HH:MM)"
            )
    
    def _validate_date(self, value: str) -> bool:
        """Valida formato de fecha."""
        if not value:
            return True  # Permitir vacío si no es requerido
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _validate_time(self, value: str) -> bool:
        """Valida formato de hora."""
        if not value:
            return True  # Permitir vacío
        try:
            datetime.strptime(value, "%H:%M")
            return True
        except ValueError:
            return False
    
    def _setup_bindings(self) -> None:
        """Configura bindings de eventos."""
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<KeyRelease>', self._on_key_release)
    
    def _on_focus_in(self, event) -> None:
        """Maneja focus in."""
        if self._placeholder_active:
            self.delete(0, END)
            self.configure(bootstyle=self.original_bootstyle)
            self._placeholder_active = False
    
    def _on_focus_out(self, event) -> None:
        """Maneja focus out."""
        value = self.get()
        if not value and self.placeholder:
            self.insert(0, self.placeholder)
            self.configure(bootstyle=(SECONDARY,))
            self._placeholder_active = True
        else:
            self._validate_and_update_style()
    
    def _on_key_release(self, event) -> None:
        """Maneja key release para validación en tiempo real."""
        if not self._placeholder_active:
            self._validate_and_update_style()
    
    def _validate_and_update_style(self) -> None:
        """Valida y actualiza estilo visual."""
        value = self.get()
        if value and not self.validate(value):
            self.configure(bootstyle=DANGER)
        else:
            self.configure(bootstyle=self.original_bootstyle)
    
    def get_real_value(self) -> str:
        """Retorna el valor real (sin placeholder)."""
        if self._placeholder_active:
            return ""
        return self.get()
    
    def is_valid(self) -> bool:
        """Verifica si el valor actual es válido."""
        value = self.get_real_value()
        return self.validate(value) if value else True


class SmartText(tb.Text):
    """Text widget con características avanzadas."""
    
    def __init__(self, parent, max_chars: Optional[int] = None, **kwargs):
        """
        Inicializa SmartText.
        
        Args:
            parent: Widget padre
            max_chars: Límite máximo de caracteres
            **kwargs: Argumentos adicionales para Text
        """
        super().__init__(parent, **kwargs)
        
        self.max_chars = max_chars
        self.char_count_label: Optional[tb.Label] = None
        
        if max_chars:
            self._setup_char_counter()
        
        self._setup_bindings()
    
    def _setup_char_counter(self) -> None:
        """Configura contador de caracteres."""
        self.bind('<KeyRelease>', self._update_char_count)
        self.bind('<Button-1>', self._update_char_count)
    
    def _setup_bindings(self) -> None:
        """Configura bindings adicionales."""
        # Binding para paste
        self.bind('<Control-v>', self._on_paste)
    
    def _update_char_count(self, event=None) -> None:
        """Actualiza contador de caracteres."""
        if self.char_count_label and self.max_chars:
            current_chars = len(self.get("1.0", "end-1c"))
            remaining = max(0, self.max_chars - current_chars)
            
            self.char_count_label.config(text=f"{current_chars}/{self.max_chars}")
            
            if remaining < 50:
                self.char_count_label.configure(bootstyle=WARNING)
            elif remaining == 0:
                self.char_count_label.configure(bootstyle=DANGER)
            else:
                self.char_count_label.configure(bootstyle=SECONDARY)
    
    def _on_paste(self, event) -> None:
        """Maneja pegado respetando límite de caracteres."""
        if self.max_chars:
            try:
                clipboard_text = self.clipboard_get()
                current_text = self.get("1.0", "end-1c")
                cursor_pos = self.index(INSERT)
                
                # Calcular espacio disponible
                available_space = self.max_chars - len(current_text)
                
                if available_space > 0:
                    truncated_text = clipboard_text[:available_space]
                    self.insert(cursor_pos, truncated_text)
                
                return "break"  # Prevenir comportamiento por defecto
            except:
                pass  # Clipboard vacío o error
    
    def set_char_counter_label(self, label: tb.Label) -> None:
        """Establece label para mostrar contador de caracteres."""
        self.char_count_label = label
        self._update_char_count()
    
    def get_clean_text(self) -> str:
        """Retorna texto limpio sin espacios extra."""
        return self.get("1.0", "end-1c").strip()


class TreeviewComponent:
    """Componente reutilizable para Treeview con funcionalidades estándar."""
    
    def __init__(self, parent, columns: Dict[str, Dict], height: int = 12):
        """
        Inicializa TreeviewComponent.
        
        Args:
            parent: Widget padre
            columns: Configuración de columnas {'id': {'text': 'Título', 'width': 100}}
            height: Altura del Treeview
        """
        self.parent = parent
        self.columns = columns
        self.height = height
        
        self.frame: Optional[tb.Frame] = None
        self.tree: Optional[tb.Treeview] = None
        self.scrollbar: Optional[tb.Scrollbar] = None
        
        self._create_component()
    
    def _create_component(self) -> None:
        """Crea el componente Treeview."""
        # Frame contenedor
        self.frame = tb.Frame(self.parent)
        
        # Crear Treeview
        column_ids = list(self.columns.keys())
        self.tree = tb.Treeview(
            self.frame,
            columns=column_ids,
            show='headings',
            height=self.height
        )
        
        # Configurar columnas
        for col_id, config in self.columns.items():
            self.tree.heading(col_id, text=config.get('text', col_id))
            self.tree.column(
                col_id,
                width=config.get('width', 100),
                minwidth=config.get('minwidth', 50),
                anchor=config.get('anchor', W)
            )
        
        # Scrollbar
        self.scrollbar = tb.Scrollbar(
            self.frame,
            orient=VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)
    
    def pack(self, **kwargs) -> None:
        """Pack del frame contenedor."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid del frame contenedor."""
        self.frame.grid(**kwargs)
    
    def clear(self) -> None:
        """Limpia el Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_item(self, values: List[str], tags: List[str] = None) -> str:
        """
        Agrega un item al Treeview.
        
        Args:
            values: Valores para las columnas
            tags: Tags del item
            
        Returns:
            ID del item creado
        """
        return self.tree.insert('', 'end', values=values, tags=tags or [])
    
    def get_selected_item(self) -> Optional[str]:
        """Retorna el item seleccionado."""
        selection = self.tree.selection()
        return selection[0] if selection else None
    
    def get_item_values(self, item_id: str) -> List[str]:
        """Retorna los valores de un item."""
        return self.tree.item(item_id)['values']
    
    def get_item_tags(self, item_id: str) -> List[str]:
        """Retorna los tags de un item."""
        return self.tree.item(item_id)['tags']
    
    def bind_double_click(self, callback: Callable) -> None:
        """Bind para doble click."""
        self.tree.bind('<Double-1>', callback)
    
    def bind_right_click(self, callback: Callable) -> None:
        """Bind para click derecho."""
        self.tree.bind('<Button-3>', callback)


class DialogHeader:
    """Componente para headers de diálogos."""
    
    def __init__(self, parent, title: str, subtitle: str = "", icon: str = ""):
        """
        Inicializa DialogHeader.
        
        Args:
            parent: Widget padre
            title: Título principal
            subtitle: Subtítulo opcional
            icon: Icono/emoji opcional
        """
        self.parent = parent
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        
        self.frame: Optional[tb.Frame] = None
        self._create_header()
    
    def _create_header(self) -> None:
        """Crea el header."""
        self.frame = tb.Frame(self.parent)
        
        # Título principal
        title_text = f"{self.icon} {self.title}" if self.icon else self.title
        title_label = tb.Label(
            self.frame,
            text=title_text,
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor=W)
        
        # Subtítulo si existe
        if self.subtitle:
            subtitle_label = tb.Label(
                self.frame,
                text=self.subtitle,
                font=("Arial", 10),
                bootstyle=SECONDARY
            )
            subtitle_label.pack(anchor=W, pady=(2, 0))
    
    def pack(self, **kwargs) -> None:
        """Pack del frame contenedor."""
        self.frame.pack(**kwargs)
    
    def update_title(self, new_title: str) -> None:
        """Actualiza el título."""
        self.title = new_title
        # Reconfigurar header
        for widget in self.frame.winfo_children():
            widget.destroy()
        self._create_header()


class FormField:
    """Componente para campos de formulario estandarizados."""
    
    def __init__(self, parent, label: str, field_type: str = "entry", 
                 required: bool = False, **kwargs):
        """
        Inicializa FormField.
        
        Args:
            parent: Widget padre
            label: Etiqueta del campo
            field_type: Tipo de campo ('entry', 'text', 'combobox')
            required: Si el campo es requerido
            **kwargs: Argumentos adicionales para el widget
        """
        self.parent = parent
        self.label = label
        self.field_type = field_type
        self.required = required
        self.kwargs = kwargs
        
        self.frame: Optional[tb.Frame] = None
        self.label_widget: Optional[tb.Label] = None
        self.input_widget = None
        
        self._create_field()
    
    def _create_field(self) -> None:
        """Crea el campo de formulario."""
        self.frame = tb.Frame(self.parent)
        
        # Label
        label_text = f"{self.label} *" if self.required else self.label
        self.label_widget = tb.Label(
            self.frame,
            text=label_text,
            font=("Arial", 10, "bold")
        )
        self.label_widget.pack(anchor=W)
        
        # Input widget según tipo
        if self.field_type == "entry":
            self.input_widget = SmartEntry(self.frame, **self.kwargs)
        elif self.field_type == "text":
            self.input_widget = SmartText(self.frame, **self.kwargs)
        elif self.field_type == "combobox":
            self.input_widget = tb.Combobox(self.frame, **self.kwargs)
        
        if self.input_widget:
            if self.field_type == "text":
                self.input_widget.pack(fill=BOTH, expand=True, pady=(5, 0))
            else:
                self.input_widget.pack(fill=X, pady=(5, 0))
    
    def pack(self, **kwargs) -> None:
        """Pack del frame contenedor."""
        self.frame.pack(**kwargs)
    
    def get_value(self) -> str:
        """Retorna el valor del campo."""
        if hasattr(self.input_widget, 'get_real_value'):
            return self.input_widget.get_real_value()
        elif hasattr(self.input_widget, 'get_clean_text'):
            return self.input_widget.get_clean_text()
        elif hasattr(self.input_widget, 'get'):
            return self.input_widget.get()
        return ""
    
    def set_value(self, value: str) -> None:
        """Establece el valor del campo."""
        if hasattr(self.input_widget, 'delete') and hasattr(self.input_widget, 'insert'):
            self.input_widget.delete(0, END)
            self.input_widget.insert(0, value)
        elif hasattr(self.input_widget, 'delete') and hasattr(self.input_widget, 'insert'):
            self.input_widget.delete("1.0", END)
            self.input_widget.insert("1.0", value)
    
    def is_valid(self) -> bool:
        """Verifica si el campo es válido."""
        value = self.get_value()
        
        if self.required and not value:
            return False
        
        if hasattr(self.input_widget, 'is_valid'):
            return self.input_widget.is_valid()
        
        return True
    
    def get_validation_error(self) -> str:
        """Retorna error de validación si existe."""
        if not self.is_valid():
            if self.required and not self.get_value():
                return f"El campo '{self.label}' es obligatorio"
            elif hasattr(self.input_widget, 'get_validation_error'):
                return self.input_widget.get_validation_error()
        return "" 