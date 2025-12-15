from datetime import date
from Modelo.Presupuesto import Presupuesto  # Ajusta la ruta según tu estructura

class Usuario:
    def __init__(self, ID_usuario: str, nombre: str, email: str, contrasenia: str):
        self.ID_usuario = ID_usuario
        self.nombre = nombre
        self.email = email
        self.contrasenia = contrasenia
        self.presupuestos = []  # Lista de objetos Presupuesto
        self.metas_financieras = []  # Lista de objetos MetaFinanciera
        self.transacciones = []  # Lista de objetos Transaccion

    def cambiar_contrasenia(self, contrasenia_nueva: str):
        self.contrasenia = contrasenia_nueva

    def crear_presupuesto(self, id_presupuesto: str, monto_limite: float, fecha_inicio: date, fecha_fin: date):
        nuevo_presupuesto = Presupuesto(id_presupuesto, monto_limite, fecha_inicio, fecha_fin, self.ID_usuario)
        self.presupuestos.append(nuevo_presupuesto)
