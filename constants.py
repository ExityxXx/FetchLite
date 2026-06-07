class RequestTypes:
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"

    @staticmethod
    def getAll() -> list[str]:
        return [
            RequestTypes.GET, RequestTypes.POST,
            RequestTypes.PATCH, RequestTypes.PUT,
            RequestTypes.DELETE
        ]

class ColorConfig:
    class TopPanel:
        BACKGROUND = "#f3f3f3"
        
    class CentralPanel:
        BACKGROUND = "#ffffff" 
