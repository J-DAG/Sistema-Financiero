from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QIntValidator

class ControlRegistrarIngreso(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Ingreso")
        self.setGeometry(100, 100, 300, 200)

        layout = QtWidgets.QVBoxLayout()

        # Campo de monto
        self.label_monto = QtWidgets.QLabel("Monto del ingreso:")
        self.input_monto = QtWidgets.QLineEdit()
        self.input_monto.setValidator(QIntValidator(0, 1000000000))
        layout.addWidget(self.label_monto)
        layout.addWidget(self.input_monto)

        # Campo de fecha
        self.label_fecha = QtWidgets.QLabel("Fecha del ingreso:")
        self.fecha_edit = QtWidgets.QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QtCore.QDate.currentDate())
        layout.addWidget(self.label_fecha)
        layout.addWidget(self.fecha_edit)

        # Botones
        self.btn_guardar = QtWidgets.QPushButton("Guardar")
        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")
        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_cancelar)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

        # Acciones
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_guardar.clicked.connect(self.guardar_ingreso)

    def guardar_ingreso(self):
        monto_texto = self.input_monto.text()
        fecha = self.fecha_edit.date().toString("dd/MM/yyyy")

        if not monto_texto:
            QtWidgets.QMessageBox.warning(self, "Error", "Debes ingresar un monto.")
            return

        monto = int(monto_texto)
        QtWidgets.QMessageBox.information(self, "Ingreso registrado", f"Monto: {monto} Bs\nFecha: {fecha}")
        self.close()