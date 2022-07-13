from typing import MutableMapping, Optional, Union
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

import os
import ssl

StrPath = Union[str, os.PathLike[str]]


class SSLObject(ssl.SSLObject):
    def do_handshake(self) -> None:
        ssl.SSLObject.do_handshake(self)
        cert = self.getpeercert(binary_form=True)
        if not cert:
            raise ssl.SSLError("Must have certificate")
        self.context.notify_certificate(self.server_hostname, cert)  # type: ignore


class TOFUContext(ssl.SSLContext):
    sslobject_class = SSLObject
    trust: MutableMapping[str, bytes]

    def notify_certificate(self, commonname: str, certdata: bytes) -> None:
        cert = x509.load_der_x509_certificate(certdata)
        certnames = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        fingerprint = cert.fingerprint(hashes.SHA256())

        trusted_fingerprint = self.trust.get(commonname)
        if trusted_fingerprint is not None:
            if fingerprint != trusted_fingerprint:
                raise ssl.CertificateError("Certificate fingerprint does not match")

        for name in certnames:
            if name.value.lower() == commonname:
                self.trust[commonname] = fingerprint
                break
        else:
            raise ssl.CertificateError(
                "Certificate has no matching common name")


def create_server_ssl_context(
    certfile: StrPath,
    keyfile: StrPath
) -> ssl.SSLContext:
    if not certfile or not keyfile:
        raise ValueError("Must set server certificate and key")

    sslcontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslcontext.check_hostname = False
    sslcontext.load_cert_chain(certfile, keyfile)
    sslcontext.verify_mode = ssl.CERT_NONE
    return sslcontext


def create_client_ssl_context(
    trust: MutableMapping[str, bytes],
    certfile: Optional[StrPath],
    keyfile: Optional[StrPath],
) -> ssl.SSLContext:
    sslcontext = TOFUContext(ssl.PROTOCOL_TLS_CLIENT)
    sslcontext.trust = trust
    sslcontext.check_hostname = False
    sslcontext.verify_mode = ssl.CERT_NONE
    if certfile and keyfile:
        sslcontext.load_cert_chain(certfile, keyfile)
    return sslcontext
