import requests
from phe import paillier
import numpy as np

# Exercise 1: Paillier client

def send_query(modulo, encoded_arr):
    response = requests.post('http://localhost:8000/prediction', json={
        'pub_key_n': modulo,
        'enc_feature_vector': encoded_arr
    })
    val = response.json()['enc_prediction']
    return val

def query_pred(arr, func=send_query):
    exponent = 16
    server_side_exponent = 16
    public_key, private_key = paillier.generate_paillier_keypair(n_length=2048)
    enc_input = [public_key.encrypt(int(x * 2 ** exponent)) for x in arr]
    val = func(public_key.n, [int(x.ciphertext()) for x in enc_input])
    enc_val = paillier.EncryptedNumber(public_key, val)
    result = private_key.decrypt(enc_val) / (2 ** (exponent + server_side_exponent))
    return result

reference_input = [0.48555949, 0.29289251, 0.63463107,
                                  0.41933057, 0.78672205, 0.58910837,
                                  0.00739207, 0.31390802, 0.37037496,
                                  0.3375726 ]
reference_output = 0.44812144746653826

assert 2**(-16) > abs(query_pred(reference_input) - reference_output), \
    'Client doesn\'t work properly'
print('Client works properly')


# Exercise 2: stealing linear regression model
def steal_model():
    n = 10
    w = [0] * n
    values_to_send = [0] * n
    bias = query_pred(values_to_send)
    for i in range(n):
        values_to_send = [0] * n
        values_to_send[i] = 1
        w[i] = query_pred(values_to_send) - bias
    weights = np.array(w)
    return weights, bias

def make_model(weights, bias):
    def model(x):
        return np.array(x) @ weights + bias
    return model

weights, bias = steal_model()
model = make_model(weights, bias)
assert 2 ** (-16) > abs(model(reference_input) - reference_output), \
    'Model doesn\'t produce reference value'
print('Model is stolen successfully')


# Exercise 1 [optional] Paillier server
def mult(enc_m1, m2, modulo):
    return pow(enc_m1, m2, modulo * modulo)

def add(enc_m1, enc_m2, modulo):
    return (enc_m1 * enc_m2) % (modulo * modulo)

def add_plain(enc_m1, m2, modulo):
    g = modulo + 1
    modulo_squared = modulo * modulo
    return (enc_m1 * pow(g, m2, modulo_squared)) % modulo_squared

def dot(enc_arr1, plain_arr2, modulo):
    assert len(enc_arr1) == len(plain_arr2)
    sum_ = None
    for enc_m1, m2 in zip(enc_arr1, plain_arr2):
        x = mult(enc_m1, m2, modulo)
        if sum_ is None:
            sum_ = x
        else:
            sum_ = add(sum_, x, modulo)
    return sum_


def create_paillier_model(weights, bias):
    exponent = 16
    int_weights = [int(w * 2 ** exponent) for w in weights]
    int_bias = int(bias * 2 ** (2 * exponent))
    def paillier_model(x, modulo):
        return add_plain(dot(x, int_weights, modulo), int_bias, modulo)
    return paillier_model

# when printing weights when stealing the model use list(weights) as it gives higher precision
# than numpy.ndarray, which may cause the last test to fail due to numerical error.
# Creating paillier model by plugging freshly stolen parameters works also!
stolen_bias = 0.0545806884765625
stolen_weights = [0.1352691650390625, 0.027130126953125, 0.185882568359375, 0.0145416259765625, 
    0.056915283203125, 0.109893798828125, 0.1661224365234375, 0.04010009765625, 0.0539093017578125,
    0.1556549072265625]
homomorphic_model = create_paillier_model(stolen_weights, stolen_bias)

def paillier_server(modulo, encoded_arr):
    return homomorphic_model(encoded_arr, modulo)

assert 2**(-16) > abs(query_pred(reference_input, paillier_server) - reference_output), \
    'Custom paillier based server failed'
print('Custom paillier based server passed the test')