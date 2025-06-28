"""
Notificaciones.py - Sistema de notificaciones y recordatorios

Este módulo se encarga de:
- Detección de eventos próximos
- Notificaciones de recordatorios
- Alertas de conflictos de horario
- Validaciones de eventos
- Mensajes al usuario

Autor: Mariano Capella, Gabriel Osemberg
"""

import datetime
import winsound
import sys
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from src.core.eventos import Evento, EventosManager
from src.utils.helpers import formatear_fecha_completa


@dataclass
class Notificacion:
    """
    Clase que representa una notificación.
    """
    tipo: str  # 'recordatorio', 'conflicto', 'info', 'warning'
    titulo: str
    mensaje: str
    evento: Optional[Evento] = None
    urgencia: int = 0  # 0=baja, 1=media, 2=alta
    fecha_notificacion: datetime.datetime = None
    
    def __post_init__(self):
        if self.fecha_notificacion is None:
            self.fecha_notificacion = datetime.datetime.now()
    
    def get_icono(self) -> str:
        """Obtiene el icono según el tipo de notificación."""
        iconos = {
            'recordatorio': '🔔',
            'conflicto': '⚠️',
            'info': 'ℹ️',
            'warning': '⚡',
            'success': '✅',
            'error': '❌'
        }
        return iconos.get(self.tipo, '📢')
    
    def get_color_urgencia(self) -> str:
        """Obtiene el color según la urgencia."""
        colores = {
            0: 'info',      # Azul - Baja
            1: 'warning',   # Amarillo - Media  
            2: 'danger'     # Rojo - Alta
        }
        return colores.get(self.urgencia, 'info')
    
    def reproducir_sonido(self) -> None:
        """Reproduce sonido de forma no bloqueante según el tipo y urgencia."""
        try:
            if sys.platform == "win32":
                if self.urgencia >= 2:  # Alta urgencia
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    # Solo un beep corto para evitar bloqueos
                    winsound.Beep(800, 200)  # Beep más corto
                elif self.urgencia >= 1:  # Media urgencia
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                else:  # Baja urgencia
                    winsound.MessageBeep(winsound.MB_OK)
            else:
                # Para otros sistemas, usar beep del sistema
                print('\a')  # ASCII bell
        except Exception as e:
            print(f"⚠️ Audio no disponible: {e}")  # Menos verbose


class ValidadorEventos:
    """
    Clase para validar eventos y detectar conflictos.
    """
    
    def __init__(self, eventos_manager: EventosManager):
        """
        Inicializa el validador.
        
        Args:
            eventos_manager: Gestor de eventos
        """
        self.eventos_manager = eventos_manager
    
    def validar_conflicto_horario(self, evento_nuevo: dict, excluir_id: str = None) -> Tuple[bool, List[Evento]]:
        """
        Valida si un evento tiene conflicto de horario.
        
        Args:
            evento_nuevo: Datos del evento a validar
            excluir_id: ID del evento a excluir (para edición)
            
        Returns:
            Tuple[bool, List[Evento]]: (hay_conflicto, eventos_conflicto)
        """
        if not evento_nuevo.get('hora'):
            # Sin hora específica, no hay conflicto
            return False, []
        
        fecha_str = evento_nuevo['fecha']
        hora_str = evento_nuevo['hora']
        
        try:
            fecha_evento = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_evento = datetime.datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            return False, []
        
        # Obtener eventos del mismo día
        eventos_dia = self.eventos_manager.obtener_eventos_fecha(fecha_evento)
        
        eventos_conflicto = []
        for evento in eventos_dia:
            # Excluir el evento que se está editando
            if excluir_id and evento.id == excluir_id:
                continue
            
            # Solo verificar eventos con hora
            if evento.hora:
                try:
                    hora_existente = datetime.datetime.strptime(evento.hora, "%H:%M").time()
                    if hora_existente == hora_evento:
                        eventos_conflicto.append(evento)
                except ValueError:
                    continue
        
        return len(eventos_conflicto) > 0, eventos_conflicto
    
    def validar_evento_pasado(self, fecha_str: str, hora_str: str = None) -> bool:
        """
        Valida si un evento es en el pasado.
        
        Args:
            fecha_str: Fecha del evento
            hora_str: Hora del evento (opcional)
            
        Returns:
            bool: True si el evento es en el pasado
        """
        try:
            fecha_evento = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
            ahora = datetime.datetime.now()
            
            if fecha_evento < ahora.date():
                return True
            elif fecha_evento == ahora.date() and hora_str:
                try:
                    hora_evento = datetime.datetime.strptime(hora_str, "%H:%M").time()
                    datetime_evento = datetime.datetime.combine(fecha_evento, hora_evento)
                    return datetime_evento < ahora
                except ValueError:
                    pass
        except ValueError:
            pass
        
        return False
    
    def validar_fecha_valida(self, fecha_str: str) -> Tuple[bool, str]:
        """
        Valida si una fecha es válida.
        
        Args:
            fecha_str: Fecha en formato string
            
        Returns:
            Tuple[bool, str]: (es_valida, mensaje_error)
        """
        try:
            fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
            
            # Verificar que no sea demasiado lejana (10 años)
            limite_futuro = datetime.date.today() + datetime.timedelta(days=3650)
            if fecha > limite_futuro:
                return False, "La fecha no puede ser más de 10 años en el futuro"
            
            # Verificar que no sea demasiado antigua (100 años)
            limite_pasado = datetime.date.today() - datetime.timedelta(days=36500)
            if fecha < limite_pasado:
                return False, "La fecha no puede ser más de 100 años en el pasado"
            
            return True, ""
        except ValueError:
            return False, "Formato de fecha inválido. Use YYYY-MM-DD"
    
    def obtener_estadisticas_validacion(self) -> dict:
        """
        Obtiene estadísticas de validación de eventos.
        
        Returns:
            dict: Estadísticas de validación
        """
        total_eventos = len(self.eventos_manager.eventos)
        eventos_pasados = 0
        eventos_futuros = 0
        eventos_hoy = 0
        eventos_con_hora = 0
        eventos_conflictos = 0
        
        hoy = datetime.date.today()
        
        for evento in self.eventos_manager.eventos:
            try:
                fecha_evento = evento.get_fecha_objeto()
                
                if fecha_evento < hoy:
                    eventos_pasados += 1
                elif fecha_evento > hoy:
                    eventos_futuros += 1
                else:
                    eventos_hoy += 1
                
                if evento.hora:
                    eventos_con_hora += 1
            except:
                pass
        
        # Verificar conflictos existentes
        for evento in self.eventos_manager.eventos:
            if evento.hora:
                evento_dict = {
                    'fecha': evento.fecha,
                    'hora': evento.hora
                }
                hay_conflicto, _ = self.validar_conflicto_horario(evento_dict, evento.id)
                if hay_conflicto:
                    eventos_conflictos += 1
        
        return {
            'total_eventos': total_eventos,
            'eventos_pasados': eventos_pasados,
            'eventos_futuros': eventos_futuros,
            'eventos_hoy': eventos_hoy,
            'eventos_con_hora': eventos_con_hora,
            'eventos_sin_hora': total_eventos - eventos_con_hora,
            'eventos_conflictos': eventos_conflictos
        }


class NotificacionesManager:
    """
    Clase principal para gestionar notificaciones.
    """
    
    def __init__(self, eventos_manager: EventosManager):
        """
        Inicializa el gestor de notificaciones.
        
        Args:
            eventos_manager: Gestor de eventos
        """
        self.eventos_manager = eventos_manager
        self.validador = ValidadorEventos(eventos_manager)
        self.notificaciones = []
        self.callback_mostrar_notificacion = None
        
        # Configuración de recordatorios
        self.horas_recordatorio = [24, 1]  # 24 horas y 1 hora antes
    
    def set_callback_mostrar_notificacion(self, callback: Callable) -> None:
        """
        Establece el callback para mostrar notificaciones.
        
        Args:
            callback: Función para mostrar notificaciones
        """
        self.callback_mostrar_notificacion = callback
    
    def verificar_eventos_proximos(self, horas_adelante: int = 24) -> List[Notificacion]:
        """
        Verifica eventos próximos y genera notificaciones.
        
        Args:
            horas_adelante: Horas hacia adelante para verificar
            
        Returns:
            List[Notificacion]: Lista de notificaciones generadas
        """
        notificaciones = []
        ahora = datetime.datetime.now()
        limite = ahora + datetime.timedelta(hours=horas_adelante)
        
        for evento in self.eventos_manager.eventos:
            try:
                fecha_evento = evento.get_fecha_objeto()
                
                if evento.hora:
                    # Evento con hora específica
                    hora_evento = evento.get_hora_objeto()
                    if hora_evento:
                        datetime_evento = datetime.datetime.combine(fecha_evento, hora_evento)
                        
                        if ahora <= datetime_evento <= limite:
                            tiempo_restante = datetime_evento - ahora
                            
                            if tiempo_restante.total_seconds() <= 3600:  # 1 hora
                                urgencia = 2
                                titulo = "🚨 Evento Muy Próximo"
                                tiempo_texto = self._formatear_tiempo_restante(tiempo_restante)
                            elif tiempo_restante.total_seconds() <= 86400:  # 24 horas
                                urgencia = 1
                                titulo = "⏰ Recordatorio de Evento"
                                tiempo_texto = self._formatear_tiempo_restante(tiempo_restante)
                            else:
                                urgencia = 0
                                titulo = "📅 Evento Próximo"
                                tiempo_texto = self._formatear_tiempo_restante(tiempo_restante)
                            
                            mensaje = f"'{evento.titulo}' comienza en {tiempo_texto}\n"
                            mensaje += f"📅 {formatear_fecha_completa(fecha_evento)}\n"
                            mensaje += f"🕒 {evento.hora}"
                            
                            if evento.descripcion:
                                mensaje += f"\n📝 {evento.descripcion[:100]}..."
                            
                            notificacion = Notificacion(
                                tipo='recordatorio',
                                titulo=titulo,
                                mensaje=mensaje,
                                evento=evento,
                                urgencia=urgencia
                            )
                            notificaciones.append(notificacion)
                else:
                    # Evento sin hora (todo el día)
                    if fecha_evento == ahora.date():
                        titulo = "📅 Evento de Hoy"
                        mensaje = f"Tienes el evento '{evento.titulo}' programado para hoy"
                        
                        if evento.descripcion:
                            mensaje += f"\n📝 {evento.descripcion[:100]}..."
                        
                        notificacion = Notificacion(
                            tipo='recordatorio',
                            titulo=titulo,
                            mensaje=mensaje,
                            evento=evento,
                            urgencia=0
                        )
                        notificaciones.append(notificacion)
            except:
                pass
        
        return notificaciones
    
    def verificar_eventos_hoy(self) -> List[Notificacion]:
        """
        Verifica eventos de hoy específicamente.
        
        Returns:
            List[Notificacion]: Notificaciones de eventos de hoy
        """
        return self.verificar_eventos_proximos(24)
    
    def generar_notificacion_conflicto(self, evento_nuevo: dict, eventos_conflicto: List[Evento]) -> Notificacion:
        """
        Genera una notificación de conflicto de horario.
        
        Args:
            evento_nuevo: Datos del evento nuevo
            eventos_conflicto: Lista de eventos en conflicto
            
        Returns:
            Notificacion: Notificación de conflicto
        """
        titulo = "⚠️ Conflicto de Horario Detectado"
        
        mensaje = f"El evento '{evento_nuevo['titulo']}' tiene un conflicto de horario:\n\n"
        mensaje += f"📅 Fecha: {evento_nuevo['fecha']}\n"
        mensaje += f"🕒 Hora: {evento_nuevo['hora']}\n\n"
        mensaje += "Eventos en conflicto:\n"
        
        for i, evento in enumerate(eventos_conflicto, 1):
            mensaje += f"{i}. '{evento.titulo}' a las {evento.hora}\n"
        
        mensaje += "\n¿Desea continuar de todas formas?"
        
        return Notificacion(
            tipo='conflicto',
            titulo=titulo,
            mensaje=mensaje,
            urgencia=2
        )
    
    def generar_notificacion_evento_pasado(self, evento: dict) -> Notificacion:
        """
        Genera una notificación para evento en el pasado.
        
        Args:
            evento: Datos del evento
            
        Returns:
            Notificacion: Notificación de advertencia
        """
        titulo = "⚡ Evento en el Pasado"
        mensaje = f"El evento '{evento['titulo']}' está programado en el pasado:\n\n"
        mensaje += f"📅 Fecha: {evento['fecha']}\n"
        
        if evento.get('hora'):
            mensaje += f"🕒 Hora: {evento['hora']}\n"
        
        mensaje += "\n¿Está seguro que desea crear este evento?"
        
        return Notificacion(
            tipo='warning',
            titulo=titulo,
            mensaje=mensaje,
            urgencia=1
        )
    
    def mostrar_notificacion(self, notificacion: Notificacion) -> None:
        """
        Muestra una notificación al usuario.
        
        Args:
            notificacion: Notificación a mostrar
        """
        # Reproducir sonido primero
        notificacion.reproducir_sonido()
        
        print(f"\n{notificacion.get_icono()} {notificacion.titulo}")
        print(f"   {notificacion.mensaje}")
        
        # Agregar a lista de notificaciones
        self.notificaciones.append(notificacion)
        
        # Llamar callback si existe
        if self.callback_mostrar_notificacion:
            self.callback_mostrar_notificacion(notificacion)
    
    def obtener_resumen_notificaciones(self) -> str:
        """
        Obtiene un resumen de notificaciones recientes.
        
        Returns:
            str: Resumen de notificaciones
        """
        if not self.notificaciones:
            return "No hay notificaciones recientes"
        
        resumen = f"📊 Resumen de Notificaciones ({len(self.notificaciones)}):\n\n"
        
        # Agrupar por tipo
        tipos = {}
        for notif in self.notificaciones:
            tipo = notif.tipo
            if tipo not in tipos:
                tipos[tipo] = []
            tipos[tipo].append(notif)
        
        for tipo, notifs in tipos.items():
            resumen += f"{notifs[0].get_icono()} {tipo.title()}: {len(notifs)}\n"
        
        return resumen
    
    def limpiar_notificaciones(self) -> None:
        """Limpia todas las notificaciones."""
        self.notificaciones.clear()
        print("🧹 Notificaciones limpiadas")
    
    def _formatear_tiempo_restante(self, tiempo_restante: datetime.timedelta) -> str:
        """
        Formatea el tiempo restante en formato legible.
        
        Args:
            tiempo_restante: Tiempo restante
            
        Returns:
            str: Tiempo formateado
        """
        segundos_totales = int(tiempo_restante.total_seconds())
        
        if segundos_totales < 3600:  # Menos de 1 hora
            minutos = segundos_totales // 60
            return f"{minutos} minuto(s)"
        elif segundos_totales < 86400:  # Menos de 1 día
            horas = segundos_totales // 3600
            minutos = (segundos_totales % 3600) // 60
            return f"{horas} hora(s) y {minutos} minuto(s)"
        else:  # 1 día o más
            dias = segundos_totales // 86400
            horas = (segundos_totales % 86400) // 3600
            return f"{dias} día(s) y {horas} hora(s)"
    
    def verificar_inicio_aplicacion(self) -> List[Notificacion]:
        """
        Verifica eventos al inicio de la aplicación.
        
        Returns:
            List[Notificacion]: Notificaciones de inicio
        """
        print("\n🔍 Verificando eventos próximos...")
        
        notificaciones_proximas = self.verificar_eventos_proximos(24)
        
        if notificaciones_proximas:
            print(f"📢 Se encontraron {len(notificaciones_proximas)} recordatorio(s)")
            for notif in notificaciones_proximas:
                self.mostrar_notificacion(notif)
        else:
            print("✅ No hay eventos próximos en las próximas 24 horas")
        
        return notificaciones_proximas
    
    def obtener_estadisticas_completas(self) -> dict:
        """
        Obtiene estadísticas completas del sistema.
        
        Returns:
            dict: Estadísticas completas
        """
        stats_eventos = self.eventos_manager.obtener_estadisticas()
        stats_validacion = self.validador.obtener_estadisticas_validacion()
        
        return {
            'eventos': stats_eventos,
            'validacion': stats_validacion,
            'notificaciones': {
                'total_notificaciones': len(self.notificaciones),
                'tipos_notificaciones': {
                    notif.tipo: len([n for n in self.notificaciones if n.tipo == notif.tipo])
                    for notif in self.notificaciones
                } if self.notificaciones else {}
            }
        } 