import json


class ControllerResponse:
    def __init__(self, code=None, message=None, data=None):
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def error_response(cls, code, message):
        return cls(code=code, message=message, data=None).to_json()

    @classmethod
    def success_response(cls, data):
        return cls(code=0, message="", data=data).to_json()

    def to_json(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }


if __name__ == '__main__':
    # 示例：
    # 错误响应
    error_resp = ControllerResponse.error_response(404, "Not Found")
    print(error_resp.to_json())

    # 成功响应
    success_resp = ControllerResponse.success_response({"key": "value"})
    print(success_resp.to_json())
