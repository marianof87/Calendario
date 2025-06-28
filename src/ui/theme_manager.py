"""
Theme_Manager.py - Gestor de temas para el sistema de calendario

Este módulo se encarga de:
- Gestión de temas disponibles en ttkbootstrap
- Aplicación dinámica de temas
- Organización de temas por categorías (claro/oscuro)
- Validación de temas

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from typing import List, Tuple, Optional


class ThemeManager:
    """
    Clase para gestionar todos los aspectos relacionados con temas.
    """
    
    def __init__(self):
        """Inicializa el gestor de temas."""
        self._init_temas()
        self.tema_actual = "litera"  # Tema por defecto
        self.style = None
        
    def _init_temas(self) -> None:
        """Inicializa las listas de temas disponibles."""
        # Temas claros - UI más clara y brillante
        self.temas_claros = [
            "litera", "cosmo", "flatly", "journal", "lumen", "minty", 
            "pulse", "sandstone", "united", "yeti", "morph", "simplex",
            "cerculean", "spacelab"
        ]
        
        # Temas oscuros - UI más oscura, mejor para ambiente con poca luz
        self.temas_oscuros = [
            "solar", "superhero", "darkly", "cyborg", "vapor", "slate"
        ]
        
        # Lista completa para combobox con separador visual
        self.temas_disponibles = self.temas_claros + ["---"] + self.temas_oscuros
    
    def get_temas_disponibles(self) -> List[str]:
        """
        Obtiene la lista completa de temas para el combobox.
        
        Returns:
            List[str]: Lista de temas con separador
        """
        return self.temas_disponibles
    
    def get_tema_actual(self) -> str:
        """
        Obtiene el tema actualmente en uso.
        
        Returns:
            str: Nombre del tema actual
        """
        return self.tema_actual
    
    def es_tema_valido(self, tema: str) -> bool:
        """
        Valida si un tema es válido (no es separador y existe).
        
        Args:
            tema: Nombre del tema a validar
            
        Returns:
            bool: True si el tema es válido
        """
        return tema != "---" and tema in (self.temas_claros + self.temas_oscuros)
    
    def es_tema_claro(self, tema: str) -> bool:
        """
        Determina si un tema es de tipo claro.
        
        Args:
            tema: Nombre del tema
            
        Returns:
            bool: True si es tema claro
        """
        return tema in self.temas_claros
    
    def es_tema_oscuro(self, tema: str) -> bool:
        """
        Determina si un tema es de tipo oscuro.
        
        Args:
            tema: Nombre del tema
            
        Returns:
            bool: True si es tema oscuro
        """
        return tema in self.temas_oscuros
    
    def get_tipo_tema(self, tema: str) -> str:
        """
        Obtiene el tipo de tema con emoji.
        
        Args:
            tema: Nombre del tema
            
        Returns:
            str: Tipo de tema con emoji
        """
        if self.es_tema_claro(tema):
            return "🌞 Claro"
        elif self.es_tema_oscuro(tema):
            return "🌙 Oscuro"
        else:
            return "❓ Desconocido"
    
    def inicializar_style(self, tema: str) -> tb.Style:
        """
        Inicializa el style con un tema específico.
        
        Args:
            tema: Nombre del tema a aplicar
            
        Returns:
            tb.Style: Objeto Style configurado
            
        Raises:
            ValueError: Si el tema no es válido
        """
        if not self.es_tema_valido(tema):
            raise ValueError(f"Tema '{tema}' no es válido")
            
        self.tema_actual = tema
        self.style = tb.Style(tema)
        return self.style
    
    def cambiar_tema(self, nuevo_tema: str) -> Tuple[bool, str]:
        """
        Cambia el tema de la aplicación.
        
        Args:
            nuevo_tema: Nombre del nuevo tema
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Validar que no sea el separador
        if nuevo_tema == "---":
            return False, "No se puede seleccionar el separador"
        
        # Validar que sea un tema válido
        if not self.es_tema_valido(nuevo_tema):
            return False, f"Tema '{nuevo_tema}' no es válido"
        
        # Si es el mismo tema, no hacer nada
        if nuevo_tema == self.tema_actual:
            return False, f"Ya está usando el tema '{nuevo_tema}'"
        
        # Aplicar el nuevo tema
        try:
            if self.style:
                self.style.theme_use(nuevo_tema)
            else:
                self.style = tb.Style(nuevo_tema)
            
            self.tema_actual = nuevo_tema
            tipo_tema = self.get_tipo_tema(nuevo_tema)
            mensaje = f"✅ Tema cambiado a: {nuevo_tema} ({tipo_tema})"
            
            return True, mensaje
            
        except Exception as e:
            # Si hay error, intentar crear nuevo style
            try:
                self.style = tb.Style(nuevo_tema)
                self.tema_actual = nuevo_tema
                tipo_tema = self.get_tipo_tema(nuevo_tema)
                mensaje = f"✅ Tema cambiado a: {nuevo_tema} ({tipo_tema}) [Reiniciado]"
                return True, mensaje
            except Exception as e2:
                return False, f"Error al cambiar tema: {str(e2)}"
    
    def get_titulo_con_tema(self, titulo_base: str) -> str:
        """
        Genera un título que incluye el tema actual.
        
        Args:
            titulo_base: Título base de la aplicación
            
        Returns:
            str: Título con información del tema
        """
        return f"{titulo_base} - Tema: {self.tema_actual.title()}"
    
    def get_info_tema_completa(self) -> dict:
        """
        Obtiene información completa del tema actual.
        
        Returns:
            dict: Información detallada del tema
        """
        return {
            'nombre': self.tema_actual,
            'tipo': self.get_tipo_tema(self.tema_actual),
            'es_claro': self.es_tema_claro(self.tema_actual),
            'es_oscuro': self.es_tema_oscuro(self.tema_actual),
            'total_temas': len(self.temas_claros) + len(self.temas_oscuros),
            'temas_claros_count': len(self.temas_claros),
            'temas_oscuros_count': len(self.temas_oscuros)
        } 