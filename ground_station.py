import zmq
import pickle
import random
import time
from crypto_utils import decrypt_message, encrypt_message

MEDIUM_TO_GROUND_PORT = 5556  # example port

def generate_reply(message):
    keywords = {
        "weather": ["Weather is clear", "Storm ahead", "Turbulence reported"],
        "altitude": ["Climb to FL350", "Descend to FL210", "Maintain FL390"],
        "position": ["On course", "Heading deviation detected", "Traffic alert"],
        "landing": ["Cleared to land runway 18", "Hold at waypoint BRAVO", "Delay due to congestion"]
    }

    message_lower = message.lower()
    for keyword in keywords:
        if keyword in message_lower:
            return random.choice(keywords[keyword])

    return "Message received. No further instructions."

def run_ground_station():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{MEDIUM_TO_GROUND_PORT}")
    print(f"[Ground Station] Listening on port {MEDIUM_TO_GROUND_PORT}...")

    while True:
        data = socket.recv()
        nonce, ciphertext = pickle.loads(data)
        assert len(nonce) == 12, f"Nonce length invalid: {len(nonce)}"

        try:
            message = decrypt_message(nonce, ciphertext)
            print(f"[Ground Station] Received decrypted message: {message}")
            time.sleep(1)  # Simulate processing delay
            reply_text = generate_reply(message)
            res_nonce, res_ciphertext = encrypt_message(reply_text)
            assert len(res_nonce) == 12, f"Reply nonce length invalid: {len(res_nonce)}"

            print(f"[Ground Station] Sending encrypted reply: {reply_text}")
            socket.send(pickle.dumps((res_nonce, res_ciphertext)))
        except Exception as e:
            print("[Ground Station] Error decrypting or encrypting:", e)
            socket.send(pickle.dumps((b"", b"")))  # Send empty response to avoid blocking

if __name__ == "__main__":
    run_ground_station()
