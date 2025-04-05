import os
import subprocess
import re

# Paths to root CA cert and key
ROOT_CA_CERT = 'certs/rootCA.pem'
ROOT_CA_KEY = 'certs/rootCA.key'
CERTS_DIR = 'certs/dynamic_certs'

# Ensure dynamic certs directory exists
os.makedirs(CERTS_DIR, exist_ok=True)

def sanitize_filename(domain):
    """
    Replace any unsafe characters in domain names to use as filenames.
    """
    return re.sub(r'[^a-zA-Z0-9.-]', '_', domain)

def generate_cert(domain):
    """
    Generates a certificate for the specified domain signed by the root CA.
    Returns the path to the cert and key files.
    """
    safe_domain = sanitize_filename(domain)

    cert_path = os.path.join(CERTS_DIR, f"{safe_domain}.crt")
    key_path = os.path.join(CERTS_DIR, f"{safe_domain}.key")
    csr_path = os.path.join(CERTS_DIR, f"{safe_domain}.csr")
    config_path = os.path.join(CERTS_DIR, f"{safe_domain}_ext.cnf")

    # If already exists, reuse it
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print(f"[+] Using cached certificate for {domain}")
        return cert_path, key_path

    print(f"[+] Generating new certificate for {domain}")

    try:
        # 1. Generate private key
        subprocess.run(['openssl', 'genrsa', '-out', key_path, '2048'], check=True)

        # 2. Generate CSR (Certificate Signing Request)
        subprocess.run([
            'openssl', 'req', '-new', '-key', key_path, '-out', csr_path,
            '-subj', f"/CN={domain}"
        ], check=True)

        # 3. Create SAN extension config
        with open(config_path, 'w') as f:
            f.write(f"""
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
subjectAltName = DNS:{domain}
""")

        # 4. Sign the certificate with our root CA
        subprocess.run([
            'openssl', 'x509', '-req', '-in', csr_path, '-CA', ROOT_CA_CERT,
            '-CAkey', ROOT_CA_KEY, '-CAcreateserial', '-out', cert_path,
            '-days', '825', '-sha256', '-extfile', config_path
        ], check=True)

    finally:
        # 5. Clean up temporary files
        if os.path.exists(csr_path):
            os.remove(csr_path)
        if os.path.exists(config_path):
            os.remove(config_path)

    return cert_path, key_path
