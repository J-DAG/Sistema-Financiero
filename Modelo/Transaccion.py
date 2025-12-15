from datetime import date

from Modelo.TipoTransaccion import TipoTransaccion


class Transaccion:
    def __init__(self, id_transaccion: str, descripcion: str, fecha: date, monto: float, categoria: TipoTransaccion, usuario_id: str):
        self.id_transaccion = id_transaccion
        self.descripcion = descripcion
        self.fecha = fecha
        self.monto = monto
        self.categoria = categoria
        self.usuario_id = usuario_id

    def actualizar_monto(self, monto: float):
        self.monto = monto