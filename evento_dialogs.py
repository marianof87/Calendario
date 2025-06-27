"""
Evento_Dialogs.py - Ventanas modales para gestión de eventos

Este módulo se encarga de:
- Ventanas modales para agregar/editar eventos
- Visualización de eventos del día
- Confirmaciones de eliminación
- Validación de formularios
- Interfaz de búsqueda de eventos

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import datetime
from typing import Optional, List, Callable, Tuple
from eventos import Evento, EventosManager
from helpers import formatear_fecha_completa, validar_fecha


class EventoDialog:
    """Ventana modal base para gestión de eventos."""
    
    def __init__(self, parent, title: str, evento: Optional[Evento] = None):
        self.parent = parent
        self.evento = evento
        self.resultado = None
        
        # Crear ventana modal
        self.window = tb.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("500x450")
        self.window.resizable(True, True)  # Permitir redimensionamiento
        self.window.minsize(450, 400)     # Tamaño mínimo
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables de formulario
        self.var_titulo = tb.StringVar()
        self.var_fecha = tb.StringVar()
        self.var_hora = tb.StringVar()
        
        # Valores por defecto
        if self.evento:
            self._cargar_datos_evento()
        else:
            self.var_fecha.set(datetime.date.today().strftime("%Y-%m-%d"))
        
        self._crear_interfaz()
        
        # Centrar ventana después de crear la interfaz
        self._centrar_ventana()
    
    def _cargar_datos_evento(self) -> None:
        """Carga los datos del evento en el formulario."""
        if self.evento:
            self.var_titulo.set(self.evento.titulo)
            self.var_fecha.set(self.evento.fecha)
            self.var_hora.set(self.evento.hora or "")
    
    def _centrar_ventana(self) -> None:
        """Centra la ventana modal en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_interfaz(self) -> None:
        """Crea la interfaz del formulario."""
        main_frame = tb.Frame(self.window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        titulo_form = "Editar Evento" if self.evento else "Agregar Nuevo Evento"
        tb.Label(main_frame, text=titulo_form, font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Campo título
        frame = tb.Frame(main_frame)
        frame.pack(fill=X, pady=5)
        tb.Label(frame, text="Título *", font=("Arial", 10, "bold")).pack(anchor=W)
        entry = tb.Entry(frame, textvariable=self.var_titulo, font=("Arial", 11), bootstyle=PRIMARY)
        entry.pack(fill=X, pady=(5, 0))
        entry.focus()
        
        # Campo fecha
        frame = tb.Frame(main_frame)
        frame.pack(fill=X, pady=5)
        tb.Label(frame, text="Fecha * (YYYY-MM-DD)", font=("Arial", 10, "bold")).pack(anchor=W)
        fecha_frame = tb.Frame(frame)
        fecha_frame.pack(fill=X, pady=(5, 0))
        tb.Entry(fecha_frame, textvariable=self.var_fecha, font=("Arial", 11), bootstyle=INFO, width=12).pack(side=LEFT)
        tb.Button(fecha_frame, text="Hoy", bootstyle=(OUTLINE, SECONDARY), 
                 command=lambda: self.var_fecha.set(datetime.date.today().strftime("%Y-%m-%d"))).pack(side=LEFT, padx=(10, 0))
        
        # Campo hora
        frame = tb.Frame(main_frame)
        frame.pack(fill=X, pady=5)
        tb.Label(frame, text="Hora (HH:MM) - Opcional", font=("Arial", 10, "bold")).pack(anchor=W)
        hora_frame = tb.Frame(frame)
        hora_frame.pack(fill=X, pady=(5, 0))
        tb.Entry(hora_frame, textvariable=self.var_hora, font=("Arial", 11), bootstyle=SUCCESS, width=8).pack(side=LEFT)
        tb.Label(hora_frame, text="Ej: 14:30, 09:00", font=("Arial", 9), bootstyle=(SECONDARY,)).pack(side=LEFT, padx=(10, 0))
        
        # Campo descripción
        frame = tb.Frame(main_frame)
        frame.pack(fill=BOTH, expand=True, pady=5)
        tb.Label(frame, text="Descripción - Opcional", font=("Arial", 10, "bold")).pack(anchor=W)
        
        # Frame para text widget con scrollbar
        text_frame = tb.Frame(frame)
        text_frame.pack(fill=BOTH, expand=True, pady=(5, 0))
        
        self.text_descripcion = tb.Text(text_frame, height=5, font=("Arial", 10), wrap=WORD)
        
        # Scrollbar para descripción
        scrollbar_desc = tb.Scrollbar(text_frame, orient=VERTICAL, command=self.text_descripcion.yview)
        self.text_descripcion.configure(yscrollcommand=scrollbar_desc.set)
        
        self.text_descripcion.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_desc.pack(side=RIGHT, fill=Y)
        
        if self.evento and self.evento.descripcion:
            self.text_descripcion.insert("1.0", self.evento.descripcion)
        
        # Separador visual
        separator = tb.Separator(main_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(15, 10))
        
        # Frame para botones con mejor espaciado
        buttons_frame = tb.Frame(main_frame)
        buttons_frame.pack(fill=X, pady=(0, 10))
        
        # Botón Guardar (a la derecha)
        texto_guardar = "Actualizar" if self.evento else "Guardar"
        btn_guardar = tb.Button(
            buttons_frame, 
            text=texto_guardar, 
            bootstyle=SUCCESS, 
            command=self._guardar,
            width=12
        )
        btn_guardar.pack(side=RIGHT, padx=(5, 0))
        
        # Botón Cancelar (a la derecha del Guardar)
        btn_cancelar = tb.Button(
            buttons_frame, 
            text="Cancelar", 
            bootstyle=(OUTLINE, SECONDARY), 
            command=self._cancelar,
            width=12
        )
        btn_cancelar.pack(side=RIGHT, padx=(5, 5))
    
    def _guardar(self) -> None:
        """Guarda el evento."""
        # Validaciones
        titulo = self.var_titulo.get().strip()
        if not titulo:
            Messagebox.show_error("Error", "El título del evento es obligatorio", parent=self.window)
            return
        
        fecha_str = self.var_fecha.get().strip()
        if not fecha_str:
            Messagebox.show_error("Error", "La fecha es obligatoria", parent=self.window)
            return
        
        try:
            datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Error", "Formato de fecha inválido. Use YYYY-MM-DD", parent=self.window)
            return
        
        hora_str = self.var_hora.get().strip()
        if hora_str:
            try:
                datetime.datetime.strptime(hora_str, "%H:%M")
            except ValueError:
                Messagebox.show_error("Error", "Formato de hora inválido. Use HH:MM", parent=self.window)
                return
        
        descripcion = self.text_descripcion.get("1.0", "end-1c").strip()
        
        self.resultado = {
            'titulo': titulo,
            'fecha': fecha_str,
            'hora': hora_str or None,
            'descripcion': descripcion if descripcion else None
        }
        self.window.destroy()
    
    def _cancelar(self) -> None:
        """Cancela el diálogo."""
        self.resultado = None
        self.window.destroy()
    
    def mostrar(self) -> Optional[dict]:
        """Muestra el diálogo modal."""
        self.window.wait_window()
        return self.resultado


class EventosDelDiaDialog:
    """
    Ventana modal para mostrar eventos de un día específico.
    """
    
    def __init__(self, parent, fecha: datetime.date, eventos_manager: EventosManager):
        """
        Inicializa la ventana de eventos del día.
        
        Args:
            parent: Ventana padre
            fecha: Fecha para mostrar eventos
            eventos_manager: Gestor de eventos
        """
        self.parent = parent
        self.fecha = fecha
        self.eventos_manager = eventos_manager
        self.callback_actualizar = None
        
        # Crear ventana modal
        self.window = tb.Toplevel(parent)
        self.window.title(f"Eventos del {formatear_fecha_completa(fecha)}")
        self.window.geometry("600x550")
        self.window.resizable(True, True)
        self.window.minsize(500, 400)  # Tamaño mínimo
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrar ventana
        self._centrar_ventana()
        
        self._crear_interfaz()
        self._actualizar_lista_eventos()
    
    def _centrar_ventana(self) -> None:
        """Centra la ventana modal en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_interfaz(self) -> None:
        """Crea la interfaz de la ventana."""
        # Frame principal
        main_frame = tb.Frame(self.window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Encabezado
        self._crear_encabezado(main_frame)
        
        # Botones de acción
        self._crear_botones_accion(main_frame)
        
        # Lista de eventos
        self._crear_lista_eventos(main_frame)
        
        # Botón cerrar
        self._crear_boton_cerrar(main_frame)
    
    def _crear_encabezado(self, parent) -> None:
        """Crea el encabezado de la ventana."""
        header_frame = tb.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 15))
        
        # Título
        tb.Label(
            header_frame,
            text=f"📅 {formatear_fecha_completa(self.fecha)}",
            font=("Arial", 14, "bold")
        ).pack(side=LEFT)
        
        # Contador de eventos
        self.label_contador = tb.Label(
            header_frame,
            text="",
            font=("Arial", 10),
            bootstyle=(INFO,)
        )
        self.label_contador.pack(side=RIGHT)
    
    def _crear_botones_accion(self, parent) -> None:
        """Crea los botones de acción."""
        buttons_frame = tb.Frame(parent)
        buttons_frame.pack(fill=X, pady=(0, 10))
        
        # Botón Agregar Evento
        tb.Button(
            buttons_frame,
            text="➕ Agregar Evento",
            bootstyle=SUCCESS,
            command=self._agregar_evento
        ).pack(side=LEFT)
        
        # Botón Actualizar
        tb.Button(
            buttons_frame,
            text="🔄 Actualizar",
            bootstyle=(OUTLINE, INFO),
            command=self._actualizar_lista_eventos
        ).pack(side=LEFT, padx=(10, 0))
    
    def _crear_lista_eventos(self, parent) -> None:
        """Crea la lista de eventos."""
        # Frame con scroll
        list_frame = tb.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Crear Treeview
        columns = ('hora', 'titulo', 'descripcion')
        self.tree_eventos = tb.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12
        )
        
        # Configurar columnas
        self.tree_eventos.heading('hora', text='Hora')
        self.tree_eventos.heading('titulo', text='Título')
        self.tree_eventos.heading('descripcion', text='Descripción')
        
        self.tree_eventos.column('hora', width=80, minwidth=60)
        self.tree_eventos.column('titulo', width=200, minwidth=150)
        self.tree_eventos.column('descripcion', width=300, minwidth=200)
        
        # Scrollbar
        scrollbar = tb.Scrollbar(list_frame, orient=VERTICAL, command=self.tree_eventos.yview)
        self.tree_eventos.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree_eventos.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind eventos
        self.tree_eventos.bind('<Double-1>', self._editar_evento_seleccionado)
        self.tree_eventos.bind('<Button-3>', self._mostrar_menu_contextual)
    
    def _crear_boton_cerrar(self, parent) -> None:
        """Crea el botón para cerrar la ventana."""
        # Separador visual
        separator = tb.Separator(parent, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(5, 10))
        
        # Frame para botón cerrar
        button_frame = tb.Frame(parent)
        button_frame.pack(fill=X)
        
        tb.Button(
            button_frame,
            text="Cerrar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._cerrar,
            width=12
        ).pack(side=RIGHT, pady=5)
    
    def _actualizar_lista_eventos(self) -> None:
        """Actualizar la lista de eventos."""
        # Limpiar árbol
        for item in self.tree_eventos.get_children():
            self.tree_eventos.delete(item)
        
        # Obtener eventos del día
        eventos = self.eventos_manager.obtener_eventos_fecha(self.fecha)
        
        # Agregar eventos al árbol
        for evento in eventos:
            hora_display = evento.hora or "Todo el día"
            descripcion_display = (evento.descripcion[:50] + "...") if evento.descripcion and len(evento.descripcion) > 50 else (evento.descripcion or "")
            
            self.tree_eventos.insert(
                '',
                'end',
                values=(hora_display, evento.titulo, descripcion_display),
                tags=(evento.id,)
            )
        
        # Actualizar contador
        self.label_contador.config(text=f"{len(eventos)} evento(s)")
    
    def _agregar_evento(self) -> None:
        """Abre el diálogo para agregar un nuevo evento."""
        dialog = EventoDialog(self.window, "Agregar Evento")
        
        # Pre-establecer la fecha
        dialog.var_fecha.set(self.fecha.strftime("%Y-%m-%d"))
        
        resultado = dialog.mostrar()
        if resultado:
            # Agregar evento
            exito, mensaje, evento = self.eventos_manager.agregar_evento(
                titulo=resultado['titulo'],
                fecha=resultado['fecha'],
                hora=resultado['hora'],
                descripcion=resultado['descripcion']
            )
            
            if exito:
                Messagebox.show_info("Éxito", mensaje, parent=self.window)
                self._actualizar_lista_eventos()
                if self.callback_actualizar:
                    self.callback_actualizar()
            else:
                Messagebox.show_error("Error", mensaje, parent=self.window)
    
    def _editar_evento_seleccionado(self, event=None) -> None:
        """Edita el evento seleccionado."""
        selection = self.tree_eventos.selection()
        if not selection:
            return
        
        # Obtener ID del evento
        item = selection[0]
        tags = self.tree_eventos.item(item)['tags']
        if not tags:
            return
        
        evento_id = tags[0]
        evento = self.eventos_manager.buscar_evento_por_id(evento_id)
        
        if evento:
            dialog = EventoDialog(self.window, "Editar Evento", evento)
            resultado = dialog.mostrar()
            
            if resultado:
                # Actualizar evento
                # Primero eliminar el evento actual
                self.eventos_manager.eliminar_evento(evento_id)
                
                # Crear evento actualizado (manteniendo ID original)
                evento_actualizado = Evento(
                    id=evento_id,
                    titulo=resultado['titulo'],
                    fecha=resultado['fecha'],
                    hora=resultado['hora'],
                    descripcion=resultado['descripcion']
                )
                
                # Agregar evento actualizado
                self.eventos_manager.eventos.append(evento_actualizado)
                self.eventos_manager.guardar_eventos()
                
                Messagebox.show_info("Éxito", "Evento actualizado correctamente", parent=self.window)
                self._actualizar_lista_eventos()
                if self.callback_actualizar:
                    self.callback_actualizar()
    
    def _mostrar_menu_contextual(self, event) -> None:
        """Muestra el menú contextual para eventos."""
        selection = self.tree_eventos.selection()
        if not selection:
            return
        
        # Crear menú contextual
        menu = tb.Menu(self.window, tearoff=0)
        menu.add_command(label="✏️ Editar", command=self._editar_evento_seleccionado)
        menu.add_command(label="🗑️ Eliminar", command=self._eliminar_evento_seleccionado)
        
        # Mostrar menú en la posición del mouse
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _eliminar_evento_seleccionado(self) -> None:
        """Elimina el evento seleccionado."""
        selection = self.tree_eventos.selection()
        if not selection:
            return
        
        # Obtener ID del evento
        item = selection[0]
        tags = self.tree_eventos.item(item)['tags']
        if not tags:
            return
        
        evento_id = tags[0]
        evento = self.eventos_manager.buscar_evento_por_id(evento_id)
        
        if evento:
            # Confirmar eliminación
            resultado = Messagebox.show_question(
                "Confirmar Eliminación",
                f"¿Está seguro que desea eliminar el evento:\n\n'{evento.titulo}'?\n\nEsta acción no se puede deshacer.",
                parent=self.window
            )
            
            if resultado == "Yes":
                exito, mensaje = self.eventos_manager.eliminar_evento(evento_id)
                if exito:
                    Messagebox.show_info("Éxito", mensaje, parent=self.window)
                    self._actualizar_lista_eventos()
                    if self.callback_actualizar:
                        self.callback_actualizar()
                else:
                    Messagebox.show_error("Error", mensaje, parent=self.window)
    
    def _cerrar(self) -> None:
        """Cierra la ventana."""
        self.window.destroy()
    
    def set_callback_actualizar(self, callback: Callable) -> None:
        """
        Establece el callback para actualizar la vista principal.
        
        Args:
            callback: Función a llamar cuando se actualicen eventos
        """
        self.callback_actualizar = callback


class BuscarEventosDialog:
    """
    Ventana modal para buscar eventos por nombre.
    """
    
    def __init__(self, parent, eventos_manager: EventosManager):
        """
        Inicializa la ventana de búsqueda.
        
        Args:
            parent: Ventana padre
            eventos_manager: Gestor de eventos
        """
        self.parent = parent
        self.eventos_manager = eventos_manager
        
        # Crear ventana modal
        self.window = tb.Toplevel(parent)
        self.window.title("🔍 Buscar Eventos")
        self.window.geometry("700x550")
        self.window.resizable(True, True)
        self.window.minsize(600, 400)  # Tamaño mínimo
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrar ventana
        self._centrar_ventana()
        
        # Variable de búsqueda
        self.var_busqueda = tb.StringVar()
        self.var_busqueda.trace('w', self._realizar_busqueda)
        
        self._crear_interfaz()
        self._realizar_busqueda()  # Mostrar todos los eventos inicialmente
    
    def _centrar_ventana(self) -> None:
        """Centra la ventana modal en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_interfaz(self) -> None:
        """Crea la interfaz de búsqueda."""
        # Frame principal
        main_frame = tb.Frame(self.window, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Campo de búsqueda
        self._crear_campo_busqueda(main_frame)
        
        # Resultados
        self._crear_area_resultados(main_frame)
        
        # Botón cerrar
        self._crear_boton_cerrar(main_frame)
    
    def _crear_campo_busqueda(self, parent) -> None:
        """Crea el campo de búsqueda."""
        search_frame = tb.Frame(parent)
        search_frame.pack(fill=X, pady=(0, 15))
        
        tb.Label(
            search_frame,
            text="🔍 Buscar eventos:",
            font=("Arial", 12, "bold")
        ).pack(anchor=W, pady=(0, 5))
        
        entry_frame = tb.Frame(search_frame)
        entry_frame.pack(fill=X)
        
        self.entry_busqueda = tb.Entry(
            entry_frame,
            textvariable=self.var_busqueda,
            font=("Arial", 11),
            bootstyle=INFO
        )
        self.entry_busqueda.pack(side=LEFT, fill=X, expand=True)
        self.entry_busqueda.focus()
        
        tb.Button(
            entry_frame,
            text="Limpiar",
            bootstyle=(OUTLINE, SECONDARY),
            command=lambda: self.var_busqueda.set("")
        ).pack(side=RIGHT, padx=(10, 0))
    
    def _crear_area_resultados(self, parent) -> None:
        """Crea el área de resultados."""
        results_frame = tb.Frame(parent)
        results_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Label de resultados
        self.label_resultados = tb.Label(
            results_frame,
            text="",
            font=("Arial", 10),
            bootstyle=(INFO,)
        )
        self.label_resultados.pack(anchor=W, pady=(0, 5))
        
        # Treeview para resultados
        columns = ('fecha', 'hora', 'titulo', 'descripcion')
        self.tree_resultados = tb.Treeview(
            results_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar columnas
        self.tree_resultados.heading('fecha', text='Fecha')
        self.tree_resultados.heading('hora', text='Hora')
        self.tree_resultados.heading('titulo', text='Título')
        self.tree_resultados.heading('descripcion', text='Descripción')
        
        self.tree_resultados.column('fecha', width=100, minwidth=80)
        self.tree_resultados.column('hora', width=80, minwidth=60)
        self.tree_resultados.column('titulo', width=200, minwidth=150)
        self.tree_resultados.column('descripcion', width=300, minwidth=200)
        
        # Scrollbar
        scrollbar = tb.Scrollbar(results_frame, orient=VERTICAL, command=self.tree_resultados.yview)
        self.tree_resultados.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree_resultados.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def _crear_boton_cerrar(self, parent) -> None:
        """Crea el botón para cerrar."""
        # Separador visual
        separator = tb.Separator(parent, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(10, 10))
        
        # Frame específico para el botón cerrar
        button_frame = tb.Frame(parent)
        button_frame.pack(fill=X, pady=(0, 5))
        
        # Botón cerrar centrado
        tb.Button(
            button_frame,
            text="Cerrar",
            bootstyle=(OUTLINE, SECONDARY),
            command=self._cerrar,
            width=12
        ).pack(pady=5)
    
    def _realizar_busqueda(self, *args) -> None:
        """Realiza la búsqueda de eventos."""
        termino = self.var_busqueda.get().strip()
        
        # Limpiar resultados
        for item in self.tree_resultados.get_children():
            self.tree_resultados.delete(item)
        
        if termino:
            # Buscar eventos por título
            eventos = self.eventos_manager.buscar_eventos_por_titulo(termino)
        else:
            # Mostrar todos los eventos
            eventos = self.eventos_manager.eventos
        
        # Ordenar eventos por fecha
        eventos.sort(key=lambda e: (e.fecha, e.hora or "00:00"))
        
        # Agregar resultados
        for evento in eventos:
            hora_display = evento.hora or "Todo el día"
            descripcion_display = (evento.descripcion[:50] + "...") if evento.descripcion and len(evento.descripcion) > 50 else (evento.descripcion or "")
            
            self.tree_resultados.insert(
                '',
                'end',
                values=(evento.fecha, hora_display, evento.titulo, descripcion_display)
            )
        
        # Actualizar label de resultados
        if termino:
            self.label_resultados.config(text=f"Se encontraron {len(eventos)} evento(s) para '{termino}'")
        else:
            self.label_resultados.config(text=f"Total de eventos: {len(eventos)}")
    
    def _cerrar(self) -> None:
        """Cierra la ventana."""
        self.window.destroy() 