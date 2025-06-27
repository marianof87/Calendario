"""
Main.py - Punto de entrada del sistema de calendario

Este módulo es el punto de entrada principal de la aplicación.
Solo se encarga de:
- Inicialización de la ventana principal
- Configuración inicial del tema
- Arranque de la aplicación

Toda la lógica está distribuida en módulos especializados:
- calendario_ui.py: Interfaz gráfica
- calendario_logic.py: Lógica del calendario
- theme_manager.py: Gestión de temas  
- helpers.py: Funciones de utilidad

Autor: Mariano Capella, Gabriel Osemberg
"""

import ttkbootstrap as tb
from calendario_ui import CalendarioUI


def main():
    """
    Función principal de la aplicación.
    
    Inicializa la ventana principal y arranca la aplicación.
    """
    # Crear ventana principal con tema por defecto
    root = tb.Window(themename="litera")
    
    # Configurar propiedades de la ventana
    root.geometry("800x600")  # Tamaño inicial
    root.minsize(600, 400)    # Tamaño mínimo
    
    # Crear la aplicación del calendario
    app = CalendarioUI(root)
    
    # Mostrar información inicial en consola
    print("🗓️  Sistema de Calendario iniciado")
    print("   Desarrollado por: Mariano Capella & Gabriel Osemberg")
    print("   Tecnologías: Python + ttkbootstrap")
    print(f"   Tema inicial: {app.get_theme_manager().get_tema_actual()}")
    print("   ¡Disfruta usando el calendario! 🎉")
    
    # Iniciar el loop principal de la aplicación
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        print("🔒 Cerrando sistema de calendario...")


if __name__ == "__main__":
    main()
