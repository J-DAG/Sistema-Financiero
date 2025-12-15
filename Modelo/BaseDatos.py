import os
import pickle
from datetime import date
from Modelo.Ingresos import Ingreso
from Modelo.MetaFinanciera import MetaFinanciera
from Modelo.Presupuesto import Presupuesto
from Modelo.Recomendacion import Recomendacion
from Modelo.TipoTransaccion import TipoTransaccion
from Modelo.Transaccion import Transaccion
from Modelo.Usuario import Usuario
from PyQt6.QtWidgets import QMessageBox

class BaseDatos:
    def __init__(self):
        self.usuario = None
        self.transacciones = []
        self.recomendaciones = []
        self.presupuestos = []
        self.ingresos = []
        self.metas = []

    ### --- Métodos de acceso a archivos separados ---
    def guardar_objeto(self, archivo, id_usuario, objeto):
        datos = {}
        if os.path.exists(archivo):
            with open(archivo, "rb") as f:
                datos = pickle.load(f)
        datos[id_usuario] = objeto
        with open(archivo, "wb") as f:
            pickle.dump(datos, f)

    def cargar_objeto(self, archivo, id_usuario):
        if not os.path.exists(archivo):
            return []
        with open(archivo, "rb") as f:
            datos = pickle.load(f)
        return datos.get(id_usuario, [])

    def guardar_todo(self):
        self.guardar_objeto("usuarios.dat", self.usuario.ID_usuario, self.usuario)
        self.guardar_objeto("transacciones.dat", self.usuario.ID_usuario, self.transacciones)
        self.guardar_objeto("ingresos.dat", self.usuario.ID_usuario, self.ingresos)
        self.guardar_objeto("metas.dat", self.usuario.ID_usuario, self.metas)
        self.guardar_objeto("presupuestos.dat", self.usuario.ID_usuario, self.presupuestos)
        self.guardar_objeto("recomendaciones.dat", self.usuario.ID_usuario, self.recomendaciones)
        print("Datos guardados exitosamente.")

    def cargar_todo(self, id_usuario):
        self.usuario = self.cargar_objeto("usuarios.dat", id_usuario)
        self.transacciones = self.cargar_objeto("transacciones.dat", id_usuario)
        self.ingresos = self.cargar_objeto("ingresos.dat", id_usuario)
        self.metas = self.cargar_objeto("metas.dat", id_usuario)
        self.presupuestos = self.cargar_objeto("presupuestos.dat", id_usuario)
        self.recomendaciones = self.cargar_objeto("recomendaciones.dat", id_usuario)

    ### --- Lógica de la aplicación ---
    def porcentaje_x_tipo_transaccion(self):
        total = sum(t.monto for t in self.transacciones if t.monto > 0)
        if total == 0:
            return {}

        conteo = {}
        for transaccion in self.transacciones:
            if transaccion.monto > 0:
                categoria = transaccion.categoria.value
                conteo[categoria] = conteo.get(categoria, 0) + transaccion.monto

        return {cat: (monto / total) * 100 for cat, monto in conteo.items()}

    def informe_saldos(self):
        ingresos_totales = sum(i.monto for i in self.ingresos)
        gastos_totales = sum(t.monto for t in self.transacciones)
        ahorros_totales = sum(meta.monto_actual for meta in self.metas)
        return {
            "ingresos_totales": ingresos_totales,
            "gastos_totales": gastos_totales,
            "ahorros_totales": ahorros_totales,
            "saldo_final": ingresos_totales - gastos_totales - ahorros_totales
        }

    def ingresar_transaccion(self, descripcion: str, fecha: date, monto: float, categoria, parent_widget=None):
        if not self.verificar_presupuesto(parent_widget):
            return
        transaccion = Transaccion(
            "T" + str(len(self.transacciones) + 1),
            descripcion,
            fecha,
            monto,
            categoria,
            self.usuario.ID_usuario
        )
        self.transacciones.append(transaccion)
        self.guardar_todas_las_transacciones()


    def guardar_todas_las_transacciones(self):
        archivo = "transacciones.dat"
        datos = {}
        if os.path.exists(archivo):
            with open(archivo, "rb") as f:
                datos = pickle.load(f)
        datos[self.usuario.ID_usuario] = self.transacciones
        with open(archivo, "wb") as f:
            pickle.dump(datos, f)
        print("Transacciones guardadas.")

    def cargar_transacciones(self):
        archivo = "transacciones.dat"
        if not os.path.exists(archivo):
            self.transacciones = []
            return
        with open(archivo, "rb") as f:
            todas_transacciones = pickle.load(f)
            # Filtra solo las transacciones del usuario actual
            self.transacciones = [t for t in todas_transacciones if t.usuario_id == self.usuario.ID_usuario]

    def registrar_ingreso(self, monto: float, fecha: date):
        if self.usuario is None:
            raise Exception("No hay usuario cargado para asociar el ingreso.")
        nuevo_ingreso = Ingreso(
            id_ingreso = "I" + str(len(self.ingresos) + 1),
            monto = monto,
            fecha = fecha,
            usuario_id = self.usuario.ID_usuario
        )
        self.ingresos.append(nuevo_ingreso)
        self.guardar_objeto("ingresos.dat", self.usuario.ID_usuario, self.ingresos)

    def ingresar_meta(self, nombre: str, monto_objetivo: float, monto_inicial: float, fecha_objetivo: date):
        if self.usuario is None:
            raise Exception("No hay usuario cargado para asociar la meta.")
        nueva_meta = MetaFinanciera(
            ID_meta_financiera = "M" + str(len(self.metas) + 1),
            nombre = nombre,
            monto_objetivo = monto_objetivo,
            monto_inicial = monto_inicial,
            fecha_objetivo = fecha_objetivo,
            usuario_id = self.usuario.ID_usuario
        )
        self.metas.append(nueva_meta)
        self.guardar_objeto("metas.dat", self.usuario.ID_usuario, self.metas)

    # Ejemplo para actualizar progreso en una meta
    def agregar_progreso_meta(self, id_meta: str, monto: float, fecha: date):
        for meta in self.metas:
            if meta.ID_meta_financiera == id_meta:
                meta.agregar_progreso(monto, fecha)
                self.guardar_objeto("metas.dat", self.usuario.ID_usuario, self.metas)
                break


    def ingresar_presupuesto(self, monto_limite: float, categoria: TipoTransaccion):
        nuevo_presupuesto = Presupuesto(
            id_presupuesto="P" + str(len(self.presupuestos) + 1),
            monto_limite=monto_limite,
            usuario_id=self.usuario.ID_usuario,
            categoria=categoria
        )
        self.presupuestos.append(nuevo_presupuesto)
        self.guardar_objeto("presupuestos.dat", self.usuario.ID_usuario, self.presupuestos)

    def agregar_recomendacion(self, mensaje: str):
        nueva_id = "R" + str(len(self.recomendaciones) + 1)
        recomendacion = Recomendacion(nueva_id, self.usuario.ID_usuario, mensaje, date.today())
        self.recomendaciones.append(recomendacion)
        self.guardar_objeto("recomendaciones.dat", self.usuario.ID_usuario, self.recomendaciones)

    def generar_recomendaciones_presupuesto(self):
        self.recomendaciones.clear()  # Limpiar anteriores

        gastos_por_categoria = {}
        for t in self.transacciones:
            categoria = t.categoria.value
            gastos_por_categoria[categoria] = gastos_por_categoria.get(categoria, 0) + abs(t.monto)

        for presupuesto in self.presupuestos:
            categoria = presupuesto.categoria.value
            monto_limite = presupuesto.monto_limite
            gasto_actual = gastos_por_categoria.get(categoria, 0)

            porcentaje_consumo = (gasto_actual / monto_limite) * 100 if monto_limite > 0 else 0

            if porcentaje_consumo >= 100:
                mensaje = f"¡Has superado el presupuesto para {categoria}! Gastaste {gasto_actual:.2f} y el límite es {monto_limite:.2f}."
                self.recomendaciones.append(Recomendacion("TEMP", self.usuario.ID_usuario, mensaje, date.today()))
            elif porcentaje_consumo >= 90:
                mensaje = f"Has alcanzado el 90% del presupuesto para {categoria}. Ten cuidado con los próximos gastos."
                self.recomendaciones.append(Recomendacion("TEMP", self.usuario.ID_usuario, mensaje, date.today()))
            elif porcentaje_consumo >= 80:
                mensaje = f"Has consumido el 80% del presupuesto para {categoria}. Considera revisar tus gastos."
                self.recomendaciones.append(Recomendacion("TEMP", self.usuario.ID_usuario, mensaje, date.today()))

        if gastos_por_categoria:
            categoria_mas_gasto = max(gastos_por_categoria, key=gastos_por_categoria.get)
            monto_mas_gasto = gastos_por_categoria[categoria_mas_gasto]
            mensaje = f"Estás gastando más en {categoria_mas_gasto} con un total de {monto_mas_gasto:.2f}."
            self.recomendaciones.append(Recomendacion("TEMP", self.usuario.ID_usuario, mensaje, date.today()))

    from datetime import timedelta

    def generar_notificaciones(self):
        notificaciones = []
        self.generar_recomendaciones_presupuesto()
        for rec in self.recomendaciones:
            notificaciones.append(f"💡 Recomendación: {rec.mensaje}")

        # Verificar metas
        hoy = date.today()
        for meta in self.metas:
            dias_restantes = (meta.fecha_objetivo - hoy).days
            if meta.monto_actual >= meta.monto_objetivo:
                notificaciones.append(f"🎉 ¡Meta lograda!: Has alcanzado el monto objetivo de '{meta.nombre}'.")
            elif 0 < dias_restantes <= 10:
                notificaciones.append(f"⏳ Meta próxima a vencer: Te quedan {dias_restantes} días para cumplir la meta '{meta.nombre}'.")

        return notificaciones

    def ingresar_usuario(self, ID_usuario: str, nombre: str, email: str, contrasenia: str, parent_widget=None):
        if os.path.exists("usuarios.dat"):
            with open("usuarios.dat", "rb") as f:
                usuarios = pickle.load(f)
            if ID_usuario in usuarios:
                QMessageBox.critical(parent_widget, "Error", "El usuario ya existe.")
                return False

        self.usuario = Usuario(ID_usuario, nombre, email, contrasenia)
        self.guardar_todo()
        QMessageBox.information(parent_widget, "Éxito", "Usuario creado correctamente.")
        return True

    @staticmethod

    def autenticar(ID_usuario: str, contrasenia: str):
        # Usuario por defecto: admin / admin
        if ID_usuario == "admin" and contrasenia == "admin":
            bd = BaseDatos()
            bd.usuario = Usuario("admin", "Administrador", "admin@correo.com", "admin")
            # Se asegura de crear listas vacías si no existen
            bd.transacciones = []
            bd.ingresos = []
            bd.presupuestos = []
            bd.metas = []
            bd.recomendaciones = []
            return bd, None

        if not os.path.exists("usuarios.dat"):
            return None, "No existen usuarios registrados."

        try:
            with open("usuarios.dat", "rb") as f:
                usuarios = pickle.load(f)
        except Exception as e:
            return None, f"Error al cargar usuarios: {e}"

        usuario = usuarios.get(ID_usuario)
        if not usuario:
            return None, "El usuario no existe."

        if usuario.contrasenia != contrasenia:
            return None, "Contraseña incorrecta."

        bd = BaseDatos()
        bd.cargar_todo(ID_usuario)
        return bd, None

    def verificar_presupuesto(self, parent_widget=None):
        if not self.presupuestos:
            if parent_widget:
                QMessageBox.warning(parent_widget, "Advertencia", "Debe registrar al menos un presupuesto antes de continuar.")
            return False
        return True
