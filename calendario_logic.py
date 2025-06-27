"""
Calendario_Logic.py - Lógica del calendario para el sistema

Este módulo se encarga de:
- Navegación entre meses y años
- Generación de la estructura del calendario
- Manejo de fechas y días especiales
- Lógica de eventos de calendario

Autor: Mariano Capella, Gabriel Osemberg
"""

import datetime
from typing import Callable, Optional, List, Tuple
from helpers import (
    obtener_nombre_mes, es_dia_actual, obtener_calendario_mes,
    navegar_mes, navegar_año, ir_a_hoy
)


class CalendarioLogic:
    """
    Clase que maneja toda la lógica del calendario.
    """
    
    def __init__(self):
        """Inicializa la lógica del calendario."""
        self.hoy = datetime.date.today()
        self.fecha_actual = self.hoy.replace(day=1)
        self.callback_actualizar_vista = None
        
    def set_callback_actualizar_vista(self, callback: Callable) -> None:
        """
        Establece el callback para actualizar la vista.
        
        Args:
            callback: Función a llamar cuando se actualice la vista
        """
        self.callback_actualizar_vista = callback
    
    def get_fecha_actual(self) -> datetime.date:
        """
        Obtiene la fecha actual del calendario.
        
        Returns:
            datetime.date: Fecha actual
        """
        return self.fecha_actual
    
    def get_hoy(self) -> datetime.date:
        """
        Obtiene la fecha de hoy.
        
        Returns:
            datetime.date: Fecha de hoy
        """
        return self.hoy
    
    def get_nombre_mes_actual(self) -> str:
        """
        Obtiene el nombre del mes actual.
        
        Returns:
            str: Nombre del mes y año
        """
        return obtener_nombre_mes(self.fecha_actual)
    
    def _actualizar_vista(self) -> None:
        """Llama al callback de actualización de vista si está disponible."""
        if self.callback_actualizar_vista:
            self.callback_actualizar_vista()
    
    def ir_ano_anterior(self) -> None:
        """Navega al mismo mes del año anterior."""
        self.fecha_actual = navegar_año(self.fecha_actual, 'anterior')
        self._actualizar_vista()
        print(f"📅 Navegando a: {self.get_nombre_mes_actual()}")
    
    def ir_ano_siguiente(self) -> None:
        """Navega al mismo mes del año siguiente."""
        self.fecha_actual = navegar_año(self.fecha_actual, 'siguiente')
        self._actualizar_vista()
        print(f"📅 Navegando a: {self.get_nombre_mes_actual()}")
    
    def ir_mes_anterior(self) -> None:
        """Navega al mes anterior."""
        self.fecha_actual = navegar_mes(self.fecha_actual, 'anterior')
        self._actualizar_vista()
        print(f"📅 Navegando a: {self.get_nombre_mes_actual()}")
    
    def ir_mes_siguiente(self) -> None:
        """Navega al mes siguiente."""
        self.fecha_actual = navegar_mes(self.fecha_actual, 'siguiente')
        self._actualizar_vista()
        print(f"📅 Navegando a: {self.get_nombre_mes_actual()}")
    
    def ir_a_hoy_mes(self) -> None:
        """Navega al mes actual."""
        self.fecha_actual = ir_a_hoy()
        self._actualizar_vista()
        print(f"🏠 Volviendo a hoy: {self.get_nombre_mes_actual()}")
    
    def obtener_matriz_calendario(self) -> List[List[int]]:
        """
        Obtiene la matriz del calendario del mes actual.
        
        Returns:
            List[List[int]]: Matriz con los días del mes
        """
        return obtener_calendario_mes(self.fecha_actual.year, self.fecha_actual.month)
    
    def es_dia_hoy(self, dia: int) -> bool:
        """
        Verifica si un día específico es hoy.
        
        Args:
            dia: Número del día a verificar
            
        Returns:
            bool: True si es el día actual
        """
        try:
            fecha_dia = datetime.date(self.fecha_actual.year, self.fecha_actual.month, dia)
            return es_dia_actual(fecha_dia)
        except ValueError:
            return False
    
    def obtener_fecha_dia(self, dia: int) -> Optional[datetime.date]:
        """
        Obtiene el objeto fecha para un día específico del mes actual.
        
        Args:
            dia: Número del día
            
        Returns:
            Optional[datetime.date]: Fecha del día o None si es inválido
        """
        try:
            return datetime.date(self.fecha_actual.year, self.fecha_actual.month, dia)
        except ValueError:
            return None
    
    def manejar_click_dia(self, dia: int) -> datetime.date:
        """
        Maneja el click en un día específico.
        
        Args:
            dia: Día clickeado
            
        Returns:
            datetime.date: Fecha del día clickeado
        """
        fecha_seleccionada = self.obtener_fecha_dia(dia)
        if fecha_seleccionada:
            print(f"📅 Día seleccionado: {fecha_seleccionada}")
            # TODO: Aquí se implementará la lógica de eventos en Fase 4
            return fecha_seleccionada
        else:
            print(f"❌ Error: Día {dia} no válido")
            return self.fecha_actual
    
    def obtener_info_mes(self) -> dict:
        """
        Obtiene información completa del mes actual.
        
        Returns:
            dict: Información del mes
        """
        matriz = self.obtener_matriz_calendario()
        dias_totales = sum(1 for semana in matriz for dia in semana if dia != 0)
        
        return {
            'año': self.fecha_actual.year,
            'mes': self.fecha_actual.month,
            'nombre_mes': self.get_nombre_mes_actual(),
            'dias_totales': dias_totales,
            'semanas': len(matriz),
            'primer_dia': matriz[0][0] if matriz and matriz[0] else 0,
            'ultimo_dia': max(max(semana) for semana in matriz),
            'es_mes_actual': (self.fecha_actual.year == self.hoy.year 
                             and self.fecha_actual.month == self.hoy.month)
        }
    
    def navegar_a_fecha(self, year: int, month: int) -> bool:
        """
        Navega a una fecha específica.
        
        Args:
            year: Año de destino
            month: Mes de destino (1-12)
            
        Returns:
            bool: True si la navegación fue exitosa
        """
        try:
            nueva_fecha = datetime.date(year, month, 1)
            self.fecha_actual = nueva_fecha
            self._actualizar_vista()
            print(f"📅 Navegando a: {self.get_nombre_mes_actual()}")
            return True
        except ValueError:
            print(f"❌ Error: Fecha inválida ({year}/{month})")
            return False
    
    def obtener_dias_especiales(self) -> List[Tuple[int, str]]:
        """
        Obtiene los días especiales del mes actual.
        
        Returns:
            List[Tuple[int, str]]: Lista de (día, descripción) de días especiales
        """
        dias_especiales = []
        
        # Agregar el día actual si está en el mes
        if self.fecha_actual.year == self.hoy.year and self.fecha_actual.month == self.hoy.month:
            dias_especiales.append((self.hoy.day, "Hoy"))
        
        # TODO: Aquí se pueden agregar más días especiales como:
        # - Eventos guardados
        # - Días festivos
        # - Recordatorios
        
        return dias_especiales
    
    def es_fin_de_semana(self, dia: int) -> bool:
        """
        Verifica si un día es fin de semana.
        
        Args:
            dia: Número del día
            
        Returns:
            bool: True si es sábado o domingo
        """
        fecha_dia = self.obtener_fecha_dia(dia)
        if fecha_dia:
            # weekday(): Lunes=0, Domingo=6
            return fecha_dia.weekday() in [5, 6]  # Sábado y Domingo
        return False
    
    def obtener_estadisticas_mes(self) -> dict:
        """
        Obtiene estadísticas del mes actual.
        
        Returns:
            dict: Estadísticas del mes
        """
        matriz = self.obtener_matriz_calendario()
        dias_laborables = 0
        dias_fin_semana = 0
        
        for semana in matriz:
            for dia in semana:
                if dia != 0:
                    if self.es_fin_de_semana(dia):
                        dias_fin_semana += 1
                    else:
                        dias_laborables += 1
        
        return {
            'dias_laborables': dias_laborables,
            'dias_fin_semana': dias_fin_semana,
            'total_dias': dias_laborables + dias_fin_semana,
            'semanas_completas': len([s for s in matriz if all(d != 0 for d in s)])
        } 