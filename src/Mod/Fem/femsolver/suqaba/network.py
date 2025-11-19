import socket
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.connection import allowed_gai_family


def ipv4_resolution():
    def _family():
        return socket.AF_INET
    requests.packages.urllib3.util.connection.allowed_gai_family = _family


class IPv4Session(requests.Session):
    """A requests Session that forces IPv4."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ipv4_resolution()


ipv4_session = IPv4Session()