import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class CalendarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendario")
        self.style = tb.Style("litera")  # Podés cambiar el tema: cosmo, flatly, darkly, etc.

        self.hoy = datetime.date.today()
        self.fecha_actual = self.hoy.replace(day=1)

        self.crear_widgets()

    def crear_widgets(self):
        # Frame superior para la cabecera (mes, año y botones)
        top_frame = tb.Frame(self.root, padding=10)
        top_frame.pack(fill=X)

        # Botones de navegación
        btn_ano_ant = tb.Button(top_frame, text="<<", bootstyle=SECONDARY, command=self.ir_ano_anterior)
        btn_mes_ant = tb.Button(top_frame, text="<", bootstyle=SECONDARY, command=self.ir_mes_anterior)
        btn_hoy = tb.Button(top_frame, text="Hoy", bootstyle=INFO, command=self.ir_a_hoy)
        btn_mes_sig = tb.Button(top_frame, text=">", bootstyle=SECONDARY, command=self.ir_mes_siguiente)
        btn_ano_sig = tb.Button(top_frame, text=">>", bootstyle=SECONDARY, command=self.ir_ano_siguiente)

        btn_ano_ant.pack(side=LEFT, padx=5)
        btn_mes_ant.pack(side=LEFT, padx=5)
        btn_hoy.pack(side=LEFT, padx=5)
        btn_mes_sig.pack(side=LEFT, padx=5)
        btn_ano_sig.pack(side=LEFT, padx=5)

        # Etiqueta para mostrar mes y año
        self.label_fecha = tb.Label(top_frame, text=self.obtener_nombre_mes(), font=("Arial", 18, "bold"))
        self.label_fecha.pack(side=RIGHT)

        # Frame central para el calendario (a desarrollar en la próxima fase)
        self.frame_calendario = tb.Frame(self.root, padding=10)
        self.frame_calendario.pack(fill=BOTH, expand=True)

    def obtener_nombre_mes(self):
        return self.fecha_actual.strftime("%B %Y").capitalize()

    # Funciones de navegación (vacías por ahora)
    def ir_ano_anterior(self):
        pass

    def ir_ano_siguiente(self):
        pass

    def ir_mes_anterior(self):
        pass

    def ir_mes_siguiente(self):
        pass

    def ir_a_hoy(self):
        self.fecha_actual = self.hoy.replace(day=1)
        self.label_fecha.config(text=self.obtener_nombre_mes())

# Ejecutar la app
if __name__ == "__main__":
    root = tb.Window(themename="litera")  # podés probar otros: morph, cyborg, lumen...
    app = CalendarioApp(root)
    root.mainloop()
