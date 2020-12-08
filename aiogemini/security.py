from typing import MutableMapping, Protocol, Union
from cryptography import x509
from cryptography.x509.oid import NameOID

import os
import ssl

StrPath = Union[str, os.PathLike[str]]


class SecurityContext(Protocol):
    def get_client_ssl_context(self, host: str) -> ssl.SSLContext:
        ...

    def get_server_ssl_context(self) -> ssl.SSLContext:
        ...


class TOFUContext:
    def __init__(
        self,
        certs: MutableMapping[str, str],
        certfile: StrPath = None,
        keyfile: StrPath = None,
    ) -> None:
        self.certs = certs
        self.certfile = certfile
        self.keyfile = keyfile

    def get_server_ssl_context(self) -> ssl.SSLContext:
        if not self.certfile or not self.keyfile:
            raise ValueError("Must set server certificate and key")

        sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sslcontext.check_hostname = False
        sslcontext.load_cert_chain(self.certfile, self.keyfile)
        sslcontext.verify_mode = ssl.CERT_NONE
        return sslcontext

    def get_client_ssl_context(
        self,
        commonname: str
    ) -> ssl.SSLContext:
        class SSLObject(ssl.SSLObject):
            def do_handshake(self) -> None:
                ssl.SSLObject.do_handshake(self)
                cert = self.getpeercert(binary_form=True)
                assert cert, "Must have cert"
                notify_certifcate(commonname, cert)

        if not commonname.islower():
            raise ValueError("Common name must be lower case")

        notify_certifcate = self.notify_certificate

        cert = self.certs.get(commonname)
        sslcontext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if self.certfile and self.keyfile:
            sslcontext.load_cert_chain(self.certfile, self.keyfile)
        if cert is None:
            sslcontext.check_hostname = False
            sslcontext.verify_mode = ssl.CERT_NONE
        else:
            sslcontext.load_verify_locations(cadata=cert)
        sslcontext.sslobject_class = SSLObject
        return sslcontext

    def notify_certificate(self, commonname: str, certdata: bytes) -> None:
        cert = x509.load_der_x509_certificate(certdata)
        pem = ssl.DER_cert_to_PEM_cert(certdata)
        certnames = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        for name in certnames:
            if name.value.lower() == commonname:
                self.certs[commonname] = pem
                break
        else:
            raise ssl.CertificateError(
                "Certificate has no matching common name"
            )
