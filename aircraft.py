import zmq
import pickle
from crypto_utils import encrypt_message, decrypt_message

AIRCRAFT_TO_MEDIUM_PORT = 5555  # example port

context = zmq.Context()

sock_to_medium = context.socket(zmq.REQ)
sock_to_medium.connect(f"tcp://localhost:{AIRCRAFT_TO_MEDIUM_PORT}")

def send_message(msg):
    nonce, ciphertext = encrypt_message(msg)
    assert len(nonce) == 12, f"Nonce length invalid: {len(nonce)}"
    sock_to_medium.send(pickle.dumps((nonce, ciphertext)))
    reply_data = sock_to_medium.recv()
    res_nonce, res_ciphertext = pickle.loads(reply_data)
    assert len(res_nonce) == 12, f"Reply nonce length invalid: {len(res_nonce)}"
    reply = decrypt_message(res_nonce, res_ciphertext)
    return nonce.hex(), ciphertext.hex(), reply


if __name__ == "__main__":
    while True:
        message = input("Enter ACARS message to send: ").strip()
        if not message:
            print("Empty message, try again.")
            continue
        try:
            nonce_hex, ciphertext_hex, reply = send_message(message)
            print(f"Sent encrypted message nonce: {nonce_hex}")
            print(f"Sent encrypted message ciphertext: {ciphertext_hex}")
            print(f"Received decrypted reply: {reply}\n")
        except Exception as e:
            print("Error:", e)
