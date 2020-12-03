from typing import MutableMapping, Protocol
from cryptography import x509
from cryptography.x509.oid import NameOID

import ssl


class SecurityContext(Protocol):
    def get_ssl_context(self, host: str) -> ssl.SSLContext:
        ...


class TOFUContext:
    def __init__(self, certs: MutableMapping[str, str]) -> None:
        self.certs = certs

    def get_ssl_context(self, common_name: str) -> ssl.SSLContext:
        class SSLObject(ssl.SSLObject):
            def do_handshake(self) -> None:
                ssl.SSLObject.do_handshake(self)
                cert = self.getpeercert(binary_form=True)
                if cert:
                    notify_certifcate(cert)

        notify_certifcate = self.notify_certificate

        cert = self.certs.get(common_name)
        sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if cert is None:
            sslcontext.check_hostname = False
            sslcontext.verify_mode = ssl.CERT_NONE
        else:
            sslcontext.load_verify_locations(cadata=cert)
        sslcontext.sslobject_class = SSLObject
        return sslcontext

    def notify_certificate(self, certdata: bytes) -> None:
        cert = x509.load_der_x509_certificate(certdata)
        pem = ssl.DER_cert_to_PEM_cert(certdata)
        common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        for name in common_name:
            self.certs[name.value] = pem
