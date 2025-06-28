"""
Notificacion_Timer.py - Timer optimizado para verificar eventos sin sobrecargar el sistema

Este módulo se ejecuta en segundo plano y verifica eventos de forma inteligente,
evitando sobrecargas durante eventos activos.

Autor: Mariano Capella, Gabriel Osemberg
"""

import threading
import time
import datetime
from typing import Callable, Optional, Set
from src.notifications.notificaciones import NotificacionesManager


class NotificacionTimer:
    """Timer optimizado que verifica eventos sin sobrecargar el sistema."""
    
    def __init__(self, notificaciones_manager: NotificacionesManager, main_window=None):
        """
        Inicializa el timer.
        
        Args:
            notificaciones_manager: Gestor de notificaciones
            main_window: Ventana principal para threading seguro
        """
        self.notificaciones_manager = notificaciones_manager
        self.main_window = main_window
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.interval = 60  # Verificar cada 60 segundos
        self.eventos_avisados_hoy: Set[str] = set()  # Eventos del día actual ya avisados
        
        # Protecciones contra sobrecarga
        self.evento_activo = False  # Flag para pausar durante eventos
        self.ultima_notificacion = 0  # Timestamp de última notificación
        self.min_intervalo_notificacion = 30  # Mínimo 30 segundos entre notificaciones
        self.pausado_hasta = 0  # Timestamp hasta cuando pausar
        
    def start(self) -> None:
        """Inicia el timer en segundo plano."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("🔔 Timer de notificaciones iniciado (versión optimizada)")
    
    def stop(self) -> None:
        """Detiene el timer."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️ Timer de notificaciones detenido")
    
    def _run(self) -> None:
        """Bucle principal del timer optimizado."""
        while self.running:
            try:
                # Verificar si estamos pausados
                if time.time() < self.pausado_hasta:
                    print(f"⏸️ Timer pausado hasta {datetime.datetime.fromtimestamp(self.pausado_hasta).strftime('%H:%M:%S')}")
                    time.sleep(30)  # Dormir menos cuando estamos pausados
                    continue
                
                # Verificar eventos de forma optimizada
                self._verificar_eventos_optimizado()
                
                # Dormir el intervalo completo
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"❌ Error en timer de notificaciones: {e}")
                time.sleep(self.interval)
    
    def _verificar_eventos_optimizado(self) -> None:
        """Verifica eventos de forma optimizada para evitar sobrecargas."""
        ahora = datetime.datetime.now()
        
        # Limpiar eventos avisados si cambió el día
        hoy_str = ahora.date().strftime("%Y-%m-%d")
        if not hasattr(self, '_ultimo_dia') or self._ultimo_dia != hoy_str:
            self.eventos_avisados_hoy.clear()
            self._ultimo_dia = hoy_str
            print("🧹 Nuevo día - limpiando eventos avisados")
        
        # Verificar protección contra spam
        if time.time() - self.ultima_notificacion < self.min_intervalo_notificacion:
            print(f"⏳ Esperando {self.min_intervalo_notificacion}s entre notificaciones")
            return
        
        print(f"🔍 Verificando eventos a las {ahora.strftime('%H:%M:%S')}")
        
        # Obtener solo eventos de hoy con hora
        eventos_hoy = []
        for evento in self.notificaciones_manager.eventos_manager.eventos:
            try:
                fecha_evento = evento.get_fecha_objeto()
                if fecha_evento == ahora.date() and evento.hora:
                    eventos_hoy.append(evento)
            except Exception:
                continue
        
        if not eventos_hoy:
            print("   📭 No hay eventos con hora para hoy")
            return
        
        print(f"   📋 Verificando {len(eventos_hoy)} eventos de hoy")
        
        # Verificar cada evento
        for evento in eventos_hoy:
            if self._verificar_evento_individual(evento, ahora):
                # Si encontramos un evento activo, pausar por un tiempo
                self._pausar_timer(5)  # Pausar 5 minutos
                break
    
    def _verificar_evento_individual(self, evento, ahora) -> bool:
        """
        Verifica un evento individual.
        
        Returns:
            bool: True si se activó una notificación
        """
        try:
            # Verificar si ya fue avisado hoy
            if evento.id in self.eventos_avisados_hoy:
                return False
            
            hora_evento = evento.get_hora_objeto()
            if not hora_evento:
                return False
                
            fecha_evento = evento.get_fecha_objeto()
            datetime_evento = datetime.datetime.combine(fecha_evento, hora_evento)
            diferencia_segundos = (datetime_evento - ahora).total_seconds()
            
            # Solo eventos que están ocurriendo AHORA (±2 minutos)
            if abs(diferencia_segundos) <= 120:  # 2 minutos de tolerancia
                print(f"🚨 ¡EVENTO ACTUAL! {evento.titulo}")
                self._enviar_notificacion_segura(evento)
                self.eventos_avisados_hoy.add(evento.id)
                self.ultima_notificacion = time.time()
                return True
                
        except Exception as e:
            print(f"❌ Error verificando evento '{evento.titulo}': {e}")
        
        return False
    
    def _pausar_timer(self, minutos: int) -> None:
        """Pausa el timer por un número específico de minutos."""
        self.pausado_hasta = time.time() + (minutos * 60)
        print(f"⏸️ Timer pausado por {minutos} minutos para evitar spam")
    
    def _enviar_notificacion_segura(self, evento) -> None:
        """Envía una notificación de forma segura y no bloqueante."""
        if self.main_window:
            # Programar en el hilo principal
            self.main_window.after(0, lambda: self._procesar_notificacion(evento))
        else:
            # Procesar directamente si no hay ventana principal
            self._procesar_notificacion(evento)
    
    def _procesar_notificacion(self, evento) -> None:
        """Procesa la notificación en el hilo principal."""
        try:
            from src.notifications.notificaciones import Notificacion
            
            print(f"🚨 Enviando notificación para: {evento.titulo}")
            
            notificacion = Notificacion(
                tipo='recordatorio',
                titulo='🚨 ¡EVENTO AHORA!',
                mensaje=f"'{evento.titulo}' está comenzando ahora\n🕒 {evento.hora}",
                evento=evento,
                urgencia=2  # Máxima urgencia
            )
            
            # Mostrar notificación
            self.notificaciones_manager.mostrar_notificacion(notificacion)
            
            # Reproducir sonido de forma no bloqueante
            threading.Thread(target=notificacion.reproducir_sonido, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error procesando notificación: {e}")
    
    def verificar_eventos_manualmente(self) -> None:
        """Fuerza una verificación manual de eventos."""
        print("🔍 Verificación manual de eventos solicitada")
        # Resetear protecciones para verificación manual
        self.pausado_hasta = 0
        self.ultima_notificacion = 0
        self._verificar_eventos_optimizado()
    
    def reanudar_timer(self) -> None:
        """Reanuda el timer si estaba pausado."""
        self.pausado_hasta = 0
        print("▶️ Timer reanudado manualmente")
    
    def limpiar_notificaciones_del_dia(self) -> None:
        """Limpia las notificaciones del día."""
        self.eventos_avisados_hoy.clear()
        print("🧹 Notificaciones del día limpiadas")
    
    def get_estadisticas(self) -> dict:
        """Obtiene estadísticas del timer."""
        ahora = time.time()
        return {
            'running': self.running,
            'interval_segundos': self.interval,
            'eventos_avisados_hoy': len(self.eventos_avisados_hoy),
            'total_eventos': len(self.notificaciones_manager.eventos_manager.eventos),
            'pausado': ahora < self.pausado_hasta,
            'segundos_hasta_reanudar': max(0, int(self.pausado_hasta - ahora)),
            'ultima_notificacion': datetime.datetime.fromtimestamp(self.ultima_notificacion).strftime('%H:%M:%S') if self.ultima_notificacion else 'Nunca'
        }
    
    def probar_notificacion(self) -> None:
        """Prueba las notificaciones con un evento ficticio."""
        try:
            print("🧪 Probando sistema de notificaciones...")
            
            # Crear evento ficticio para prueba
            class EventoPrueba:
                def __init__(self):
                    self.id = "test_notification"
                    self.titulo = "🧪 Prueba de Notificación"
                    self.hora = datetime.datetime.now().strftime("%H:%M")
            
            evento_prueba = EventoPrueba()
            
            # Resetear protecciones para la prueba
            self.ultima_notificacion = 0
            self.pausado_hasta = 0
            
            self._enviar_notificacion_segura(evento_prueba)
            print("✅ Notificación de prueba enviada")
            
        except Exception as e:
            print(f"❌ Error en prueba de notificación: {e}")
    
    def mostrar_estadisticas_detalladas(self) -> None:
        """Muestra estadísticas detalladas del sistema."""
        stats = self.get_estadisticas()
        print("\n📊 === ESTADÍSTICAS DEL TIMER OPTIMIZADO ===")
        print(f"🔄 Estado: {'🟢 Ejecutándose' if stats['running'] else '🔴 Detenido'}")
        print(f"⏱️ Intervalo: {stats['interval_segundos']} segundos")
        print(f"⏸️ Pausado: {'🟡 Sí' if stats['pausado'] else '🟢 No'}")
        
        if stats['pausado']:
            print(f"⏳ Reanudar en: {stats['segundos_hasta_reanudar']} segundos")
            
        print(f"🚨 Eventos avisados hoy: {stats['eventos_avisados_hoy']}")
        print(f"📋 Total eventos: {stats['total_eventos']}")
        print(f"🕐 Última notificación: {stats['ultima_notificacion']}")
        
        if self.eventos_avisados_hoy:
            print(f"🗂️ IDs avisados: {', '.join(list(self.eventos_avisados_hoy)[:5])}")
        else:
            print("📭 Ningún evento avisado hoy")
            
        print("=" * 45) 