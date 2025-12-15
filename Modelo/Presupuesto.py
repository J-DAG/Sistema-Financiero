from datetime import date

from Modelo.TipoTransaccion import TipoTransaccion


class Presupuesto:
    def __init__(self, id_presupuesto: str, monto_limite: float, usuario_id: str,categoria: TipoTransaccion):
        self.id_presupuesto = id_presupuesto
        self.monto_limite = monto_limite
        self.gastado = 0.0
        self.categoria = categoria
        self.usuario_id = usuario_id

    def agregar_gasto(self, monto: float):
        self.gastado += monto

    def actualizar_monto_limite(self, monto: float):
        self.monto_limite = monto

    def porcentaje_monto_ocupado(self):
        if self.monto_limite == 0:
            return 0.0
        return (self.gastado * 100) / self.monto_limite

    def __str__(self):
        return (f"Presupuesto: límite ${self.monto_limite:.2f}, gastado ${self.gastado:.2f} "
                f"({self.porcentaje_monto_ocupado():.1f}%)")

