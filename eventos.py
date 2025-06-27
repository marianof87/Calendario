"""
Eventos.py - Sistema de gestión de eventos para el calendario

Este módulo se encarga de:
- Creación, edición y eliminación de eventos
- Persistencia de datos en JSON
- Validación de eventos
- Búsqueda y filtrado de eventos
- Notificaciones de eventos próximos

Autor: Mariano Capella, Gabriel Osemberg
"""

import json
import datetime
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from helpers import validar_fecha, formatear_fecha_completa


@dataclass
class Evento:
    """
    Clase que representa un evento del calendario.
    """
    id: str
    titulo: str
    fecha: str  # Formato: YYYY-MM-DD
    hora: Optional[str] = None  # Formato: HH:MM
    descripcion: Optional[str] = None
    fecha_creacion: str = None
    
    def __post_init__(self):
        """Inicialización posterior al constructor."""
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        """Convierte el evento a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Evento':
        """Crea un evento desde un diccionario."""
        return cls(**data)
    
    def get_fecha_objeto(self) -> datetime.date:
        """Obtiene la fecha como objeto datetime.date."""
        return datetime.datetime.strptime(self.fecha, "%Y-%m-%d").date()
    
    def get_hora_objeto(self) -> Optional[datetime.time]:
        """Obtiene la hora como objeto datetime.time."""
        if self.hora:
            return datetime.datetime.strptime(self.hora, "%H:%M").time()
        return None
    
    def get_datetime_completo(self) -> Optional[datetime.datetime]:
        """Obtiene fecha y hora como datetime completo."""
        if self.hora:
            fecha_str = f"{self.fecha} {self.hora}"
            return datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        return None


class EventosManager:
    """
    Clase para gestionar todos los eventos del calendario.
    """
    
    def __init__(self, archivo_datos: str = "data/eventos.json"):
        """
        Inicializa el gestor de eventos.
        
        Args:
            archivo_datos: Ruta al archivo de datos JSON
        """
        self.archivo_datos = archivo_datos
        self.eventos = []
        self._asegurar_directorio()
        self.cargar_eventos()
    
    def _asegurar_directorio(self) -> None:
        """Asegura que el directorio de datos exista."""
        directorio = os.path.dirname(self.archivo_datos)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def _generar_id(self) -> str:
        """Genera un ID único para un evento."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"evt_{timestamp}_{len(self.eventos)}"
    
    def cargar_eventos(self) -> bool:
        """
        Carga eventos desde el archivo JSON.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            if os.path.exists(self.archivo_datos):
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    eventos_data = data.get('eventos', [])
                    self.eventos = [Evento.from_dict(evento_dict) for evento_dict in eventos_data]
                print(f"✅ Cargados {len(self.eventos)} eventos desde {self.archivo_datos}")
                return True
            else:
                print(f"📁 Archivo {self.archivo_datos} no existe, creando uno nuevo")
                self._crear_archivo_inicial()
                return True
        except Exception as e:
            print(f"❌ Error al cargar eventos: {e}")
            return False
    
    def guardar_eventos(self) -> bool:
        """
        Guarda eventos al archivo JSON.
        
        Returns:
            bool: True si el guardado fue exitoso
        """
        try:
            data = {
                "eventos": [evento.to_dict() for evento in self.eventos],
                "version": "1.0",
                "fecha_actualizacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_eventos": len(self.eventos)
            }
            
            with open(self.archivo_datos, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Guardados {len(self.eventos)} eventos en {self.archivo_datos}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar eventos: {e}")
            return False
    
    def _crear_archivo_inicial(self) -> None:
        """Crea el archivo inicial de eventos."""
        data = {
            "eventos": [],
            "version": "1.0",
            "fecha_creacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": "Archivo de datos para eventos del calendario"
        }
        
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def agregar_evento(self, titulo: str, fecha: str, hora: str = None, descripcion: str = None) -> Tuple[bool, str, Optional[Evento]]:
        """
        Agrega un nuevo evento.
        
        Args:
            titulo: Título del evento (obligatorio)
            fecha: Fecha en formato YYYY-MM-DD
            hora: Hora en formato HH:MM (opcional)
            descripcion: Descripción del evento (opcional)
            
        Returns:
            Tuple[bool, str, Optional[Evento]]: (éxito, mensaje, evento_creado)
        """
        # Validaciones
        if not titulo or titulo.strip() == "":
            return False, "El título del evento es obligatorio", None
        
        try:
            # Validar formato de fecha
            fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return False, "Formato de fecha inválido. Use YYYY-MM-DD", None
        
        if hora:
            try:
                # Validar formato de hora
                datetime.datetime.strptime(hora, "%H:%M")
            except ValueError:
                return False, "Formato de hora inválido. Use HH:MM", None
        
        # Crear evento
        evento_id = self._generar_id()
        evento = Evento(
            id=evento_id,
            titulo=titulo.strip(),
            fecha=fecha,
            hora=hora,
            descripcion=descripcion.strip() if descripcion else None
        )
        
        # Agregar a la lista
        self.eventos.append(evento)
        
        # Guardar cambios
        if self.guardar_eventos():
            mensaje = f"✅ Evento '{titulo}' creado para el {fecha}"
            if hora:
                mensaje += f" a las {hora}"
            return True, mensaje, evento
        else:
            # Si no se pudo guardar, remover de la lista
            self.eventos.remove(evento)
            return False, "Error al guardar el evento", None
    
    def obtener_eventos_fecha(self, fecha: datetime.date) -> List[Evento]:
        """
        Obtiene todos los eventos de una fecha específica.
        
        Args:
            fecha: Fecha a buscar
            
        Returns:
            List[Evento]: Lista de eventos de esa fecha
        """
        fecha_str = fecha.strftime("%Y-%m-%d")
        eventos_fecha = [evento for evento in self.eventos if evento.fecha == fecha_str]
        
        # Ordenar por hora
        eventos_fecha.sort(key=lambda e: e.hora or "00:00")
        
        return eventos_fecha
    
    def obtener_eventos_mes(self, year: int, month: int) -> List[Evento]:
        """
        Obtiene todos los eventos de un mes específico.
        
        Args:
            year: Año
            month: Mes
            
        Returns:
            List[Evento]: Lista de eventos del mes
        """
        eventos_mes = []
        for evento in self.eventos:
            fecha_evento = evento.get_fecha_objeto()
            if fecha_evento.year == year and fecha_evento.month == month:
                eventos_mes.append(evento)
        
        # Ordenar por fecha y hora
        eventos_mes.sort(key=lambda e: (e.fecha, e.hora or "00:00"))
        
        return eventos_mes
    
    def eliminar_evento(self, evento_id: str) -> Tuple[bool, str]:
        """
        Elimina un evento por ID.
        
        Args:
            evento_id: ID del evento a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        evento = self.buscar_evento_por_id(evento_id)
        if not evento:
            return False, "Evento no encontrado"
        
        self.eventos.remove(evento)
        
        if self.guardar_eventos():
            return True, f"✅ Evento '{evento.titulo}' eliminado exitosamente"
        else:
            # Si no se pudo guardar, restaurar el evento
            self.eventos.append(evento)
            return False, "Error al guardar los cambios"
    
    def buscar_evento_por_id(self, evento_id: str) -> Optional[Evento]:
        """
        Busca un evento por su ID.
        
        Args:
            evento_id: ID del evento
            
        Returns:
            Optional[Evento]: Evento encontrado o None
        """
        for evento in self.eventos:
            if evento.id == evento_id:
                return evento
        return None
    
    def buscar_eventos_por_titulo(self, titulo: str) -> List[Evento]:
        """
        Busca eventos por título (búsqueda parcial, insensible a mayúsculas).
        
        Args:
            titulo: Término de búsqueda
            
        Returns:
            List[Evento]: Lista de eventos encontrados
        """
        titulo_lower = titulo.lower()
        eventos_encontrados = [
            evento for evento in self.eventos 
            if titulo_lower in evento.titulo.lower()
        ]
        
        return eventos_encontrados
    
    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadísticas de los eventos.
        
        Returns:
            dict: Estadísticas de eventos
        """
        total_eventos = len(self.eventos)
        eventos_con_hora = len([e for e in self.eventos if e.hora])
        eventos_sin_hora = total_eventos - eventos_con_hora
        
        # Eventos por mes
        eventos_por_mes = {}
        for evento in self.eventos:
            fecha_obj = evento.get_fecha_objeto()
            mes_key = f"{fecha_obj.year}-{fecha_obj.month:02d}"
            eventos_por_mes[mes_key] = eventos_por_mes.get(mes_key, 0) + 1
        
        return {
            'total_eventos': total_eventos,
            'eventos_con_hora': eventos_con_hora,
            'eventos_sin_hora': eventos_sin_hora,
            'eventos_por_mes': eventos_por_mes,
            'archivo_datos': self.archivo_datos
        }
    
    def tiene_eventos_fecha(self, fecha: datetime.date) -> bool:
        """
        Verifica si una fecha tiene eventos.
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            bool: True si hay eventos en esa fecha
        """
        return len(self.obtener_eventos_fecha(fecha)) > 0 