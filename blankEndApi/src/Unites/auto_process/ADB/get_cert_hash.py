"""
获取Charles证书的正确Hash值
用于Android系统证书命名
"""

import subprocess
import tempfile
import os

CHARLES_CERT = """-----BEGIN CERTIFICATE-----
MIIFQjCCBCqgAwIBAgIGAZpYklggMA0GCSqGSIb3DQEBCwUAMIGlMTYwNAYDVQQDDC1DaGFybGVz
IFByb3h5IENBICg2IE5vdiAyMDI1LCBNQUtVUk8tREVTS1RPUCkxJTAjBgNVBAsMHGh0dHBzOi8v
Y2hhcmxlc3Byb3h5LmNvbS9zc2wxETAPBgNVBAoMCFhLNzIgTHRkMREwDwYDVQQHDAhBdWNrbGFu
ZDERMA8GA1UECAwIQXVja2xhbmQxCzAJBgNVBAYTAk5aMB4XDTI1MTEwNTA5NDkzN1oXDTI2MTEw
NTA5NDkzN1owgaUxNjA0BgNVBAMMLUNoYXJsZXMgUHJveHkgQ0EgKDYgTm92IDIwMjUsIE1BS1VS
Ty1ERVNLVE9QKTElMCMGA1UECwwcaHR0cHM6Ly9jaGFybGVzcHJveHkuY29tL3NzbDERMA8GA1UE
CgwIWEs3MiBMdGQxETAPBgNVBAcMCEF1Y2tsYW5kMREwDwYDVQQIDAhBdWNrbGFuZDELMAkGA1UE
BhMCTlowggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDLFmGPr6cVfOcf1g7jv3ZT4rsS
QsGSaQqecCa3FVotYrI3IJcg34sU5vyuljLLjW3s2qVckksUkLC/KCMDs0RI8uwV7T26PdARCYXx
7j7nV+tSAdr12KLALRgnsNt6IdzNRBek7vdORFcO3fFTQrprqUXXzpaEquKwkvRzvfX8MoE4/pZg
i1JyHlloRn/Dm20jQOKvEmir0empGv4YQLXoOQvUMuK2VfcACrIkiHq//OsTXn81zYSrTpun7P6s
6jJ/aa3KLB19CqJde/fxB5J/+Aok0Z1iDcfjzgk673CPQspyStfE4RRa/j3SNsAyIf6Z1AO0seXJ
Tau2Kn9hwSAfAgMBAAGjggF0MIIBcDAPBgNVHRMBAf8EBTADAQH/MIIBLAYJYIZIAYb4QgENBIIB
HROCARlUaGlzIFJvb3QgY2VydGlmaWNhdGUgd2FzIGdlbmVyYXRlZCBieSBDaGFybGVzIFByb3h5
IGZvciBTU0wgUHJveHlpbmcuIElmIHRoaXMgY2VydGlmaWNhdGUgaXMgcGFydCBvZiBhIGNlcnRp
ZmljYXRlIGNoYWluLCB0aGlzIG1lYW5zIHRoYXQgeW91J3JlIGJyb3dzaW5nIHRocm91Z2ggQ2hh
cmxlcyBQcm94eSB3aXRoIFNTTCBQcm94eWluZyBlbmFibGVkIGZvciB0aGlzIHdlYnNpdGUuIFBs
ZWFzZSBzZWUgaHR0cDovL2NoYXJsZXNwcm94eS5jb20vc3NsIGZvciBtb3JlIGluZm9ybWF0aW9u
LjAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNjO5CCh0Rec14BBtrn3uovqWyjnMA0GCSqGSIb3
DQEBCwUAA4IBAQAGSpNUx8eysNMbmZsQ+pTyfAOjM8wxYNVC7OlIUxeTStUn6pkYgBNvh9gznrU4
2GTO3Z35isKJOiu7pN4uJRZ59fff5vgEup5AvjJaU6urM6Z9f5VTb/+ca0L/zjX/hzoWYjbcMTmv
s3QVRz0P1REdKjgInMitAV4HsdZYu+Zc4LX6KNBeY81LDIm5Ou3p5a5bQaVpY3B0BZsBH/+x2HI2
YST/MxU4rvsps28Vt8SCSPLYx8jlF9WbZOik4wlYN33qXlVMjTdvmYjAb7Ws4P3YkrYcLMFS5UJL
8xFey1XRuxXN0zYCRVn0LzpIRxstVaF37f6lPrdjfUIbRX55qaZV
-----END CERTIFICATE-----"""


def get_cert_hash_openssl():
    """使用OpenSSL命令获取证书hash"""
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
        f.write(CHARLES_CERT)
        cert_file = f.name
    
    try:
        # 使用OpenSSL命令计算hash
        result = subprocess.run(
            ['openssl', 'x509', '-subject_hash_old', '-noout', '-in', cert_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            hash_value = result.stdout.strip()
            print(f"✓ 使用OpenSSL计算的hash: {hash_value}")
            return hash_value
        else:
            print(f"✗ OpenSSL命令失败: {result.stderr}")
            return None
    except FileNotFoundError:
        print("✗ 未找到OpenSSL命令")
        return None
    finally:
        # 清理临时文件
        try:
            os.unlink(cert_file)
        except:
            pass


def get_cert_hash_python():
    """使用Python cryptography库计算hash"""
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        import hashlib
        
        # 解析证书
        cert = x509.load_pem_x509_certificate(
            CHARLES_CERT.encode(),
            default_backend()
        )
        
        # 获取Subject
        subject = cert.subject
        
        # 构建Subject字符串
        subject_parts = []
        for attr in subject:
            subject_parts.append(f"{attr.oid._name}={attr.value}")
        
        subject_str = "/" + "/".join(subject_parts)
        print(f"Subject DN: {subject_str}")
        
        # 计算MD5 hash
        hash_obj = hashlib.md5(subject_str.encode())
        hash_bytes = hash_obj.digest()
        
        # 转换为OpenSSL格式
        hash_value = int.from_bytes(hash_bytes[:4], byteorder='little')
        hash_hex = f"{hash_value:08x}"
        
        print(f"✓ 使用Python计算的hash: {hash_hex}")
        return hash_hex
        
    except Exception as e:
        print(f"✗ Python计算失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Charles证书Hash计算工具")
    print("=" * 60)
    
    print("\n方法1: 使用OpenSSL命令")
    hash1 = get_cert_hash_openssl()
    
    print("\n方法2: 使用Python cryptography库")
    hash2 = get_cert_hash_python()
    
    print("\n" + "=" * 60)
    print("结果:")
    if hash1:
        print(f"OpenSSL hash: {hash1}")
        print(f"证书文件名: {hash1}.0")
    if hash2:
        print(f"Python hash:  {hash2}")
        print(f"证书文件名: {hash2}.0")
    
    if hash1 and hash2 and hash1 == hash2:
        print("\n✓ 两种方法计算结果一致!")
    elif hash1 or hash2:
        print("\n⚠ 建议使用OpenSSL的结果作为标准")
    print("=" * 60)

