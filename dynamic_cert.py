import os
import subprocess

ROOT_CA_CERT = 'certs/rootCA.pem'
ROOT_CA_KEY = 'certs/rootCA.key'
CERTS_DIR = 'certs/dynamic_certs'

# Make sure the dynamic certs folder exists
os.makedirs(CERTS_DIR, exist_ok=True)

def generate_cert(domain):
    cert_path = os.path.join(CERTS_DIR, f"{domain}.crt")
    key_path = os.path.join(CERTS_DIR, f"{domain}.key")
    csr_path = os.path.join(CERTS_DIR, f"{domain}.csr")
    config_path = os.path.join(CERTS_DIR, f"{domain}_ext.cnf")

    # If already generated, just return paths
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path

    # 1. Generate private key
    subprocess.run(['openssl', 'genrsa', '-out', key_path, '2048'], check=True)

    # 2. Generate CSR
    subprocess.run([
        'openssl', 'req', '-new', '-key', key_path, '-out', csr_path,
        '-subj', f"/CN={domain}"
    ], check=True)

    # 3. Create ext config for SAN
    with open(config_path, 'w') as f:
        f.write(f"""
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
subjectAltName = DNS:{domain}
""")

    # 4. Sign certificate with root CA
    subprocess.run([
        'openssl', 'x509', '-req', '-in', csr_path, '-CA', ROOT_CA_CERT,
        '-CAkey', ROOT_CA_KEY, '-CAcreateserial', '-out', cert_path,
        '-days', '825', '-sha256', '-extfile', config_path
    ], check=True)

    # Cleanup temp files
    os.remove(csr_path)
    os.remove(config_path)

    return cert_path, key_path
