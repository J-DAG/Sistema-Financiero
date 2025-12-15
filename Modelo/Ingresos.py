from datetime import date


class Ingreso:
    def __init__(self,id_ingreso: str,monto:float,fecha:date,usuario_id:str):
        self.id_ingreso = id_ingreso
        self.monto = monto
        self.fecha = fecha
        self.usuario_id = usuario_id