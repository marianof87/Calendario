"""
Calendario_UI.py - Interfaz gráfica del sistema de calendario

Este módulo se encarga de:
- Creación y gestión de widgets de la interfaz
- Layout y disposición de componentes
- Interacción con la lógica del calendario
- Renderizado visual del calendario

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Optional
from calendario_logic import CalendarioLogic
from theme_manager import ThemeManager
from helpers import obtener_dias_semana


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
        
        # Configurar callbacks
        self.calendar_logic.set_callback_actualizar_vista(self.actualizar_vista)
        
        # Inicializar tema
        self.theme_manager.inicializar_style("litera")
        self._actualizar_titulo()
        
        # Referencias a widgets
        self.label_fecha = None
        self.combo_tema = None
        self.frame_calendario = None
        
        # Crear la interfaz
        self.crear_widgets()
    
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
        # Determinar el estilo del botón
        if self.calendar_logic.es_dia_hoy(dia):
            # Día actual - estilo especial
            bootstyle = SUCCESS
        elif self.calendar_logic.es_fin_de_semana(dia):
            # Fin de semana - estilo diferente
            bootstyle = WARNING
        else:
            # Día normal
            bootstyle = LIGHT
        
        # Crear botón para el día
        btn_dia = tb.Button(
            self.frame_calendario,
            text=str(dia),
            bootstyle=bootstyle,
            command=lambda d=dia: self._click_dia(d)
        )
        btn_dia.grid(row=row, column=col, padx=1, pady=1, sticky="NSEW")
    
    def _click_dia(self, dia: int) -> None:
        """
        Maneja el click en un día.
        
        Args:
            dia: Día clickeado
        """
        fecha_seleccionada = self.calendar_logic.manejar_click_dia(dia)
        # TODO: Aquí se abrirá la ventana de eventos en Fase 4
    
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