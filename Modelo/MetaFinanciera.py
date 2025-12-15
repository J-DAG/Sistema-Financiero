from datetime import date

class MetaFinanciera:
    def __init__(self, ID_meta_financiera: str, nombre: str, monto_objetivo: float, monto_inicial: float, fecha_objetivo: date, usuario_id: str):
        print("DEBUG: Creando MetaFinanciera...")
        self.ID_meta_financiera = ID_meta_financiera
        self.nombre = nombre
        self.monto_objetivo = monto_objetivo
        self.fecha_objetivo = fecha_objetivo
        self.monto_actual = monto_inicial
        self.completada = False
        self.usuario_id = usuario_id
        self.historial_aportes = [(date.today(), monto_inicial)] if monto_inicial > 0 else []
        print("DEBUG: MetaFinanciera creada con éxito.")

    def agregar_progreso(self, monto, fecha):
        self.monto_actual += monto
        self.historial_aportes.append((fecha, monto))
        self.verificar_completada()

    def verificar_completada(self):
        """Verifica si la meta ha sido completada"""
        if self.monto_actual >= self.monto_objetivo:
            self.completada = True

    def calcular_porcentaje_progreso(self) -> float:
        if self.monto_objetivo == 0:
            return 0.0
        return (self.monto_actual / self.monto_objetivo) * 100

    def dias_restantes(self) -> int:
        dias = (self.fecha_objetivo - date.today()).days
        return max(0, dias)

    def get_historial_aportes(self):
        return self.historial_aportes

    def __str__(self) -> str:
        return (f"Meta: {self.nombre} - Objetivo: ${self.monto_objetivo:,.2f} - "
                f"Progreso: ${self.monto_actual:,.2f} ({self.calcular_porcentaje_progreso():.1f}%)")
