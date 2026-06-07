from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo, showwarning
from tkinter import filedialog as fd
from request_wrapper import RequestWrapper
import constants

class FetchLiteWindow(Tk):
    def __init__(self) -> None:
        super().__init__()
        self._initializeSelfAttributes()
        self._initializeWindowParameters()
        self._initializeWidgets()

    def _initializeSelfAttributes(self) -> None:
        self.request_types : list[str] = constants.RequestTypes.getAll()

    def _initializeWindowParameters(self) -> None:
        self.title("FetchLite")
        self.geometry("900x600+600+200")
        self.minsize(600, 300)

    def _initializeWidgets(self) -> None:
        self._packTopPanelFrame()
        self._packCentralPanelFrame()
    
    def _packTopPanelFrame(self) -> None:
        def sendRequest():
            rtype = request_type_box.get()
            url = request_url_entry.get()

            if not url:
                showinfo("Ввод", "Поле ввода URL пустое!")
                return
            
            headers = self.headers_text.get("1.0", "end-1c")
            body = self.post_body_text.get("1.0", "end-1c")
            is_data_for_change = rtype in [
                constants.RequestTypes.POST,
                constants.RequestTypes.PATCH,
                constants.RequestTypes.PUT
            ]

            if not headers and is_data_for_change:
                showwarning(
                    "Установка заголовков",
                    "Если вы пытаетесь отправить запрос типа POST/PUT/PATCH\n" \
                    "и любой другой запрос отправляющие данные на сервер\n" \
                    "вам необходимо заполнить заголовок с ключом Content-Type что бы избежать ошибки.\n\n" \
                    "Content-Type: application/json; charset=utf-8"
                )
            if not body and is_data_for_change:
                showwarning(
                    "Отсутствие тела",
                    "Отсутствует тело для отправки запроса."
                )
            
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
                self.info_label.config(text=f"Статус: {response.status_code} OK")
                self.info_label.config(fg="#459949")
                self.response_text.delete("1.0", "end")
                self.response_text.insert("1.0", response.text)
            else:
                self.info_label.config(text=f"Статус: {response.status_code} FAIL")
                self.info_label.config(fg="#994557")

        self.top_note = ttk.Notebook(
            master=self,
            height=50
        )
        
        self.top_panel = Frame(
            master=self.top_note,
            background=constants.ColorConfig.TopPanel.BACKGROUND
        )
        Label(self.top_note, text="FetchLite - Создано для вас.", font=("Segoe UI", 10)).place(relx=1.0, x=-3, y=-3, anchor="ne")
        Label(self.top_panel,
              text="Тип:",
              background=constants.ColorConfig.TopPanel.BACKGROUND).pack(side=LEFT, padx=(8, 2))
        
        request_type_box = ttk.Combobox(self.top_panel,
              values=self.request_types,
              state="readonly", width=10)
        
        request_type_box.pack(side=LEFT, padx=2)
        request_type_box.set(constants.RequestTypes.GET)
        
        Label(self.top_panel,
              text="URL:",
              background=constants.ColorConfig.TopPanel.BACKGROUND).pack(side=LEFT, padx=(8, 2))
        
        request_url_entry = ttk.Entry(self.top_panel, width=55)
        request_url_entry.pack(side=LEFT, padx=2, anchor="w")
        
        ttk.Button(self.top_panel,
            text="Отправить запрос",
            cursor="hand2",
            command=sendRequest).pack(side=RIGHT, padx=8, anchor="w")
        
        ttk.Button(self.top_panel,
            text="Сохранить",
            cursor="hand2",
            command=self.saveToFile).pack(side=RIGHT, padx=(8, 2), anchor="w")
                
        ttk.Button(self.top_panel,
            text="Импорт JSON",
            cursor="hand2",
            command=self.importFile).pack(side=RIGHT, padx=(8, 2), anchor="w")

        self.top_note.add(self.top_panel, text="Создать запрос")
        self.top_note.pack(padx=6, pady=6,
                       side="top", fill="x")
        
    def _packCentralPanelFrame(self) -> None:
        central_note = ttk.Notebook(self)

        central_panel = Frame(
            master=central_note,
            background=constants.ColorConfig.CentralPanel.BACKGROUND
        )
        headers_panel = Frame(
            master=central_note,
            background=constants.ColorConfig.CentralPanel.BACKGROUND
        )
        post_body_panel = Frame(
            master=central_note,
            background=constants.ColorConfig.CentralPanel.BACKGROUND
        )

        self.info_label = Label(central_note, text="Запрос не отправлен", font=("Segoe UI", 10))
        self.info_label.place(relx=1.0, x=-3, y=-2, anchor="ne")
        
        self.response_text = Text(central_panel,font=("Consolas", 13), padx=6, pady=6, bg="#262626", fg="white")
        self.response_text.pack(expand=1, fill="both", padx=6, pady=6)

        self.headers_text = Text(headers_panel,font=("Consolas", 13), padx=6, pady=6, bg="#262626", fg="white")
        self.headers_text.pack(expand=1, fill="both", padx=6, pady=6)
        self.headers_text.insert(
            "1.0",
            "Content-Type: application/json; charset=utf-8"
        )
        self.post_body_text = Text(post_body_panel,font=("Consolas", 13), padx=6, pady=6, bg="#262626", fg="white")
        self.post_body_text.pack(expand=1, fill="both", padx=6, pady=6)
        self.post_body_text.insert(
            "1.0",
            "{\"\": \"\"}"
        )
        central_note.add(central_panel, text="Результат запроса")
        central_note.add(headers_panel, text="Заголовки")
        central_note.add(post_body_panel, text="Тело к отправке")
        central_note.pack(expand=1, fill="both", padx=6, pady=6)

    def _setHeadersMenu(self) -> None:
        window = Toplevel(self)
        window.title("Быстрая настройка заголовков")
        window.geometry("350x58+600+150")
        window.minsize(350, 58)
        window.maxsize(800, 58)
        window.focus()
        window.grab_set()
        window.columnconfigure(index=0, weight=1)
        window.resizable(1, 0)
        row0 = ttk.Frame(master=window)
        row0.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="nsew"
        )
        row0.columnconfigure(index=1, weight=1)

        ttk.Label(
            master=row0,
            text="Ключ:"
        ).grid(row=0, column=0, padx=6, pady=3)

        key_entry = ttk.Entry(master=row0)
        key_entry.grid(row=0, column=1, padx=6, pady=3, sticky="nsew")

        
        row1 = ttk.Frame(master=window)
        row1.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew"
        )
        row1.columnconfigure(index=1, weight=1)

        ttk.Label(
            master=row1,
            text="Значение:"
        ).grid(row=0, column=0, padx=6, pady=3)

        key_value = ttk.Entry(master=row1)
        key_value.grid(row=0, column=1, padx=6, pady=3, sticky="nsew")

    def saveToFile(self) -> None:
        file_path = fd.asksaveasfilename(
            defaultextension=".json",
            title="Выберите файл для сохранения",
            filetypes=[("JSON файлы", "*.json"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file_to_save:
                response_text = self.response_text.get("1.0", "end-1c")
                file_to_save.write(response_text)

            self.info_label.config(text=f"Файл сохранен: {file_path}")
            self.info_label.config(fg="#459949")

    def importFile(self) -> None:
        file_path = fd.askopenfilename(
            defaultextension=".json",
            title="Выберите файл для чтения",
            filetypes=(("JSON файлы", "*.json"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
        )

        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file_for_read:
                content = file_for_read.read()
                self.post_body_text.delete("1.0", "end")
                self.post_body_text.insert("1.0", content)

            self.info_label.config(text=f"Файл прочитан: {file_path}")
            self.info_label.config(fg="#459949")
    def showWindow(self) -> None:
        self.mainloop()