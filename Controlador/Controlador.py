import sys
import re
import matplotlib
import calendar
from Modelo.TipoTransaccion import TipoTransaccion
from Vista.VMenuPrincipal import Ui_MenuPrincipal
from Vista.VNotificaiones import Ui_FormNotificaciones

matplotlib.use("QtAgg")

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QDialog
from PyQt6.uic.properties import QtCore
from enum import Enum
from Modelo.BaseDatos import BaseDatos
from Vista.VCrearCuenta import Ui_FormRegistrarUsuario
from Vista.VGastos import Ui_FormGastos
from Vista.VIngresos import Ui_FormIngresos
from Vista.VInicioSesion import Ui_InicioSesion
from Vista.VMetas import Ui_FormMetas
from Vista.VPresupuesto import Ui_FormPresupuesto
from Vista.VRecomendaciones import Ui_FormRecomendaciones
from Vista.VSaldos import Ui_FormSaldos
from Vista.VUsuarioAutenticado import Ui_FormVentanaPrincipal
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionProgressBar
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ControlInicioSesion(QtWidgets.QMainWindow, Ui_InicioSesion):
    def __init__(self, parent=None):
        super(ControlInicioSesion, self).__init__(parent)
        self.setupUi(self)
        self.btnCrearCuenta.clicked.connect(self.crear_cuenta)
        self.btnIniciarSesion.clicked.connect(self.iniciar_sesion)

    def crear_cuenta(self):
        self.vl = ControlCrearCuenta()
        self.vl.show()
        self.close()

    def iniciar_sesion(self):
        usuario = self.textUsuario.text().strip()
        clave = self.txtClave.text().strip()

        if not usuario or not clave:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, ingrese usuario y contraseña.")
            return

        bd, error = BaseDatos.autenticar(usuario, clave)

        if error:
            QMessageBox.critical(self, "Error", error)
            return

        QMessageBox.information(self, "Éxito", "Autenticación exitosa.")
        self.vlista = ControlOperaciones(bd)
        self.vlista.show()
        self.close()

class ControlCrearCuenta(QtWidgets.QWidget, Ui_FormRegistrarUsuario):
    def __init__(self, parent=None):
        super(ControlCrearCuenta, self).__init__(parent)
        self.setupUi(self)

        # Validadores
        solo_letras = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]*$"))
        solo_numeros = QIntValidator(0, 999999999)

        # Aplica los validadores
        self.txtNombre.setValidator(solo_letras)
        self.txtApellidos.setValidator(solo_letras)
        self.txtCedula.setValidator(solo_numeros)
        self.txtIngresoMensual.setValidator(solo_numeros)

        self.pushButton.clicked.connect(self.registrar_usuario)
        self.pushButton_2.clicked.connect(self.close)

    def closeEvent(self, event):
        self.ventana_login = ControlInicioSesion()
        self.ventana_login.show()
        event.accept()

    def cedula_valida(self, cedula):
        if len(cedula) != 10 or not cedula.isdigit():
            return False

        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24:
            return False

        digitos = list(map(int, cedula))
        verificador = digitos.pop()

        suma = 0
        for i in range(9):
            num = digitos[i]
            if i % 2 == 0:
                num *= 2
                if num > 9:
                    num -= 9
            suma += num

        calculado = 10 - (suma % 10) if (suma % 10) != 0 else 0
        return calculado == verificador

    def registrar_usuario(self):
        nombre = self.txtNombre.text().strip()
        apellidos = self.txtApellidos.text().strip()
        cedula = self.txtCedula.text().strip()
        correo = self.txtCorreo.text().strip()
        contrasenia = self.txtContrasenia.text()
        confirmacion = self.txtConfirmacionContrasenia.text()
        ingreso = self.txtIngresoMensual.text().strip()

        solo_letras = re.compile(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ ]+$')
        solo_numeros = re.compile(r'^\d+$')

        if not all([nombre, apellidos, cedula, correo, contrasenia, confirmacion, ingreso]):
            QtWidgets.QMessageBox.warning(self, "Campos incompletos", "Por favor, completa todos los campos.")
            return

        if not solo_letras.match(nombre):
            QtWidgets.QMessageBox.warning(self, "Nombre inválido", "El nombre solo debe contener letras.")
            return

        if not solo_letras.match(apellidos):
            QtWidgets.QMessageBox.warning(self, "Apellidos inválidos", "Los apellidos solo deben contener letras.")
            return

        if not solo_numeros.match(cedula):
            QtWidgets.QMessageBox.warning(self, "Cédula inválida", "La cédula solo debe contener números.")
            return

        if not self.cedula_valida(cedula):
            QtWidgets.QMessageBox.warning(self, "Cédula inválida", "La cédula ingresada no es válida.")
            return

        if contrasenia != confirmacion:
            QtWidgets.QMessageBox.warning(self, "Contraseña", "Las contraseñas no coinciden.")
            return

        if not solo_numeros.match(ingreso):
            QtWidgets.QMessageBox.warning(self, "Ingreso inválido", "El ingreso mensual debe ser un número.")
            return

        # Crear usuario y guardar en archivo .dat
        bd = BaseDatos()
        creado = bd.ingresar_usuario(cedula, nombre + " " + apellidos, correo, contrasenia)

        if creado:
            QtWidgets.QMessageBox.information(self, "Éxito", "Usuario registrado correctamente. Empecemos con tu planificacion de presupuesto.")
            self.ventana_login = ControlInicioSesion()
            self.ventana_login.show()
            self.close()

        else:
            QtWidgets.QMessageBox.critical(self, "Error", "El usuario ya existe.")

class ControlOperaciones(QtWidgets.QMainWindow, Ui_MenuPrincipal):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlOperaciones, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo

        self.btnSaldo.clicked.connect(self.ver_saldos)
        self.btnIngresos.clicked.connect(self.ver_ingresos)
        self.btnGastos.clicked.connect(self.ver_gastos)
        self.btnMetas.clicked.connect(self.ver_metas)
        self.btnPresupuesto.clicked.connect(self.ver_presupuesto)
        self.btnRecomendaciones.clicked.connect(self.ver_recomendaciones)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnNotificiones.clicked.connect(self.ver_notificaciones)

        #botones accion
        self.actionSaldos.triggered.connect(self.ver_saldos)
        self.actionIngresos.triggered.connect(self.ver_ingresos)
        self.actionGastos.triggered.connect(self.ver_gastos)
        self.actionMetas.triggered.connect(self.ver_metas)
        self.actionPresupuesto.triggered.connect(self.ver_presupuesto)
        self.actionRecomendacion.triggered.connect(self.ver_recomendaciones)
        self.actionNotificaciones.triggered.connect(self.ver_notificaciones)


        if modelo:
            self.setWindowTitle(f"Bienvenido, {modelo.usuario.nombre}")
            self.lblNombreUsuario.setText(modelo.usuario.nombre)
            self.mostrar_grafico_pastel()
            self.graficar_ingresos_por_mes()
            self.cargar_gastos_en_tabla()

    def mostrar_grafico_pastel(self):
        datos = self.modelo.porcentaje_x_tipo_transaccion()

        if not datos:
            QtWidgets.QMessageBox.information(self, "Sin datos", "No hay datos suficientes para generar el gráfico.")
            return

        categorias = list(datos.keys())
        porcentajes = list(datos.values())

        # Crear figura
        figura = Figure(figsize=(4, 4))
        canvas = FigureCanvas(figura)
        ax = figura.add_subplot(111)
        ax.pie(porcentajes, labels=categorias, autopct='%1.1f%%', startangle=140)
        ax.set_title("Distribución de gastos por categoría")

        # Limpiar layout anterior y añadir canvas
        layout = self.widgetGastos.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.widgetGastos)
            self.widgetGastos.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)

                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        layout.addWidget(canvas)

    def graficar_ingresos_por_mes(self):
        try:
            if self.widgetEvolucionSaldo.layout() is None:
                self.widgetEvolucionSaldo.setLayout(QtWidgets.QVBoxLayout())

            ingresos_por_mes = defaultdict(float)
            for ingreso in self.modelo.ingresos:
                mes = ingreso.fecha.month
                ingresos_por_mes[mes] += ingreso.monto

            meses = list(range(1, 13))
            montos = [ingresos_por_mes.get(m, 0) for m in meses]
            nombres_meses = [calendar.month_abbr[m] for m in meses]

            fig = Figure(figsize=(6, 4))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.bar(nombres_meses, montos, color='skyblue')
            #ax.set_title("Ingresos por mes")
            ax.set_ylabel("Monto")
            #ax.set_xlabel("Mes")

            layout = self.widgetEvolucionSaldo.layout()
            # Limpiar el layout actual (si hay gráficos previos)
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            layout.addWidget(canvas)
            canvas.draw()

            print("Gráfico generado correctamente.")

        except Exception as e:
            print("Error en graficar_ingresos_por_mes:", e)

    def cargar_gastos_en_tabla(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Descripcion", "Fecha", "Monto", "Categoria"])
        print("Cargando gastos:")
        for i, gasto in enumerate(self.modelo.transacciones):
            print(f"[{i}] →", gasto)
            try:
                item_id = QStandardItem(str(gasto.id_transaccion))
                item_descripcion = QStandardItem(gasto.descripcion)
                item_fecha = QStandardItem(gasto.fecha.strftime("%d/%m/%Y"))
                item_monto = QStandardItem(f"{gasto.monto:.2f}")
                item_categoria = QStandardItem(gasto.categoria.value)

                for item in [item_id, item_descripcion, item_fecha, item_monto, item_categoria]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([item_id, item_descripcion, item_fecha, item_monto, item_categoria])
            except Exception as e:
                print("ERROR al cargar los gastos:", e)

        self.tableTransacciones.setModel(model)
        self.tableTransacciones.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableTransacciones.resizeRowsToContents()

    def cerrar_sesion(self):
        self.ventana_login = ControlInicioSesion()
        self.ventana_login.show()
        self.close()

    def ver_saldos(self):
        self.ventana_saldos = ControlSaldos(self.modelo)
        self.ventana_saldos.show()
        self.close()

    def ver_ingresos(self):
        self.ventana_ingresos = ControlIngresos(self.modelo)
        self.ventana_ingresos.show()
        self.close()

    def ver_gastos(self):
        self.ventana_gastos = ControlGastos(self.modelo)
        self.ventana_gastos.show()
        self.close()

    def ver_metas(self):
        self.ventana_metas = ControlMetas(self.modelo)
        self.ventana_metas.show()
        self.close()

    def ver_presupuesto(self):
        self.ventana_presupuesto = ControlPresupuesto(self.modelo)
        self.ventana_presupuesto.show()
        self.close()

    def ver_recomendaciones(self):
        self.ventana_recomendaciones = ControlRecomendaciones(self.modelo)
        self.ventana_recomendaciones.show()
        self.close()

    def ver_notificaciones(self):
        self.ventana_notificaciones = ControlNotificaciones(self.modelo)
        self.ventana_notificaciones.show()
        self.close()

class ControlSaldos(QtWidgets.QWidget, Ui_FormSaldos):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlSaldos, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo
        self.pushButton.clicked.connect(self.inicio_opciones)
        self.iniciar_datos()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def iniciar_datos(self):
        datos = self.modelo.informe_saldos()
        ingresos = datos["ingresos_totales"]
        gastos = datos["gastos_totales"]
        ahorros = datos["ahorros_totales"]
        saldo = datos["saldo_final"]
        self.txtIngresos.setText(f"{ingresos:.2f}")
        self.txtGastos.setText(f"{gastos:.2f}")
        self.txtAhorrado.setText(f"{ahorros:.2f}")
        self.txtSaldoActual.setText(f"{saldo:.2f}")

class ControlIngresos(QtWidgets.QWidget,Ui_FormIngresos):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlIngresos, self).__init__(parent)
        self.modelo = modelo
        self.setupUi(self)
        self.btnAnadirIngresos.clicked.connect(self.registrar_ingreso)
        self.cargar_ingresos_en_tabla()
        self.graficar_ingresos_por_mes()
        self.pushButton.clicked.connect(self.inicio_opciones)

        if self.modelo.usuario:
            self.setWindowTitle(f"Ingresos - {self.modelo.usuario.nombre}")

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def graficar_ingresos_por_mes(self):

        try:
            if self.widgetEvolucionSaldo.layout() is None:
                self.widgetEvolucionSaldo.setLayout(QtWidgets.QVBoxLayout())

            ingresos_por_mes = defaultdict(float)
            for ingreso in self.modelo.ingresos:
                mes = ingreso.fecha.month
                ingresos_por_mes[mes] += ingreso.monto

            meses = list(range(1, 13))
            montos = [ingresos_por_mes.get(m, 0) for m in meses]
            nombres_meses = [calendar.month_abbr[m] for m in meses]

            fig = Figure(figsize=(6, 4))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.bar(nombres_meses, montos, color='skyblue')
            #ax.set_title("Ingresos por mes")
            ax.set_ylabel("Monto")
            #ax.set_xlabel("Mes")

            layout = self.widgetEvolucionSaldo.layout()
            # Limpiar el layout actual (si hay gráficos previos)
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            layout.addWidget(canvas)
            canvas.draw()

            print("Gráfico generado correctamente.")

        except Exception as e:
            print("Error en graficar_ingresos_por_mes:", e)

    def cargar_ingresos_en_tabla(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Monto", "Fecha"])

        print("Cargando ingresos:")
        for i, ingreso in enumerate(self.modelo.ingresos):
            print(f"[{i}] →", ingreso)
            try:
                item_id = QStandardItem(str(ingreso.id_ingreso))
                item_monto = QStandardItem(f"{ingreso.monto:.2f}")
                item_fecha = QStandardItem(ingreso.fecha.strftime("%d/%m/%Y"))
                #item_fecha = QStandardItem(ingreso.fecha.toPyDate().strftime("%d/%m/%Y"))

                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_monto.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([item_id, item_monto, item_fecha])
            except Exception as e:
                print("ERROR cargando ingreso:", e)

        self.tableHistorialIngresos.setModel(model)
        self.tableHistorialIngresos.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableHistorialIngresos.resizeRowsToContents()

    def registrar_ingreso(self):
        dialogo = VistaRegistrarIngreso(self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            monto = dialogo.monto           # tipo float
            fecha = dialogo.fecha           # tipo QDate

            print("Monto:", monto)
            print("Fecha:", fecha.toString("dd/MM/yyyy"))

            self.modelo.registrar_ingreso(monto, fecha.toPyDate())  # Usa fecha como date
            self.modelo.guardar_todo()
            QtWidgets.QMessageBox.information(self, "Éxito", "Ingreso registrado correctamente.")
            self.cargar_ingresos_en_tabla()  # Refresca tabla
            self.graficar_ingresos_por_mes()

class ControlGastos(QtWidgets.QWidget, Ui_FormGastos):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlGastos, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo

        # Configurar selección de tabla
        self.tableGastos.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.tableGastos.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        self.pushButton.clicked.connect(self.inicio_opciones)
        self.btnAnadirGasto.clicked.connect(self.registrar_gasto)
        self.brnModificar.clicked.connect(self.modificar_gasto)
        self.btnEliminar.clicked.connect(self.eliminar_gasto)

        self.cargar_gastos_en_tabla()
        self.mostrar_grafico_pastel()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def cargar_gastos_en_tabla(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Descripcion", "Fecha", "Monto", "Categoria"])

        print("Cargando gastos:")
        for i, gasto in enumerate(self.modelo.transacciones):
            print(f"[{i}] →", gasto)
            try:
                item_id = QStandardItem(str(gasto.id_transaccion))
                item_descripcion = QStandardItem(gasto.descripcion)
                item_fecha = QStandardItem(gasto.fecha.strftime("%d/%m/%Y"))
                item_monto = QStandardItem(f"{gasto.monto:.2f}")
                item_categoria = QStandardItem(gasto.categoria.value)

                for item in [item_id, item_descripcion, item_fecha, item_monto, item_categoria]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([item_id, item_descripcion, item_fecha, item_monto, item_categoria])
            except Exception as e:
                print("ERROR al cargar los gastos:", e)

        self.tableGastos.setModel(model)
        self.tableGastos.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableGastos.resizeRowsToContents()

    def modificar_gasto(self):
        seleccion = self.tableGastos.selectionModel().selectedRows()
        print("Filas seleccionadas:", seleccion)

        if not seleccion:
            QtWidgets.QMessageBox.warning(self, "Atención", "Seleccione el gasto a modificar.")
            return

        fila = seleccion[0].row()
        gasto = self.modelo.transacciones[fila]

        dialogo = VistaModificarGasto(TipoTransaccion, gasto, self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            gasto.descripcion = dialogo.descripcion
            gasto.monto = dialogo.monto
            gasto.fecha = dialogo.fecha.toPyDate()
            gasto.categoria = dialogo.categoria

            self.modelo.guardar_todo()
            QtWidgets.QMessageBox.information(self, "Éxito", "Gasto modificado correctamente.")
            self.cargar_gastos_en_tabla()
            self.mostrar_grafico_pastel()

    def registrar_gasto(self):
        dialogo = VistaRegistrarGasto(TipoTransaccion, self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            descripcion = dialogo.descripcion
            monto = dialogo.monto
            fecha = dialogo.fecha.toPyDate()
            categoria = dialogo.categoria
            self.modelo.ingresar_transaccion(descripcion, fecha, monto, categoria)
            QtWidgets.QMessageBox.information(self, "Éxito", "Gasto registrado correctamente.")
            self.cargar_gastos_en_tabla()
            self.mostrar_grafico_pastel()

    def eliminar_gasto(self):
        seleccion = self.tableGastos.selectionModel().selectedRows()
        if not seleccion:
            QtWidgets.QMessageBox.warning(self, "Atención", "Seleccione el gasto que deseas eliminar.")
            return

        fila = seleccion[0].row()
        gasto = self.modelo.transacciones[fila]

        confirmacion = QtWidgets.QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el gasto:\n\nDescripción: {gasto.descripcion}\nMonto: {gasto.monto:.2f}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirmacion == QtWidgets.QMessageBox.StandardButton.Yes:
            self.modelo.transacciones.remove(gasto)
            self.modelo.guardar_todo()
            self.cargar_gastos_en_tabla()
            self.mostrar_grafico_pastel()
            QtWidgets.QMessageBox.information(self, "Eliminado", "Gasto eliminado correctamente.")

    def mostrar_grafico_pastel(self):
        datos = self.modelo.porcentaje_x_tipo_transaccion()

        if not datos:
            QtWidgets.QMessageBox.information(self, "Sin datos", "No hay datos suficientes para generar el gráfico.")
            return

        categorias = list(datos.keys())
        porcentajes = list(datos.values())

        # Crear figura
        figura = Figure(figsize=(4, 4))
        canvas = FigureCanvas(figura)
        ax = figura.add_subplot(111)
        ax.pie(porcentajes, labels=categorias, autopct='%1.1f%%', startangle=140)
        ax.set_title("Distribución de gastos por categoría")

        # Limpiar layout anterior y añadir canvas
        layout = self.widgetGastos.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.widgetGastos)
            self.widgetGastos.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        layout.addWidget(canvas)

class ControlMetas(QtWidgets.QWidget,Ui_FormMetas):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlMetas, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo
        self.pushButton.clicked.connect(self.inicio_opciones)
        self.btnNuevaMeta.clicked.connect(self.ingresar_meta)
        self.brnModificar.clicked.connect(self.modificar_meta)
        self.btnAcatualizar.clicked.connect(self.actualizar_estado_meta)
        self.actualizar_tabla()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def ingresar_meta(self):
        dialogo = VistaRegistrarMeta(self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            titulo = dialogo.titulo
            monto_objetivo = dialogo.monto_objetivo
            monto_inicial = dialogo.monto_inicial
            fecha_limite = dialogo.fecha_limite.toPyDate()

            print("DEBUG - Título:", titulo)
            print("DEBUG - Monto objetivo:", monto_objetivo, type(monto_objetivo))
            print("DEBUG - Monto inicial:", monto_inicial, type(monto_inicial))
            print("DEBUG - Fecha límite:", fecha_limite)
            self.modelo.ingresar_meta(titulo, monto_objetivo, monto_inicial, fecha_limite)
            self.modelo.guardar_todo()
            self.actualizar_tabla()

    def modificar_meta(self):
        index = self.tableMetas.currentIndex()
        if not index.isValid():
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una meta para modificar.")
            return

        fila = index.row()
        meta = self.modelo.metas[fila]

        dialogo = VistaModificarMeta(meta, self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            meta.nombre = dialogo.titulo
            meta.monto_objetivo = dialogo.monto_objetivo
            meta.fecha_objetivo = dialogo.fecha_limite
            self.modelo.guardar_todo()
            self.actualizar_tabla()

    def actualizar_estado_meta(self):
        index = self.tableMetas.currentIndex()
        if not index.isValid():
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una meta para actualizar.")
            return

        fila = index.row()
        meta = self.modelo.metas[fila]

        dialogo = VistaActualizarMontoMeta(meta, self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            meta.monto_actual = dialogo.nuevo_monto_actual
            self.modelo.guardar_todo()
            self.actualizar_tabla()

    def actualizar_tabla(self):
        metas = self.modelo.metas
        self.modelo_tabla = MetasTableModel(metas)
        self.tableMetas.setModel(self.modelo_tabla)

        # Ajustar columnas para mejor vista
        self.tableMetas.resizeColumnsToContents()
        self.tableMetas.setColumnWidth(5, 150)  # Barra progreso un poco más ancha
        self.tableMetas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    # Asignar el delegado a la columna 5 (progreso)
        delegate = ProgressBarDelegate(self.tableMetas)
        self.tableMetas.setItemDelegateForColumn(5, delegate)

class ControlPresupuesto(QtWidgets.QWidget,Ui_FormPresupuesto):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlPresupuesto, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo

        self.tablePresupuesto.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.tablePresupuesto.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        self.pushButton.clicked.connect(self.inicio_opciones)
        self.btnAgregar.clicked.connect(self.ingresar_presupuesto)
        self.btnEliminar.clicked.connect(self.eliminar_presupuesto)
        self.brnModificar.clicked.connect(self.modificar_presupuesto)
        self.cargar_tabla_presupuestos()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def modificar_presupuesto(self):
        seleccion = self.tablePresupuesto.selectionModel().selectedRows()
        if not seleccion:
            QtWidgets.QMessageBox.warning(self, "Atención", "Seleccione el presupuesto a modificar.")
            return

        fila = seleccion[0].row()
        presupuesto = self.modelo.presupuestos[fila]

        dialogo = VistaModificarPresupuesto(TipoTransaccion, presupuesto, self)
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            presupuesto.monto_limite = dialogo.monto
            presupuesto.categoria = dialogo.categoria

            self.modelo.guardar_todo()
            QtWidgets.QMessageBox.information(self, "Éxito", "Presupuesto modificado correctamente.")
            self.cargar_tabla_presupuestos()

    def ingresar_presupuesto(self):
        dialogo = VistaRegistrarPresupuesto(TipoTransaccion)  # si usas Enum
        if dialogo.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            monto = dialogo.monto_limite
            categoria = dialogo.categoria
            self.modelo.ingresar_presupuesto(monto, categoria)
            self.modelo.guardar_todo()
            QtWidgets.QMessageBox.information(self, "Éxito", "Presupuesto registrado correctamente.")
            self.cargar_tabla_presupuestos()

    def cargar_tabla_presupuestos(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "Categoria", "Monto"])
        print("Cargando presupuestos:")
        for i, presupuesto in enumerate(self.modelo.presupuestos):
            print(f"[{i}] →", presupuesto)
            try:
                item_id = QStandardItem(str(presupuesto.id_presupuesto))
                item_categoria = QStandardItem(presupuesto.categoria.value)
                item_monto = QStandardItem(f"{presupuesto.monto_limite:.2f}")

                for item in [item_id, item_categoria, item_monto]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                model.appendRow([item_id, item_categoria, item_monto])
            except Exception as e:
                print("ERROR al cargar los gastos:", e)

        self.tablePresupuesto.setModel(model)
        self.tablePresupuesto.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tablePresupuesto.resizeRowsToContents()

    def eliminar_presupuesto(self):
        seleccion = self.tablePresupuesto.selectionModel().selectedRows()
        if not seleccion:
            QtWidgets.QMessageBox.warning(self, "Atención", "Seleccione el presupuesto que desea eliminar.")
            return

        fila = seleccion[0].row()
        presupuesto = self.modelo.presupuestos[fila]

        confirmacion = QtWidgets.QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el presupuesto:\n\nCategoría: {presupuesto.categoria.value}\nMonto: {presupuesto.monto_limite:.2f}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirmacion == QtWidgets.QMessageBox.StandardButton.Yes:
            self.modelo.presupuestos.remove(presupuesto)
            self.modelo.guardar_todo()
            self.cargar_tabla_presupuestos()
            QtWidgets.QMessageBox.information(self, "Eliminado", "Presupuesto eliminado correctamente.")


class ControlRecomendaciones(QtWidgets.QWidget,Ui_FormRecomendaciones):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlRecomendaciones, self).__init__(parent)
        self.modelo = modelo
        self.setupUi(self)
        self.pushButton.clicked.connect(self.inicio_opciones)
        self.mostrar_recomendaciones()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def mostrar_recomendaciones(self):
        self.modelo.generar_recomendaciones_presupuesto()
        recomendaciones = self.modelo.recomendaciones
        print(f"Recomendaciones generadas: {len(recomendaciones)}")
        print(f"RECOMENDACIONES GENERADAS:")
        for r in self.modelo.recomendaciones:
            print("→", r.mensaje)
        # Obtenemos o creamos el layout del widget de recomendaciones
        layout = self.widgetRecomendaciones.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.widgetRecomendaciones)
            self.widgetRecomendaciones.setLayout(layout)
        else:
            # Limpiar contenido anterior
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        # Si no hay recomendaciones
        if not recomendaciones:
            etiqueta = QtWidgets.QLabel("No hay recomendaciones en este momento.")
            etiqueta.setStyleSheet("font-size: 14px; color: gray;")
            layout.addWidget(etiqueta)
            return

        # Añadir cada recomendación como QLabel al layout
        for rec in recomendaciones:
            etiqueta = QtWidgets.QLabel(f"• {rec.mensaje}")
            etiqueta.setWordWrap(True)
            etiqueta.setStyleSheet("font-size: 14px; padding: 4px; color: #333;")
            layout.addWidget(etiqueta)

class ControlNotificaciones(QtWidgets.QWidget,Ui_FormNotificaciones):
    def __init__(self, modelo: BaseDatos, parent=None):
        super(ControlNotificaciones, self).__init__(parent)
        self.setupUi(self)
        self.modelo = modelo
        self.pushButton.clicked.connect(self.inicio_opciones)
        self.mostrar_notificaciones()

    def inicio_opciones(self):
        self.ventana_login = ControlOperaciones(self.modelo)
        self.ventana_login.show()
        self.close()

    def mostrar_notificaciones(self):
        notificaciones = self.modelo.generar_notificaciones()

        layout = self.widgetNotificaciones.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(self.widgetNotificaciones)
            self.widgetNotificaciones.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        if not notificaciones:
            etiqueta = QtWidgets.QLabel("No hay notificaciones en este momento.")
            etiqueta.setStyleSheet("font-size: 14px; color: gray;")
            layout.addWidget(etiqueta)
            return

        for mensaje in notificaciones:
            etiqueta = QtWidgets.QLabel(f"• {mensaje}")
            etiqueta.setWordWrap(True)
            etiqueta.setStyleSheet("font-size: 14px; padding: 4px; color: #333;")
            layout.addWidget(etiqueta)

class VistaRegistrarIngreso(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Ingreso")
        self.setMinimumSize(300, 150)

        # Widgets
        self.label_monto = QtWidgets.QLabel("Monto:")
        self.input_monto = QtWidgets.QLineEdit()
        self.input_monto.setPlaceholderText("Ej. 100.50")

        self.label_fecha = QtWidgets.QLabel("Fecha:")
        self.fecha_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)
        layout.addWidget(self.label_fecha)
        layout.addWidget(self.fecha_edit)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Resultado
        self.monto = None       # float
        self.fecha = None       # QDate

    def validar_y_aceptar(self):
        texto = self.input_monto.text().strip()
        try:
            monto = float(texto)
            if monto <= 0:
                raise ValueError("Monto debe ser mayor que cero.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto válido mayor que cero.")
            return

        self.monto = monto
        self.fecha = self.fecha_edit.date()  # tipo QDate
        self.accept()

class VistaRegistrarGasto(QtWidgets.QDialog):
    def __init__(self, enum_tipo: type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Gasto")
        self.setMinimumSize(350, 250)

        # Widgets
        self.label_descripcion = QtWidgets.QLabel("Descripción:")
        self.input_descripcion = QtWidgets.QLineEdit()

        self.label_monto = QtWidgets.QLabel("Monto:")
        self.input_monto = QtWidgets.QLineEdit()
        self.input_monto.setPlaceholderText("Ej. 100.50")

        self.label_fecha = QtWidgets.QLabel("Fecha:")
        self.fecha_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)

        self.label_categoria = QtWidgets.QLabel("Categoría:")
        self.combo_categoria = QtWidgets.QComboBox()
        # Llenar combobox con valores del enum
        for tipo in enum_tipo:
            self.combo_categoria.addItem(tipo.name, tipo)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_descripcion)
        layout.addWidget(self.input_descripcion)
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)
        layout.addWidget(self.label_fecha)
        layout.addWidget(self.fecha_edit)
        layout.addWidget(self.label_categoria)
        layout.addWidget(self.combo_categoria)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)
        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Resultados
        self.descripcion = None    # str
        self.monto = None          # float
        self.fecha = None          # QDate
        self.categoria = None      # TipoTrasaccion

    def validar_y_aceptar(self):
        descripcion = self.input_descripcion.text().strip()
        if not descripcion:
            QtWidgets.QMessageBox.warning(self, "Error", "La descripción no puede estar vacía.")
            return

        texto_monto = self.input_monto.text().strip()
        try:
            monto = float(texto_monto)
            if monto <= 0:
                raise ValueError("Monto debe ser mayor que cero.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto válido mayor que cero.")
            return

        categoria_index = self.combo_categoria.currentIndex()
        if categoria_index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una categoría.")
            return

        self.descripcion = descripcion
        self.monto = monto
        self.fecha = self.fecha_edit.date()
        self.categoria = self.combo_categoria.itemData(categoria_index)

        self.accept()

class VistaModificarGasto(QtWidgets.QDialog):
    def __init__(self, enum_tipo: type, gasto, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Gasto")
        self.setMinimumSize(350, 250)

        # Widgets
        self.label_descripcion = QtWidgets.QLabel("Descripción:")
        self.input_descripcion = QtWidgets.QLineEdit(gasto.descripcion)

        self.label_monto = QtWidgets.QLabel("Monto:")
        self.input_monto = QtWidgets.QLineEdit(f"{gasto.monto:.2f}")
        self.input_monto.setPlaceholderText("Ej. 100.50")

        self.label_fecha = QtWidgets.QLabel("Fecha:")
        self.fecha_edit = QtWidgets.QDateEdit(gasto.fecha)
        self.fecha_edit.setCalendarPopup(True)

        self.label_categoria = QtWidgets.QLabel("Categoría:")
        self.combo_categoria = QtWidgets.QComboBox()
        for tipo in enum_tipo:
            self.combo_categoria.addItem(tipo.name, tipo)
        # Seleccionar la categoría actual
        index = self.combo_categoria.findData(gasto.categoria)
        if index >= 0:
            self.combo_categoria.setCurrentIndex(index)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_descripcion)
        layout.addWidget(self.input_descripcion)
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)
        layout.addWidget(self.label_fecha)
        layout.addWidget(self.fecha_edit)
        layout.addWidget(self.label_categoria)
        layout.addWidget(self.combo_categoria)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Resultados
        self.descripcion = None
        self.monto = None
        self.fecha = None
        self.categoria = None

    def validar_y_aceptar(self):
        descripcion = self.input_descripcion.text().strip()
        if not descripcion:
            QtWidgets.QMessageBox.warning(self, "Error", "La descripción no puede estar vacía.")
            return

        texto_monto = self.input_monto.text().strip()
        try:
            monto = float(texto_monto)
            if monto <= 0:
                raise ValueError("Monto debe ser mayor que cero.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto válido mayor que cero.")
            return

        categoria_index = self.combo_categoria.currentIndex()
        if categoria_index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una categoría.")
            return

        self.descripcion = descripcion
        self.monto = monto
        self.fecha = self.fecha_edit.date()
        self.categoria = self.combo_categoria.itemData(categoria_index)

        self.accept()

class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 5:  # Columna progreso
            progreso = index.data(Qt.ItemDataRole.UserRole)
            if progreso is None:
                progreso = 0

            progress_option = QStyleOptionProgressBar()
            progress_option.rect = option.rect
            progress_option.minimum = 0
            progress_option.maximum = 100
            progress_option.progress = progreso
            progress_option.text = f"{progreso}%"
            progress_option.textVisible = True

            QtWidgets.QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, progress_option, painter)
        else:
            super().paint(painter, option, index)

class VistaRegistrarMeta(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Meta")
        self.setMinimumSize(350, 250)

        # Widgets
        self.label_titulo = QtWidgets.QLabel("Título de la Meta:")
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_titulo.setPlaceholderText("Ej. Ahorrar para vacaciones")

        self.label_monto_objetivo = QtWidgets.QLabel("Monto Objetivo:")
        self.input_monto_objetivo = QtWidgets.QLineEdit()
        self.input_monto_objetivo.setPlaceholderText("Ej. 1000.00")

        self.label_monto_inicial = QtWidgets.QLabel("Monto Inicial:")
        self.input_monto_inicial = QtWidgets.QLineEdit()
        self.input_monto_inicial.setPlaceholderText("Ej. 100.00")

        self.label_fecha_maxima = QtWidgets.QLabel("Fecha Límite:")
        self.fecha_edit = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.input_titulo)
        layout.addWidget(self.label_monto_objetivo)
        layout.addWidget(self.input_monto_objetivo)
        layout.addWidget(self.label_monto_inicial)
        layout.addWidget(self.input_monto_inicial)
        layout.addWidget(self.label_fecha_maxima)
        layout.addWidget(self.fecha_edit)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Resultado
        self.titulo = ""
        self.monto_objetivo = 0.0
        self.monto_inicial = 0.0
        self.fecha_limite = None  # QDate

    def validar_y_aceptar(self):
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QtWidgets.QMessageBox.warning(self, "Error", "Debes ingresar un título para la meta.")
            return

        try:
            monto_objetivo = float(self.input_monto_objetivo.text())
            if monto_objetivo <= 0:
                raise ValueError()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto objetivo válido mayor que cero.")
            return

        try:
            monto_inicial = float(self.input_monto_inicial.text())
            if monto_inicial < 0 or monto_inicial > monto_objetivo:
                raise ValueError()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto inicial válido (mayor o igual a 0 y menor o igual al objetivo).")
            return

        # Almacenar resultados
        self.titulo = titulo
        self.monto_objetivo = monto_objetivo
        self.monto_inicial = monto_inicial
        self.fecha_limite = self.fecha_edit.date()

        self.accept()

class MetasTableModel(QAbstractTableModel):
    def __init__(self, metas, parent=None):
        super().__init__(parent)
        self.metas = metas
        self.headers = ["ID Meta", "Título", "Monto Objetivo", "Monto Ahorrado", "Fecha Límite", "Progreso"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.metas)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        meta = self.metas[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return meta.ID_meta_financiera
            elif col == 1:
                return meta.nombre
            elif col == 2:
                return f"${meta.monto_objetivo:,.2f}"
            elif col == 3:
                return f"${meta.monto_actual:,.2f}"
            elif col == 4:
                return meta.fecha_objetivo.strftime("%Y-%m-%d")
            elif col == 5:
                # El progreso lo dejamos vacío para que lo pinte el delegado (barra)
                return None

        if role == Qt.ItemDataRole.UserRole and col == 5:
            # Retornamos progreso numérico para el delegado
            progreso = 0
            if meta.monto_objetivo > 0:
                progreso = int((meta.monto_actual / meta.monto_objetivo) * 100)
            return progreso

        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return QVariant()

class VistaModificarMeta(QtWidgets.QDialog):
    def __init__(self, meta, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Meta")
        self.setMinimumSize(350, 250)

        # Widgets
        self.label_titulo = QtWidgets.QLabel("Título de la Meta:")
        self.input_titulo = QtWidgets.QLineEdit(meta.nombre)

        self.label_monto_objetivo = QtWidgets.QLabel("Monto Objetivo:")
        self.input_monto_objetivo = QtWidgets.QLineEdit(str(meta.monto_objetivo))

        self.label_fecha_maxima = QtWidgets.QLabel("Fecha Límite:")
        self.fecha_edit = QtWidgets.QDateEdit(meta.fecha_objetivo)
        self.fecha_edit.setCalendarPopup(True)

        self.btn_guardar = QtWidgets.QPushButton("Guardar Cambios")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.input_titulo)
        layout.addWidget(self.label_monto_objetivo)
        layout.addWidget(self.input_monto_objetivo)
        layout.addWidget(self.label_fecha_maxima)
        layout.addWidget(self.fecha_edit)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Resultado
        self.titulo = meta.nombre
        self.monto_objetivo = meta.monto_objetivo
        self.fecha_limite = meta.fecha_objetivo

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

    def validar_y_aceptar(self):
        titulo = self.input_titulo.text().strip()
        if not titulo:
            QtWidgets.QMessageBox.warning(self, "Error", "Debes ingresar un título válido.")
            return

        try:
            monto_objetivo = float(self.input_monto_objetivo.text())
            if monto_objetivo <= 0:
                raise ValueError()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Monto objetivo inválido.")
            return

        # Guardar resultados
        self.titulo = titulo
        self.monto_objetivo = monto_objetivo
        self.fecha_limite = self.fecha_edit.date().toPyDate()

        self.accept()

from PyQt6 import QtWidgets, QtCore

class VistaRegistrarPresupuesto(QtWidgets.QDialog):
    def __init__(self, enum_categoria: type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Presupuesto")
        self.setMinimumSize(300, 200)

        # Widgets
        self.label_monto = QtWidgets.QLabel("Monto límite:")
        self.input_monto = QtWidgets.QLineEdit()
        self.input_monto.setPlaceholderText("Ej. 500.00")

        self.label_categoria = QtWidgets.QLabel("Categoría:")
        self.combo_categoria = QtWidgets.QComboBox()
        for categoria in enum_categoria:
            self.combo_categoria.addItem(categoria.name, categoria)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)
        layout.addWidget(self.label_categoria)
        layout.addWidget(self.combo_categoria)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Atributos de resultado
        self.monto_limite = None     # float
        self.categoria = None        # Enum o str, según implementación

    def validar_y_aceptar(self):
        texto_monto = self.input_monto.text().strip()
        try:
            monto = float(texto_monto)
            if monto <= 0:
                raise ValueError("Monto debe ser mayor que cero.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un monto válido mayor que cero.")
            return

        index = self.combo_categoria.currentIndex()
        if index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una categoría.")
            return

        self.monto_limite = monto
        self.categoria = self.combo_categoria.itemData(index)
        self.accept()

class VistaModificarPresupuesto(QtWidgets.QDialog):
    def __init__(self, enum_categoria: type, presupuesto_existente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Presupuesto")
        self.setMinimumSize(300, 250)

        # Widgets
        self.label_monto = QtWidgets.QLabel("Monto límite:")
        self.input_monto = QtWidgets.QLineEdit(str(presupuesto_existente.monto_limite))

        self.label_categoria = QtWidgets.QLabel("Categoría:")
        self.combo_categoria = QtWidgets.QComboBox()
        for categoria in enum_categoria:
            self.combo_categoria.addItem(categoria.name, categoria)

        # Selecciona el valor actual en el ComboBox
        index_categoria = self.combo_categoria.findData(presupuesto_existente.categoria)
        self.combo_categoria.setCurrentIndex(index_categoria)

        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)
        layout.addWidget(self.label_categoria)
        layout.addWidget(self.combo_categoria)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        self.btn_cancelar.clicked.connect(self.reject)

        # Resultados
        self.monto = None
        self.categoria = None

    def validar_y_aceptar(self):
        try:
            monto = float(self.input_monto.text().strip())
            if monto <= 0:
                raise ValueError("Monto debe ser mayor que cero.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingrese un monto válido mayor que cero.")
            return

        index = self.combo_categoria.currentIndex()
        if index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Seleccione una categoría.")
            return

        self.monto = monto
        self.categoria = self.combo_categoria.itemData(index)
        self.accept()


class VistaActualizarMontoMeta(QtWidgets.QDialog):
    def __init__(self, meta, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Actualizar Monto Ahorrado")
        self.setMinimumSize(370, 240)

        self.meta = meta

        # Widgets
        self.label_actual = QtWidgets.QLabel(f"Monto actual: {meta.monto_actual:.2f}")
        self.label_ajuste = QtWidgets.QLabel("Monto a ajustar:")

        self.input_ajuste = QtWidgets.QLineEdit()
        self.input_ajuste.setPlaceholderText("Ej. 50")

        self.radio_suma = QtWidgets.QRadioButton("Sumar")
        self.radio_resta = QtWidgets.QRadioButton("Restar")
        self.radio_suma.setChecked(True)  # Por defecto se selecciona "Sumar"

        self.btn_guardar = QtWidgets.QPushButton("Actualizar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_actual)
        layout.addWidget(self.label_ajuste)
        layout.addWidget(self.input_ajuste)

        radios = QtWidgets.QHBoxLayout()
        radios.addWidget(self.radio_suma)
        radios.addWidget(self.radio_resta)
        layout.addLayout(radios)

        botones = QtWidgets.QHBoxLayout()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        layout.addLayout(botones)

        self.setLayout(layout)

        # Resultado
        self.nuevo_monto_actual = meta.monto_actual

        # Conexiones
        self.btn_guardar.clicked.connect(self.validar_y_actualizar)
        self.btn_cancelar.clicked.connect(self.reject)

    def validar_y_actualizar(self):
        try:
            ajuste = float(self.input_ajuste.text())
            if ajuste <= 0:
                raise ValueError()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa un número positivo válido.")
            return

        if self.radio_resta.isChecked():
            ajuste *= -1

        nuevo_monto = self.meta.monto_actual + ajuste

        if nuevo_monto < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "El monto ahorrado no puede ser negativo.")
            return
        if nuevo_monto > self.meta.monto_objetivo:
            QtWidgets.QMessageBox.warning(self, "Error", "No puedes exceder el monto objetivo.")
            return

        self.nuevo_monto_actual = nuevo_monto
        self.accept()

class VentanaPresupuestos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configura tus presupuestos")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)
        self.inputs = {}

        for tipo in TipoTransaccion:
            hbox = QHBoxLayout()

            label = QLabel(tipo.value.title())  # Ej. "Alimentacion"
            spin = QDoubleSpinBox()
            spin.setPrefix("$ ")
            spin.setMaximum(10000)
            spin.setDecimals(2)
            spin.setSingleStep(1.0)
            self.inputs[tipo] = spin

            hbox.addWidget(label)
            hbox.addWidget(spin)
            self.layout.addLayout(hbox)

        self.boton_guardar = QPushButton("Guardar presupuestos")
        self.boton_guardar.clicked.connect(self.accept)
        self.layout.addWidget(self.boton_guardar)

    def obtener_presupuestos(self):
        return {
            tipo: spin.value()
            for tipo, spin in self.inputs.items()
            if spin.value() > 0
        }

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myApp = ControlInicioSesion()
    myApp.show()
    sys.exit(app.exec())

