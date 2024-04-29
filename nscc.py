import math
import random
import json

def load_json_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def is_prime(x):
    """ Check if a number is prime. """
    if x <= 1:
        return False
    if x <= 3:
        return True
    if x % 2 == 0 or x % 3 == 0:
        return False
    i = 5
    while i * i <= x:
        if x % i == 0 or x % (i + 2) == 0:
            return False
        i += 6
    return True

def generate_prime(min_value):
    """ Generate a random prime number greater than a given minimum value. """
    prime = min_value
    while not is_prime(prime):
        prime = random.randint(min_value, 2 * min_value)
    return prime

def generate_key_pair():
    p = generate_prime(1000000)
    q = generate_prime(1000000)
    assert p != q
    assert is_prime(p)
    assert is_prime(q)
    n = p * q
    r = random.randint(1, n)
    phi = (p - 1) * (q - 1)
    g = 1 + n
    lmbda = phi * 1
    mu = pow(phi, -1, n)
    return r, p, q, n, g, lmbda, mu

def encrypt_int(value, n, g):
    # """ Encrypt a value using the Paillier encryption scheme. """
    value, n, g = int(value), int(n), int(g)
    r = random.randint(1, n - 1)  # Choose a random r
    c = (pow(g, value, n**2) * pow(r, n, n**2)) % n**2
    return c

def encrypt_string(s, n, g):
    """ Encrypt a string by converting each character to its ASCII value and encrypting it. """
    encrypted_chars = [encrypt_int(ord(char), n, g) for char in s]
    return encrypted_chars

def loop_encrypt_json(json_obj, n, g):
    """ Recursively encrypt values in a JSON object. """
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if isinstance(value, str) and not key in ['clientID','Timestamp']:  # Encrypt only the 'Name' field
                json_obj[key] = encrypt_string(value, n, g)
            elif isinstance(value, (int, float)):  # Encrypt numeric values
                json_obj[key] = encrypt_int(value, n, g)
    elif isinstance(json_obj, list):
        for index, item in enumerate(json_obj):
            loop_encrypt_json(item, n, g)
    return json_obj

def decrypt_value(c, n, lmbda, mu):
    """ Decrypt a single encrypted value. """
    x = pow(c, lmbda, n**2)
    l_of_x = (x - 1) // n
    m = (l_of_x * mu) % n
    return m

def decrypt_string(encrypted_chars, n, lmbda, mu):
    """ Decrypt a list of encrypted ASCII values to a string. """
    decrypted_chars = [chr(decrypt_value(char, n, lmbda, mu)) for char in encrypted_chars]
    return ''.join(decrypted_chars)

def loop_decrypt_json(encrypted_json, n, lmbda, mu):
    """ Recursively decrypt values in an encrypted JSON object. """
    if isinstance(encrypted_json, dict):
        for key, value in encrypted_json.items():
            if isinstance(value, list) and all(isinstance(x, int) for x in value):  # Assuming encrypted 'Name' field
                encrypted_json[key] = decrypt_string(value, n, lmbda, mu)
            elif isinstance(value, int):  # Assuming encrypted numeric values
                encrypted_json[key] = decrypt_value(value, n, lmbda, mu)
    elif isinstance(encrypted_json, list):
        for item in encrypted_json:
            loop_decrypt_json(item, n, lmbda, mu)
    return encrypted_json

def save_encrypted_data(encrypted_json, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(encrypted_json, file, indent=4)
        print("Encrypted data has been saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving the encrypted data: {e}")



r, p, q, n, g, lmbda, mu = generate_key_pair()
file_path = r"C:/Users/repsaj.p/Desktop/Spark/Informationofclient.json"

json_data = load_json_from_file(file_path)

print("----------------------------------")
print("Original JSON data:", json_data)
print("----------------------------------")
encrypted_json = loop_encrypt_json(json_data, n, g)
print("Encrypted JSON:", encrypted_json)

save_encrypted_data(encrypted_json, file_path)

print("----------------------------------")
decrypted_json = loop_decrypt_json(encrypted_json, n, lmbda, mu)
print("Decrypted JSON:", decrypted_json)
