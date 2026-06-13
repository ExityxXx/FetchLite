from email import message_from_string
from tkinter.messagebox import showerror
import requests
import constants

class RequestWrapper:
    def __init__(self,
                 type: str | None, 
                 url: str | None,
                 headers: str | None,
                 body: str | None
                 ):
        self.rtype: str = type
        self.url: str = url
        self.headers: str = headers
        self.body: str = body
        self.response: requests.Response = None

    def sendRequest(self) -> requests.Response:
        if not self.rtype:
            raise ValueError("Request sending error. Request type is None (check wrapper)")

        if not self.url:
            raise ValueError("Request sending error. Request url value is None (check wrapper)")
        
        # dict_header: dict = dict(message_from_string(self.getHeaders()).items())
        
        try:
            method = self.rtype.lower()
            if self.rtype in (constants.RequestTypes.GET, constants.RequestTypes.DELETE):
                response = getattr(requests, method)(
                    url=self.getUrl(),
                    timeout=5
                )
            else:
                response = getattr(requests, method)(
                    url=self.getUrl(),
                    headers=self.getHeaders(),
                    data=self.getBody(),
                    timeout=5
                )

            if response:
                response.raise_for_status()

        except requests.exceptions.MissingSchema:
            showerror("Ошибка форматирования",
                        "Убедитесь что запрос начинается с "\
                        "http:// или https://")
            return
        
        except requests.exceptions.Timeout:
            showerror("Таймаут",
                        "Время ожидания от сервера истекло")
            return
        
        except requests.exceptions.RequestException as e:
            showerror("Ошибка",
                        f"Произошла ошибка запроса: {e}")
            return
            
        self.response = response
        return self.response
        
    def getResponse(self) -> requests.Response:
        return self.response
    
    def getType(self) -> str:
        return self.rtype
    
    def getUrl(self) -> str:
        return self.url
    
    def getHeaders(self) -> dict:
        return self.headers
    
    def getBody(self) -> str:
        return self.body
    
    def setType(self, ntype: str) -> None:
        try:
            self.rtype = ntype
        except ValueError as err:
            print("RequestWrapperValueError: Failed to set request type.")
            return
    
    def setUrl(self, nurl: str) -> None:
        try:
            self.url = nurl
        except ValueError as err:
            print("RequestWrapperValueError: Failed to set request url.")
            return
    
    def setHeaders(self, nheads: dict) -> None:
        try:
            self.headers = nheads
        except ValueError as err:
            print("RequestWrapperValueError: Failed to set request headers.")
            return
    
    def setBody(self, nbody: str) -> None:
        try:
            self.body = nbody
        except ValueError as err:
            print("RequestWrapperValueError: Failed to set request body.")
            return
        
    