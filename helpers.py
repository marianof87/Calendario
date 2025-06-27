"""
Helpers.py - Funciones de utilidad para el sistema de calendario

Este módulo contiene funciones de ayuda para:
- Formateo de fechas
- Validaciones de fecha
- Conversiones de formato
- Utilidades generales del calendario

Autor: Mariano Capella, Gabriel Osemberg
"""

import datetime
import calendar
from typing import Optional, List, Tuple


def obtener_nombre_mes(fecha: datetime.date) -> str:
    """
    Obtiene el nombre del mes y año en formato legible.
    
    Args:
        fecha: Objeto datetime.date
        
    Returns:
        str: Nombre del mes y año (ej: "Enero 2025")
    """
    return fecha.strftime("%B %Y").capitalize()


def es_dia_actual(fecha: datetime.date) -> bool:
    """
    Verifica si una fecha es el día actual.
    
    Args:
        fecha: Fecha a verificar
        
    Returns:
        bool: True si es el día actual
    """
    return fecha == datetime.date.today()


def obtener_calendario_mes(year: int, month: int) -> List[List[int]]:
    """
    Obtiene la matriz del calendario para un mes específico.
    
    Args:
        year: Año
        month: Mes (1-12)
        
    Returns:
        List[List[int]]: Matriz con los días del mes (0 para días vacíos)
    """
    return calendar.monthcalendar(year, month)


def obtener_dias_semana() -> List[str]:
    """
    Obtiene los nombres de los días de la semana.
    
    Returns:
        List[str]: Lista con nombres de días
    """
    return ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


def navegar_mes(fecha_actual: datetime.date, direccion: str) -> datetime.date:
    """
    Navega a un mes anterior o siguiente.
    
    Args:
        fecha_actual: Fecha base
        direccion: 'anterior' o 'siguiente'
        
    Returns:
        datetime.date: Nueva fecha
        
    Raises:
        ValueError: Si la dirección no es válida
    """
    if direccion == 'anterior':
        if fecha_actual.month == 1:
            return fecha_actual.replace(year=fecha_actual.year - 1, month=12)
        else:
            return fecha_actual.replace(month=fecha_actual.month - 1)
    elif direccion == 'siguiente':
        if fecha_actual.month == 12:
            return fecha_actual.replace(year=fecha_actual.year + 1, month=1)
        else:
            return fecha_actual.replace(month=fecha_actual.month + 1)
    else:
        raise ValueError("Dirección debe ser 'anterior' o 'siguiente'")


def navegar_año(fecha_actual: datetime.date, direccion: str) -> datetime.date:
    """
    Navega a un año anterior o siguiente.
    
    Args:
        fecha_actual: Fecha base
        direccion: 'anterior' o 'siguiente'
        
    Returns:
        datetime.date: Nueva fecha con manejo de años bisiestos
    """
    incremento = -1 if direccion == 'anterior' else 1
    
    try:
        return fecha_actual.replace(year=fecha_actual.year + incremento)
    except ValueError:
        # Manejo de años bisiestos (29 de febrero)
        return fecha_actual.replace(year=fecha_actual.year + incremento, day=28)


def ir_a_hoy() -> datetime.date:
    """
    Obtiene la fecha actual con día = 1.
    
    Returns:
        datetime.date: Primer día del mes actual
    """
    hoy = datetime.date.today()
    return hoy.replace(day=1)


def validar_fecha(year: int, month: int, day: int) -> bool:
    """
    Valida si una fecha es válida.
    
    Args:
        year: Año
        month: Mes
        day: Día
        
    Returns:
        bool: True si la fecha es válida
    """
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False


def formatear_fecha_completa(fecha: datetime.date) -> str:
    """
    Formatea una fecha completa en español.
    
    Args:
        fecha: Fecha a formatear
        
    Returns:
        str: Fecha formateada (ej: "Lunes, 15 de Enero de 2025")
    """
    dias_semana = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    dia_semana = dias_semana[fecha.weekday()]
    mes = meses[fecha.month]
    
    return f"{dia_semana}, {fecha.day} de {mes} de {fecha.year}" 