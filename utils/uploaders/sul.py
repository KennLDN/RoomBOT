from .uploader import BaseUploader, MissingApiKey, UploadError
import requests

class SulUploader(BaseUploader):

    _apiurl = "https://s-ul.eu/api/v1/upload"
    _deleteurl = "https://s-ul.eu/delete.php"

    def __init__(self, *args, **kwargs):

        self.key = kwargs.get("key", None)
        if not self.key:
            raise MissingApiKey("No api key was provided")

    def upload(self, fd):
        data = {'wizard': 'true', 'key': self.key}

        res = requests.post(self._apiurl,
                            data=data,
                            files={'file': fd})

        answer = res.json()

        if not answer.get('success', True):
            raise UploadError(answer['reason'])

        return [answer["url"], answer["filename"]]

    def uploadFile(self, filename: str):
        fd = open(filename, "rb")

        return self.upload(fd)

    def delete(self, filename: str):
        url = "{0}?key={1}&file={2}".format(self._deleteurl, self.key, filename)
        res = requests.post(url)

        return res.status_code == 200

