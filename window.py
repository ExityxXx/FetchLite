from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QTabWidget,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QMenu)

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from request_wrapper import RequestWrapper
import constants
import json

class FetchLiteWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._initSelfAttrs()
        self._initWindowParams()
        self._initWidgets()
        
    def _initSelfAttrs(self) -> None:
        self.request_types : list[str] = constants.RequestTypes.getAll()

    def _initWindowParams(self) -> None:
        self.setWindowTitle("FetchLite - API client")
        self.resize(900, 700)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_vbox_layout = QVBoxLayout(self.central)

    def _initWidgets(self) -> None:
        self._packTopPanelFrame()
        self._packCentralPanelFrame()
        self._packMenuBar()
        self._packStatusBar()

    def _packTopPanelFrame(self) -> None:
        def getTableData(table: QTableWidget) -> list:
            data = {}
            for row in range(table.rowCount()):
                for col in range(table.columnCount() - 1):
                    item = table.item(row, col)
                    if item:
                        next_item = table.item(row, col+1)
                        data[item.text()] = next_item.text()
                    else:
                        data[""] = ""
            return data
        
        def sendRequest():
            rtype = request_type_box.currentText()
            url = request_url_entry.text()

            if not url:
                mbox = QMessageBox()
                mbox.setWindowTitle("Ввод")
                mbox.setText("Поле ввода URL пустое!")
                mbox.setIcon(QMessageBox.Icon.Information)
                mbox.exec()
                return
            
            headers = getTableData(self.headers_table)
            body = self.post_body_text.toPlainText()
            print(f"rtype = {rtype}")
            print(f"url = {url}")
            print(f"headers = {headers}")
            print(f"body = {body}")

            is_data_for_change = rtype in [
                constants.RequestTypes.POST,
                constants.RequestTypes.PATCH,
                constants.RequestTypes.PUT
            ]

            if not headers and is_data_for_change:
                mbox = QMessageBox()
                mbox.setWindowTitle("Установка заголовков")
                mbox.setText("Если вы пытаетесь отправить запрос типа POST/PUT/PATCH\n" \
                    "и любой другой запрос отправляющие данные на сервер\n" \
                    "вам необходимо заполнить заголовок с ключом Content-Type что бы избежать ошибки.\n\n" \
                    "Content-Type: application/json; charset=utf-8")
                mbox.setIcon(QMessageBox.Icon.Warning)
                mbox.exec()
            if not body and is_data_for_change:
                mbox = QMessageBox()
                mbox.setWindowTitle("Отсутствие тела")
                mbox.setText("Отсутствует тело для отправки запроса.")
                mbox.setIcon(QMessageBox.Icon.Warning)
                mbox.exec()
            request = RequestWrapper(
                type=rtype,
                url=url,
                headers=headers,
                body=body
            )
            
            response = request.sendRequest()
            
            if not response:
                return
            
            if response.status_code <= 400:
                self.response_text.setPlainText(response.text)

        self.top_panel_layout = QHBoxLayout()

        request_type_box = QComboBox()
        request_type_box.addItems(self.request_types)
        request_type_box.setEditable(False)
        request_type_box.setCurrentIndex(0)

        request_url_entry = QLineEdit()
        request_url_entry.setPlaceholderText("https://placeholderapi/get")

        send_request_button = QPushButton("Отправить запрос")
        send_request_button.clicked.connect(sendRequest)

        self.top_panel_layout.addWidget(QLabel("Метод: "))
        self.top_panel_layout.addWidget(request_type_box)
        self.top_panel_layout.addWidget(QLabel("URL: "))
        self.top_panel_layout.addWidget(request_url_entry)
        self.top_panel_layout.addWidget(send_request_button)
        self.main_vbox_layout.addLayout(self.top_panel_layout)
        self.main_vbox_layout.addStretch()

    def _packCentralPanelFrame(self) -> None:
        central_note = QTabWidget()
        font_size: int = 14
        
        central_panel = QWidget()
        central_panel_layout = QVBoxLayout(central_panel)
        self.response_text = QTextEdit()
        self.response_text.setFontPointSize(font_size)

        headers_panel = QWidget()
        headers_panel_layout = QVBoxLayout(headers_panel)
        headers_top_layout = QHBoxLayout()

        self.header_key_le = QLineEdit()
        self.header_val_le = QLineEdit()

        add_row_pb = QPushButton("Добавить строку")
        add_row_pb.clicked.connect(self.addRow)

        del_row_pb = QPushButton("Удалить выбранное")
        del_row_pb.clicked.connect(self.deleteSelectedRow)

        headers_top_layout.addWidget(QLabel("Ключ: "))
        headers_top_layout.addWidget(self.header_key_le)
        headers_top_layout.addWidget(QLabel("Значение: "))
        headers_top_layout.addWidget(self.header_val_le)
        headers_top_layout.addStretch()
        headers_top_layout.addWidget(add_row_pb)
        headers_top_layout.addWidget(del_row_pb)

        self.headers_table = QTableWidget(1, 2)
        self.headers_table.setHorizontalHeaderLabels(["Ключ", "Значение"])
        self.headers_table.setItem(0, 0, QTableWidgetItem('Content-Type'))
        self.headers_table.setItem(0, 1, QTableWidgetItem('application/json; charset=utf-8'))
        self.headers_table.horizontalHeader().setStretchLastSection(True)
        self.headers_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.headers_table.customContextMenuRequested.connect(self.headersTableContextMenu)

        post_body_panel = QWidget()
        post_body_panel_layout = QVBoxLayout(post_body_panel)
        self.post_body_text = QTextEdit()
        self.post_body_text.setFontPointSize(font_size)
        self.post_body_text.setText("{\"\": \"\"}")

        central_note.addTab(central_panel, "Результат запроса")
        central_note.addTab(headers_panel, "Заголовки")
        central_note.addTab(post_body_panel, "Тело к отправке")
        
        central_panel_layout.addWidget(self.response_text)
        headers_panel_layout.addLayout(headers_top_layout)
        headers_panel_layout.addWidget(self.headers_table)
        post_body_panel_layout.addWidget(self.post_body_text)
        self.main_vbox_layout.addWidget(central_note, stretch=1)

    def _packMenuBar(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")
        
        new_request_action = QAction("Создать новый запрос", self)
        save_request_action = QAction("Сохранить запрос в файл", self)
        load_request_action = QAction("Импортировать файл в тело", self)

        http_action = QAction("HTTP", self)
        help_action = QAction("Помощь", self)

        file_menu.addAction(new_request_action)
        file_menu.addAction(save_request_action)
        file_menu.addAction(load_request_action)
        
        load_headers_menu = file_menu.addMenu("Импортировать заголовки")
        load_headers_menu.addAction(http_action)
        load_headers_menu.addSeparator()
        load_headers_menu.addAction(help_action)

    def _packStatusBar(self) -> None:
        status_bar = self.statusBar()
        status_bar.addWidget(QLabel("   API Client   "))
        response_label = QLabel(" Запрос не отправлен ")
        status_bar.addWidget(response_label)

    def headersTableContextMenu(self, pos) -> None:
        menu = QMenu()
    
        add_row_action = QAction("Добавить строку", self)
        add_row_action.triggered.connect(self.addRow)
        
        del_row_action = QAction("Удалить строку", self)
        del_row_action.triggered.connect(lambda: self.deleteRowAt(pos))
        menu.addAction(add_row_action)
        
        item_at_pos = self.headers_table.itemAt(pos)

        if item_at_pos:
            menu.addAction(del_row_action)
        
        menu.exec(self.headers_table.mapToGlobal(pos))

    def addRow(self):
        new_row = self.headers_table.rowCount()
        self.headers_table.insertRow(new_row)
        key = self.header_key_le.text()
        value = self.header_val_le.text()
        self.headers_table.setItem(new_row, 0, QTableWidgetItem(key if key else ""))
        self.headers_table.setItem(new_row, 1, QTableWidgetItem(value if value else ""))
        self.header_key_le.clear()
        self.header_val_le.clear()

    def deleteSelectedRow(self):
        selected = self.headers_table.currentRow()
        if selected != -1:
            self.headers_table.removeRow(selected)
    
    def deleteRowAt(self, pos):
        target = self.headers_table.itemAt(pos)
        if target:
            self.headers_table.removeRow(target.row())
            