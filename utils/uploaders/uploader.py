class UnimplementedMethod(Exception):
    pass

class MissingApiKey(Exception):
    pass

class UploadError(Exception):
    pass

class BaseUploader():

    def __init__(self, *args, **kwargs):
        raise UnimplementedMethod()

    def upload(self, fd):
        raise UnimplementedMethod()

    def uploadFile(self, filename: str):
        raise UnimplementedMethod()

    def delete(self, filename: str):
        raise UnimplementedMethod()

