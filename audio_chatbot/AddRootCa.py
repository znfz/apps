# TODO : temporary certifi update untill SSL Certificate issue fix
import certifi

def append_custom_cert_to_certifi(custom_cert_path):
    # Locate the certifi CA bundle
    cacert_path = certifi.where()
    print(f'Certifi CA bundle path: {cacert_path}')

    # Read the existing certifi CA bundle
    with open(cacert_path, 'r') as cacert_file:
        existing_cacerts = cacert_file.read()

    # Read your custom certificates
    with open(custom_cert_path, 'r') as custom_cert_file:
        custom_certs = custom_cert_file.read()

    # Check if the custom certificate is already in the CA bundle
    if custom_certs.strip() not in existing_cacerts:
        # Append the custom certificates to the existing CA bundle
        updated_cacerts = existing_cacerts + "\n" + custom_certs

        # Write the updated CA bundle back to the certifi CA bundle path
        with open(cacert_path, 'w') as cacert_file:
            cacert_file.write(updated_cacerts)

        print(f'Custom certificates appended to certifi CA bundle.')
    else:
        print(f'Custom certificate is already in the certifi CA bundle.')

print (certifi.where())
# Path to your custom certificate
custom_cert_path = 'data/cacerts.pem'

# Append custom cert to certifi
append_custom_cert_to_certifi(custom_cert_path)
