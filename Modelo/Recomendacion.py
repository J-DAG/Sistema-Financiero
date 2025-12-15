from datetime import date

class Recomendacion:
    def __init__(self, ID_recomendacion: str, ID_usuario: str, mensaje: str, fecha_generacion: date):
        self.ID_recomendacion = ID_recomendacion
        self.ID_usuario = ID_usuario
        self.mensaje = mensaje
        self.fecha_generacion = fecha_generacion

    def __str__(self):
        return f"[{self.fecha_generacion}] Recomendación para usuario {self.ID_usuario}: {self.mensaje}"
