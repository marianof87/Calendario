"""
Calendario_UI.py - Interfaz gráfica del sistema de calendario

Este módulo se encarga de:
- Creación y gestión de widgets de la interfaz
- Layout y disposición de componentes
- Interacción con la lógica del calendario
- Renderizado visual del calendario
- Gestión de eventos y notificaciones
- Interfaz para CRUD de eventos

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import datetime
from typing import Optional, List
from calendario_logic import CalendarioLogic
from theme_manager import ThemeManager
from helpers import obtener_dias_semana, formatear_fecha_completa
from eventos import EventosManager
from notificaciones import NotificacionesManager
from evento_dialogs import EventoDialog, EventosDelDiaDialog, BuscarEventosDialog


class CalendarioUI:
    """
    Clase que maneja toda la interfaz gráfica del calendario.
    """
    
    def __init__(self, root: tb.Window):
        """
        Inicializa la interfaz del calendario.
        
        Args:
            root: Ventana principal de ttkbootstrap
        """
        self.root = root
        self.root.title("Calendario")
        
        # Inicializar componentes
        self.calendar_logic = CalendarioLogic()
        self.theme_manager = ThemeManager()
        self.eventos_manager = EventosManager()
        self.notificaciones_manager = NotificacionesManager(self.eventos_manager)
        
        # Configurar callbacks
        self.calendar_logic.set_callback_actualizar_vista(self.actualizar_vista)
        self.notificaciones_manager.set_callback_mostrar_notificacion(self._mostrar_notificacion_ui)
        
        # Inicializar tema
        self.theme_manager.inicializar_style("litera")
        self._actualizar_titulo()
        
        # Referencias a widgets
        self.label_fecha = None
        self.combo_tema = None
        self.frame_calendario = None
        self.botones_dias = {}  # Diccionario para almacenar botones de días
        
        # Crear la interfaz
        self.crear_widgets()
        
        # Verificar eventos próximos al inicio
        self._verificar_eventos_inicio()
    
    def _actualizar_titulo(self) -> None:
        """Actualiza el título de la ventana con el tema actual."""
        titulo = self.theme_manager.get_titulo_con_tema("Calendario")
        self.root.title(titulo)
    
    def crear_widgets(self) -> None:
        """Crea todos los widgets de la interfaz."""
        self._crear_barra_superior()
        self._crear_area_calendario()
        self.actualizar_vista()
    
    def _crear_barra_superior(self) -> None:
        """Crea la barra superior con navegación y selector de tema."""
        # Frame superior para la cabecera
        top_frame = tb.Frame(self.root, padding=10)
        top_frame.pack(fill=X)
        
        # Frame izquierdo para navegación
        nav_frame = tb.Frame(top_frame)
        nav_frame.pack(side=LEFT)
        
        # Botones de navegación
        self._crear_botones_navegacion(nav_frame)
        
        # Frame central para selector de tema
        tema_frame = tb.Frame(top_frame)
        tema_frame.pack(side=LEFT, padx=20)
        self._crear_selector_tema(tema_frame)
        
        # Frame para botones de eventos
        eventos_frame = tb.Frame(top_frame)
        eventos_frame.pack(side=LEFT, padx=20)
        self._crear_botones_eventos(eventos_frame)
        
        # Etiqueta para mostrar mes y año
        self.label_fecha = tb.Label(
            top_frame, 
            text=self.calendar_logic.get_nombre_mes_actual(), 
            font=("Arial", 18, "bold")
        )
        self.label_fecha.pack(side=RIGHT)
    
    def _crear_botones_navegacion(self, parent_frame: tb.Frame) -> None:
        """
        Crea los botones de navegación.
        
        Args:
            parent_frame: Frame contenedor para los botones
        """
        # Botón año anterior
        btn_ano_ant = tb.Button(
            parent_frame, 
            text="<<", 
            bootstyle=SECONDARY, 
            command=self.calendar_logic.ir_ano_anterior
        )
        btn_ano_ant.pack(side=LEFT, padx=2)
        
        # Botón mes anterior
        btn_mes_ant = tb.Button(
            parent_frame, 
            text="<", 
            bootstyle=SECONDARY, 
            command=self.calendar_logic.ir_mes_anterior
        )
        btn_mes_ant.pack(side=LEFT, padx=2)
        
        # Botón hoy
        btn_hoy = tb.Button(
            parent_frame, 
            text="Hoy", 
            bootstyle=INFO, 
            command=self.calendar_logic.ir_a_hoy_mes
        )
        btn_hoy.pack(side=LEFT, padx=2)
        
        # Botón mes siguiente
        btn_mes_sig = tb.Button(
            parent_frame, 
            text=">", 
            bootstyle=SECONDARY, 
            command=self.calendar_logic.ir_mes_siguiente
        )
        btn_mes_sig.pack(side=LEFT, padx=2)
        
        # Botón año siguiente
        btn_ano_sig = tb.Button(
            parent_frame, 
            text=">>", 
            bootstyle=SECONDARY, 
            command=self.calendar_logic.ir_ano_siguiente
        )
        btn_ano_sig.pack(side=LEFT, padx=2)
    
    def _crear_selector_tema(self, parent_frame: tb.Frame) -> None:
        """
        Crea el selector de tema.
        
        Args:
            parent_frame: Frame contenedor para el selector
        """
        # Label del selector
        tb.Label(parent_frame, text="Tema:", font=("Arial", 10)).pack(side=LEFT, padx=(0, 5))
        
        # Combobox de temas
        self.combo_tema = tb.Combobox(
            parent_frame,
            values=self.theme_manager.get_temas_disponibles(),
            state="readonly",
            width=12,
            bootstyle=PRIMARY
        )
        self.combo_tema.set(self.theme_manager.get_tema_actual())
        self.combo_tema.bind("<<ComboboxSelected>>", self.cambiar_tema)
        self.combo_tema.pack(side=LEFT)
    
    def _crear_botones_eventos(self, parent_frame: tb.Frame) -> None:
        """
        Crea los botones para gestión de eventos.
        
        Args:
            parent_frame: Frame contenedor para los botones
        """
        # Botón Agregar Evento
        btn_agregar = tb.Button(
            parent_frame,
            text="➕ Evento",
            bootstyle=SUCCESS,
            command=self._agregar_evento
        )
        btn_agregar.pack(side=LEFT, padx=2)
        
        # Botón Buscar Eventos
        btn_buscar = tb.Button(
            parent_frame,
            text="🔍 Buscar",
            bootstyle=INFO,
            command=self._buscar_eventos
        )
        btn_buscar.pack(side=LEFT, padx=2)
        
        # Botón Eventos del Mes
        btn_mes = tb.Button(
            parent_frame,
            text="📅 Mes",
            bootstyle=WARNING,
            command=self._mostrar_eventos_mes
        )
        btn_mes.pack(side=LEFT, padx=2)
    
    def _crear_area_calendario(self) -> None:
        """Crea el área del calendario."""
        # Frame central para el calendario
        self.frame_calendario = tb.Frame(self.root, padding=10)
        self.frame_calendario.pack(fill=BOTH, expand=True)
    
    def cambiar_tema(self, event=None) -> None:
        """
        Maneja el cambio de tema.
        
        Args:
            event: Evento de selección del combobox
        """
        nuevo_tema = self.combo_tema.get()
        
        # Intentar cambiar el tema
        exito, mensaje = self.theme_manager.cambiar_tema(nuevo_tema)
        
        if not exito:
            # Si no fue exitoso, revertir la selección
            self.combo_tema.set(self.theme_manager.get_tema_actual())
            print(f"❌ {mensaje}")
        else:
            # Si fue exitoso, actualizar la vista
            self._actualizar_titulo()
            self.crear_calendario()
            print(mensaje)
    
    def actualizar_vista(self) -> None:
        """Actualiza la etiqueta del mes y regenera el calendario."""
        if self.label_fecha:
            self.label_fecha.config(text=self.calendar_logic.get_nombre_mes_actual())
        self.crear_calendario()
    
    def crear_calendario(self) -> None:
        """Crea la grilla visual del calendario."""
        if not self.frame_calendario:
            return
            
        # Limpiar el frame del calendario
        for widget in self.frame_calendario.winfo_children():
            widget.destroy()
        
        # Limpiar referencias a botones
        self.botones_dias.clear()
        
        # Crear encabezados de días de la semana
        self._crear_encabezados_dias()
        
        # Crear la grilla de días
        self._crear_grilla_dias()
        
        # Configurar expansión de columnas y filas
        self._configurar_expansion()
    
    def _crear_encabezados_dias(self) -> None:
        """Crea los encabezados de los días de la semana."""
        dias_semana = obtener_dias_semana()
        
        for i, dia in enumerate(dias_semana):
            label = tb.Label(
                self.frame_calendario, 
                text=dia, 
                font=("Arial", 12, "bold"),
                bootstyle=INFO
            )
            label.grid(row=0, column=i, padx=1, pady=1, sticky="NSEW")
    
    def _crear_grilla_dias(self) -> None:
        """Crea la grilla de días del calendario."""
        # Obtener la matriz del calendario
        cal = self.calendar_logic.obtener_matriz_calendario()
        
        # Crear botones para cada día
        for fila_idx, semana in enumerate(cal, start=1):
            for col_idx, dia in enumerate(semana):
                if dia == 0:
                    # Día vacío (pertenece al mes anterior/siguiente)
                    label = tb.Label(self.frame_calendario, text="")
                    label.grid(row=fila_idx, column=col_idx, padx=1, pady=1, sticky="NSEW")
                else:
                    # Crear botón para el día
                    self._crear_boton_dia(dia, fila_idx, col_idx)
    
    def _crear_boton_dia(self, dia: int, row: int, col: int) -> None:
        """
        Crea un botón para un día específico.
        
        Args:
            dia: Número del día
            row: Fila en la grilla
            col: Columna en la grilla
        """
        # Crear fecha para verificar eventos
        fecha_actual = self.calendar_logic.get_fecha_actual()
        fecha_dia = datetime.date(
            fecha_actual.year,
            fecha_actual.month,
            dia
        )
        
        # Verificar si hay eventos en este día
        eventos_dia = self.eventos_manager.obtener_eventos_fecha(fecha_dia)
        tiene_eventos = len(eventos_dia) > 0
        
        # Determinar el estilo del botón
        if self.calendar_logic.es_dia_hoy(dia):
            # Día actual - estilo especial
            bootstyle = SUCCESS
        elif tiene_eventos:
            # Días con eventos - estilo especial
            bootstyle = DANGER
        elif self.calendar_logic.es_fin_de_semana(dia):
            # Fin de semana - estilo diferente
            bootstyle = WARNING
        else:
            # Día normal
            bootstyle = LIGHT
        
        # Crear texto del botón con indicador de eventos
        texto_boton = str(dia)
        if tiene_eventos:
            texto_boton += f" ({len(eventos_dia)})"
        
        # Crear botón para el día
        btn_dia = tb.Button(
            self.frame_calendario,
            text=texto_boton,
            bootstyle=bootstyle,
            command=lambda d=dia: self._click_dia(d)
        )
        btn_dia.grid(row=row, column=col, padx=1, pady=1, sticky="NSEW")
        
        # Guardar referencia al botón
        self.botones_dias[dia] = btn_dia
    
    def _click_dia(self, dia: int) -> None:
        """
        Maneja el click en un día.
        
        Args:
            dia: Día clickeado
        """
        fecha_seleccionada = self.calendar_logic.manejar_click_dia(dia)
        
        # Crear fecha completa
        fecha_actual = self.calendar_logic.get_fecha_actual()
        fecha_dia = datetime.date(
            fecha_actual.year,
            fecha_actual.month,
            dia
        )
        
        # Abrir ventana de eventos del día
        self._mostrar_eventos_dia(fecha_dia)
    
    def _configurar_expansion(self) -> None:
        """Configura la expansión de columnas y filas."""
        # Configurar que las columnas se expandan
        for i in range(7):
            self.frame_calendario.columnconfigure(i, weight=1)
        
        # Configurar que las filas se expandan
        matriz = self.calendar_logic.obtener_matriz_calendario()
        for i in range(len(matriz) + 1):  # +1 por los encabezados
            self.frame_calendario.rowconfigure(i, weight=1)
    
    def obtener_info_estado(self) -> dict:
        """
        Obtiene información del estado actual de la UI.
        
        Returns:
            dict: Información del estado
        """
        return {
            'tema_actual': self.theme_manager.get_tema_actual(),
            'fecha_actual': self.calendar_logic.get_fecha_actual(),
            'mes_actual': self.calendar_logic.get_nombre_mes_actual(),
            'info_tema': self.theme_manager.get_info_tema_completa(),
            'info_mes': self.calendar_logic.obtener_info_mes()
        }
    
    def mostrar_estadisticas(self) -> None:
        """Muestra estadísticas del mes actual en consola."""
        stats = self.calendar_logic.obtener_estadisticas_mes()
        info = self.calendar_logic.obtener_info_mes()
        
        print(f"\n📊 Estadísticas de {info['nombre_mes']}:")
        print(f"   • Días laborables: {stats['dias_laborables']}")
        print(f"   • Días de fin de semana: {stats['dias_fin_semana']}")
        print(f"   • Total de días: {stats['total_dias']}")
        print(f"   • Semanas completas: {stats['semanas_completas']}")
    
    def get_calendar_logic(self) -> CalendarioLogic:
        """
        Obtiene la instancia de lógica del calendario.
        
        Returns:
            CalendarioLogic: Instancia de lógica
        """
        return self.calendar_logic
    
    def get_theme_manager(self) -> ThemeManager:
        """
        Obtiene la instancia del gestor de temas.
        
        Returns:
            ThemeManager: Instancia del gestor
        """
        return self.theme_manager
    
    # =============== MÉTODOS DE GESTIÓN DE EVENTOS ===============
    
    def _agregar_evento(self) -> None:
        """Abre el diálogo para agregar un nuevo evento."""
        dialog = EventoDialog(self.root, "Agregar Evento")
        resultado = dialog.mostrar()
        
        if resultado:
            # Validar conflictos de horario
            hay_conflicto, eventos_conflicto = self.notificaciones_manager.validador.validar_conflicto_horario(resultado)
            
            if hay_conflicto:
                # Mostrar notificación de conflicto
                notificacion_conflicto = self.notificaciones_manager.generar_notificacion_conflicto(resultado, eventos_conflicto)
                respuesta = Messagebox.show_question(
                    notificacion_conflicto.titulo,
                    notificacion_conflicto.mensaje,
                    parent=self.root
                )
                
                if respuesta != "Yes":
                    return
            
            # Verificar si es evento en el pasado
            if self.notificaciones_manager.validador.validar_evento_pasado(resultado['fecha'], resultado.get('hora')):
                notificacion_pasado = self.notificaciones_manager.generar_notificacion_evento_pasado(resultado)
                respuesta = Messagebox.show_question(
                    notificacion_pasado.titulo,
                    notificacion_pasado.mensaje,
                    parent=self.root
                )
                
                if respuesta != "Yes":
                    return
            
            # Agregar el evento
            exito, mensaje, evento = self.eventos_manager.agregar_evento(
                titulo=resultado['titulo'],
                fecha=resultado['fecha'],
                hora=resultado['hora'],
                descripcion=resultado['descripcion']
            )
            
            if exito:
                Messagebox.show_info("Éxito", mensaje, parent=self.root)
                self.actualizar_vista()  # Actualizar calendario
            else:
                Messagebox.show_error("Error", mensaje, parent=self.root)
    
    def _buscar_eventos(self) -> None:
        """Abre el diálogo de búsqueda de eventos."""
        dialog = BuscarEventosDialog(self.root, self.eventos_manager)
    
    def _mostrar_eventos_mes(self) -> None:
        """Muestra todos los eventos del mes actual."""
        fecha_actual = self.calendar_logic.get_fecha_actual()
        mes_actual = fecha_actual.month
        ano_actual = fecha_actual.year
        
        eventos_mes = self.eventos_manager.obtener_eventos_mes(ano_actual, mes_actual)
        
        if not eventos_mes:
            Messagebox.show_info(
                "Información",
                f"No hay eventos en {self.calendar_logic.get_nombre_mes_actual()}",
                parent=self.root
            )
            return
        
        # Crear ventana modal para mostrar eventos del mes
        self._mostrar_ventana_eventos_mes(eventos_mes)
    
    def _mostrar_eventos_dia(self, fecha: datetime.date) -> None:
        """
        Muestra los eventos de un día específico.
        
        Args:
            fecha: Fecha del día
        """
        dialog = EventosDelDiaDialog(self.root, fecha, self.eventos_manager)
        dialog.set_callback_actualizar(self.actualizar_vista)
    
    def _mostrar_ventana_eventos_mes(self, eventos: List) -> None:
        """
        Crea una ventana modal para mostrar eventos del mes.
        
        Args:
            eventos: Lista de eventos del mes
        """
        # Crear ventana modal
        ventana = tb.Toplevel(self.root)
        ventana.title(f"Eventos de {self.calendar_logic.get_nombre_mes_actual()}")
        ventana.geometry("800x600")
        ventana.resizable(True, True)
        
        # Hacer modal
        ventana.transient(self.root)
        ventana.grab_set()
        
        # Frame principal
        main_frame = tb.Frame(ventana, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Título
        tb.Label(
            main_frame,
            text=f"📅 Eventos de {self.calendar_logic.get_nombre_mes_actual()}",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 15))
        
        # Información de resumen
        tb.Label(
            main_frame,
            text=f"Total de eventos: {len(eventos)}",
            font=("Arial", 12),
            bootstyle=INFO
        ).pack(pady=(0, 10))
        
        # Crear Treeview
        columns = ('fecha', 'hora', 'titulo', 'descripcion')
        tree = tb.Treeview(
            main_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        # Configurar columnas
        tree.heading('fecha', text='Fecha')
        tree.heading('hora', text='Hora')
        tree.heading('titulo', text='Título')
        tree.heading('descripcion', text='Descripción')
        
        tree.column('fecha', width=100, minwidth=80)
        tree.column('hora', width=80, minwidth=60)
        tree.column('titulo', width=200, minwidth=150)
        tree.column('descripcion', width=400, minwidth=300)
        
        # Scrollbar
        scrollbar = tb.Scrollbar(main_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=LEFT, fill=BOTH, expand=True, pady=(0, 15))
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Ordenar eventos por fecha y hora
        eventos.sort(key=lambda e: (e.fecha, e.hora or "00:00"))
        
        # Agregar eventos al árbol
        for evento in eventos:
            hora_display = evento.hora or "Todo el día"
            descripcion_display = (evento.descripcion[:80] + "...") if evento.descripcion and len(evento.descripcion) > 80 else (evento.descripcion or "")
            
            tree.insert(
                '',
                'end',
                values=(evento.fecha, hora_display, evento.titulo, descripcion_display)
            )
        
        # Botón cerrar
        tb.Button(
            main_frame,
            text="Cerrar",
            bootstyle=(OUTLINE, SECONDARY),
            command=ventana.destroy
        ).pack(pady=(15, 0))
    
    def _verificar_eventos_inicio(self) -> None:
        """Verifica eventos próximos al iniciar la aplicación."""
        try:
            notificaciones = self.notificaciones_manager.verificar_inicio_aplicacion()
            
            if notificaciones:
                # Mostrar resumen de notificaciones
                self._mostrar_resumen_notificaciones(notificaciones)
        except Exception as e:
            print(f"Error al verificar eventos: {e}")
    
    def _mostrar_notificacion_ui(self, notificacion) -> None:
        """
        Muestra una notificación en la interfaz.
        
        Args:
            notificacion: Notificación a mostrar
        """
        # Mostrar como Messagebox según el tipo
        if notificacion.urgencia >= 2:
            Messagebox.show_warning(notificacion.titulo, notificacion.mensaje, parent=self.root)
        elif notificacion.urgencia >= 1:
            Messagebox.show_info(notificacion.titulo, notificacion.mensaje, parent=self.root)
        else:
            print(f"{notificacion.get_icono()} {notificacion.titulo}: {notificacion.mensaje}")
    
    def _mostrar_resumen_notificaciones(self, notificaciones: List) -> None:
        """
        Muestra un resumen de notificaciones.
        
        Args:
            notificaciones: Lista de notificaciones
        """
        if not notificaciones:
            return
        
        mensaje = f"¡Tienes {len(notificaciones)} recordatorio(s)!\n\n"
        
        for notif in notificaciones[:5]:  # Mostrar máximo 5
            mensaje += f"{notif.get_icono()} {notif.evento.titulo}\n"
            if notif.evento.hora:
                mensaje += f"   🕒 {notif.evento.hora}\n"
            mensaje += "\n"
        
        if len(notificaciones) > 5:
            mensaje += f"... y {len(notificaciones) - 5} recordatorios más"
        
        Messagebox.show_info("📢 Recordatorios", mensaje, parent=self.root)
    
    def obtener_estadisticas_completas(self) -> dict:
        """
        Obtiene estadísticas completas del sistema.
        
        Returns:
            dict: Estadísticas completas
        """
        stats_calendario = self.calendar_logic.obtener_estadisticas_mes()
        stats_eventos = self.eventos_manager.obtener_estadisticas()
        stats_notificaciones = self.notificaciones_manager.obtener_estadisticas_completas()
        
        return {
            'calendario': stats_calendario,
            'eventos': stats_eventos,
            'notificaciones': stats_notificaciones,
            'tema_actual': self.theme_manager.get_tema_actual()
        }
    
    def get_eventos_manager(self) -> EventosManager:
        """
        Obtiene la instancia del gestor de eventos.
        
        Returns:
            EventosManager: Instancia del gestor
        """
        return self.eventos_manager
    
    def get_notificaciones_manager(self) -> NotificacionesManager:
        """
        Obtiene la instancia del gestor de notificaciones.
        
        Returns:
            NotificacionesManager: Instancia del gestor
        """
        return self.notificaciones_manager