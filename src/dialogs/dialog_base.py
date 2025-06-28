"""
Dialog_Base.py - Clase base abstracta para diálogos modales

Este módulo implementa:
- Patrón Template Method para diálogos modales
- Gestión centralizada de ventanas modales
- Validación y manejo de errores unificado
- Logging y debugging integrado
- Gestión de recursos optimizada

Arquitectura basada en principios SOLID:
- Single Responsibility: Cada método tiene una responsabilidad específica
- Open/Closed: Extensible sin modificar código base
- Liskov Substitution: Clases derivadas completamente intercambiables
- Interface Segregation: Interfaces específicas por funcionalidad
- Dependency Inversion: Dependencias inyectadas, no hardcodeadas

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable, Tuple
import logging
from datetime import datetime
import weakref


class DialogException(Exception):
    """Excepción específica para errores en diálogos."""
    pass


class DialogConstants:
    """Constantes para configuración de diálogos."""
    
    # Tamaños por defecto
    DEFAULT_WIDTH = 500
    DEFAULT_HEIGHT = 450
    MIN_WIDTH = 400
    MIN_HEIGHT = 300
    
    # Espaciado y padding
    MAIN_PADDING = 20
    BUTTON_PADDING = 10
    SEPARATOR_PADDING = 15
    
    # Configuración de botones
    BUTTON_WIDTH = 12
    BUTTON_HEIGHT = 2
    
    # Timeouts
    DIALOG_TIMEOUT = 30000  # 30 segundos
    
    # Logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DialogLogger:
    """Logger especializado para diálogos."""
    
    def __init__(self, dialog_name: str):
        self.logger = logging.getLogger(f"Dialog.{dialog_name}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(DialogConstants.LOG_FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str) -> None:
        """Log información."""
        self.logger.info(message)
    
    def error(self, message: str, exception: Exception = None) -> None:
        """Log error."""
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
        else:
            self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log debug."""
        self.logger.debug(message)


class DialogValidator:
    """Validador centralizado para diálogos."""
    
    @staticmethod
    def validate_not_empty(value: str, field_name: str) -> None:
        """Valida que un campo no esté vacío."""
        if not value or not value.strip():
            raise DialogException(f"El campo '{field_name}' es obligatorio")
    
    @staticmethod
    def validate_date_format(date_str: str) -> None:
        """Valida formato de fecha."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise DialogException("Formato de fecha inválido. Use YYYY-MM-DD")
    
    @staticmethod
    def validate_time_format(time_str: str) -> None:
        """Valida formato de hora."""
        if time_str:  # Solo validar si se proporciona
            try:
                datetime.strptime(time_str, "%H:%M")
            except ValueError:
                raise DialogException("Formato de hora inválido. Use HH:MM")
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, min_len: int = 1, max_len: int = 255) -> None:
        """Valida longitud de string."""
        if len(value) < min_len:
            raise DialogException(f"'{field_name}' debe tener al menos {min_len} caracteres")
        if len(value) > max_len:
            raise DialogException(f"'{field_name}' no puede exceder {max_len} caracteres")


class DialogState:
    """Maneja el estado del diálogo."""
    
    def __init__(self):
        self.is_initialized = False
        self.is_shown = False
        self.is_destroyed = False
        self.result = None
        self.created_at = datetime.now()
    
    def can_show(self) -> bool:
        """Verifica si el diálogo puede mostrarse."""
        return self.is_initialized and not self.is_destroyed
    
    def mark_shown(self) -> None:
        """Marca el diálogo como mostrado."""
        self.is_shown = True
    
    def mark_destroyed(self) -> None:
        """Marca el diálogo como destruido."""
        self.is_destroyed = True


class BaseDialog(ABC):
    """
    Clase base abstracta para todos los diálogos modales.
    
    Implementa el patrón Template Method para estandarizar
    la creación y gestión de diálogos modales.
    """
    
    # Registry de diálogos activos para gestión de memoria
    _active_dialogs = weakref.WeakSet()
    
    def __init__(self, parent, title: str, width: int = None, height: int = None):
        """
        Inicializa el diálogo base.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            width: Ancho personalizado
            height: Alto personalizado
        """
        self.parent = parent
        self.title = title
        self.width = width or DialogConstants.DEFAULT_WIDTH
        self.height = height or DialogConstants.DEFAULT_HEIGHT
        
        # Estado del diálogo
        self.state = DialogState()
        
        # Logger específico
        self.logger = DialogLogger(self.__class__.__name__)
        
        # Validator
        self.validator = DialogValidator()
        
        # Variables de control
        self.window: Optional[tb.Toplevel] = None
        self.callbacks: Dict[str, Callable] = {}
        
        # Registrar diálogo activo
        BaseDialog._active_dialogs.add(self)
        
        self.logger.info(f"Inicializando diálogo: {title}")
        
        try:
            self._initialize_dialog()
            self.state.is_initialized = True
        except Exception as e:
            self.logger.error("Error inicializando diálogo", e)
            raise DialogException(f"Error inicializando diálogo: {str(e)}")
    
    def _initialize_dialog(self) -> None:
        """Inicializa el diálogo siguiendo el patrón Template Method."""
        self._create_window()
        self._configure_window()
        self._create_interface()
        self._configure_bindings()
        self._post_initialization()
    
    def _create_window(self) -> None:
        """Crea la ventana modal."""
        self.window = tb.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry(f"{self.width}x{self.height}")
        
        # Configuración modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Gestión de cierre
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _configure_window(self) -> None:
        """Configura propiedades de la ventana."""
        # Redimensionamiento
        self.window.resizable(True, True)
        self.window.minsize(DialogConstants.MIN_WIDTH, DialogConstants.MIN_HEIGHT)
        
        # Centrar ventana
        self._center_window()
        
        # Configurar expansión
        self._configure_grid_weights()
    
    def _center_window(self) -> None:
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Asegurar que la ventana esté visible
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        self.logger.debug(f"Ventana centrada en: {x}x{y}")
    
    def _configure_grid_weights(self) -> None:
        """Configura los pesos de grid para expansión."""
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    
    @abstractmethod
    def _create_interface(self) -> None:
        """Crea la interfaz específica del diálogo. Debe ser implementado por subclases."""
        pass
    
    def _configure_bindings(self) -> None:
        """Configura bindings de teclado estándar."""
        self.window.bind('<Escape>', lambda e: self._on_cancel())
        self.window.bind('<Return>', lambda e: self._on_accept())
        self.window.bind('<Control-s>', lambda e: self._on_accept())
    
    def _post_initialization(self) -> None:
        """Operaciones post-inicialización."""
        self.logger.info("Diálogo inicializado correctamente")
    
    def _create_button_frame(self, parent, separator: bool = True) -> tb.Frame:
        """
        Crea frame estándar para botones.
        
        Args:
            parent: Widget padre
            separator: Si agregar separador visual
            
        Returns:
            Frame configurado para botones
        """
        if separator:
            sep = tb.Separator(parent, orient=HORIZONTAL)
            sep.pack(fill=X, pady=(DialogConstants.SEPARATOR_PADDING, DialogConstants.BUTTON_PADDING))
        
        button_frame = tb.Frame(parent)
        button_frame.pack(fill=X, pady=(0, DialogConstants.BUTTON_PADDING))
        
        return button_frame
    
    def _create_standard_buttons(self, parent_frame: tb.Frame, 
                                accept_text: str = "Aceptar", 
                                cancel_text: str = "Cancelar") -> Tuple[tb.Button, tb.Button]:
        """
        Crea botones estándar de aceptar/cancelar.
        
        Args:
            parent_frame: Frame contenedor
            accept_text: Texto del botón aceptar
            cancel_text: Texto del botón cancelar
            
        Returns:
            Tupla con (botón_aceptar, botón_cancelar)
        """
        # Botón Aceptar
        btn_accept = tb.Button(
            parent_frame,
            text=accept_text,
            bootstyle=SUCCESS,
            command=self._on_accept,
            width=DialogConstants.BUTTON_WIDTH
        )
        btn_accept.pack(side=RIGHT, padx=(5, 0))
        
        # Botón Cancelar
        btn_cancel = tb.Button(
            parent_frame,
            text=cancel_text,
            bootstyle=(OUTLINE, SECONDARY),
            command=self._on_cancel,
            width=DialogConstants.BUTTON_WIDTH
        )
        btn_cancel.pack(side=RIGHT, padx=(5, 5))
        
        return btn_accept, btn_cancel
    
    def _on_accept(self) -> None:
        """Maneja la aceptación del diálogo."""
        try:
            if self._validate_input():
                result = self._get_result()
                self._set_result(result)
                self._close_dialog()
            # Si la validación falla, el diálogo permanece abierto
        except DialogException as e:
            self._show_validation_error(str(e))
        except Exception as e:
            self.logger.error("Error inesperado en aceptación", e)
            self._show_error("Error inesperado", str(e))
    
    def _on_cancel(self) -> None:
        """Maneja la cancelación del diálogo."""
        self.logger.info("Diálogo cancelado por usuario")
        self._set_result(None)
        self._close_dialog()
    
    def _on_window_close(self) -> None:
        """Maneja el cierre de ventana."""
        self._on_cancel()  # Tratar cierre como cancelación
    
    @abstractmethod
    def _validate_input(self) -> bool:
        """Valida la entrada del usuario. Debe ser implementado por subclases."""
        pass
    
    @abstractmethod
    def _get_result(self) -> Any:
        """Obtiene el resultado del diálogo. Debe ser implementado por subclases."""
        pass
    
    def _set_result(self, result: Any) -> None:
        """Establece el resultado del diálogo."""
        self.state.result = result
    
    def _show_validation_error(self, message: str) -> None:
        """Muestra error de validación."""
        Messagebox.show_error("Error de Validación", message, parent=self.window)
        self.logger.info(f"Error de validación: {message}")
    
    def _show_error(self, title: str, message: str) -> None:
        """Muestra error general."""
        Messagebox.show_error(title, message, parent=self.window)
        self.logger.error(f"{title}: {message}")
    
    def _close_dialog(self) -> None:
        """Cierra el diálogo y libera recursos."""
        if self.window and not self.state.is_destroyed:
            self.logger.info("Cerrando diálogo")
            self.state.mark_destroyed()
            self.window.destroy()
            self._cleanup_resources()
    
    def _cleanup_resources(self) -> None:
        """Limpia recursos del diálogo."""
        # Limpiar callbacks
        self.callbacks.clear()
        
        # Limpiar referencias
        self.window = None
        
        self.logger.info("Recursos del diálogo liberados")
    
    def show(self) -> Any:
        """
        Muestra el diálogo modal y retorna el resultado.
        
        Returns:
            Resultado del diálogo o None si se canceló
        """
        if not self.state.can_show():
            raise DialogException("El diálogo no puede mostrarse en su estado actual")
        
        self.logger.info(f"Mostrando diálogo: {self.title}")
        self.state.mark_shown()
        
        try:
            self.window.wait_window()
            return self.state.result
        except Exception as e:
            self.logger.error("Error mostrando diálogo", e)
            raise DialogException(f"Error mostrando diálogo: {str(e)}")
        finally:
            if not self.state.is_destroyed:
                self._close_dialog()
    
    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Establece callback para eventos específicos.
        
        Args:
            event_name: Nombre del evento
            callback: Función callback
        """
        self.callbacks[event_name] = callback
        self.logger.debug(f"Callback establecido para evento: {event_name}")
    
    def trigger_callback(self, event_name: str, *args, **kwargs) -> None:
        """
        Dispara callback si existe.
        
        Args:
            event_name: Nombre del evento
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre
        """
        if event_name in self.callbacks:
            try:
                self.callbacks[event_name](*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error ejecutando callback {event_name}", e)
    
    @classmethod
    def get_active_dialogs_count(cls) -> int:
        """Retorna el número de diálogos activos."""
        return len(cls._active_dialogs)
    
    @classmethod
    def cleanup_all_dialogs(cls) -> None:
        """Limpia todos los diálogos activos."""
        for dialog in list(cls._active_dialogs):
            if hasattr(dialog, '_close_dialog'):
                dialog._close_dialog() 