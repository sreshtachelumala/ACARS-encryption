import zmq
import pickle
import random
import time
from config import *
from crypto_utils import encrypt_message, decrypt_message

def simulate_propagation_delay(distance_km):
    delay_sec = distance_km / SPEED_OF_LIGHT
    time.sleep(delay_sec)

def simulate_noise(msg, quality):
    if quality < 0.5:
        noisy_msg = ""
        for ch in msg:
            if random.random() < 0.05:  # 5% corrupt
                noisy_msg += chr(random.randint(32, 126))
            else:
                noisy_msg += ch
        return noisy_msg
    return msg

def run_medium():
    context = zmq.Context()

    # Receive from Aircraft
    sock_aircraft = context.socket(zmq.REP)
    sock_aircraft.bind(f"tcp://*:{AIRCRAFT_TO_MEDIUM_PORT}")

    # Connect to Ground Station
    sock_ground = context.socket(zmq.REQ)
    sock_ground.connect(f"tcp://localhost:{MEDIUM_TO_GROUND_PORT}")

    # Connect for replies from Ground to Aircraft
    sock_ground_rep = context.socket(zmq.REP)
    sock_ground_rep.bind(f"tcp://*:{GROUND_TO_MEDIUM_PORT}")

    sock_aircraft_rep = context.socket(zmq.REQ)
    sock_aircraft_rep.connect(f"tcp://localhost:{MEDIUM_TO_AIRCRAFT_PORT}")

    print("[Medium] VHF medium started...")

    while True:
        # Receive from aircraft
        data = sock_aircraft.recv()
        nonce, ciphertext = pickle.loads(data)

        # Simulate message loss
        if random.random() < MESSAGE_LOSS_PROB:
            print("[Medium] Message lost from Aircraft to Ground Station")
            sock_aircraft.send(pickle.dumps((b"", b"")))  # Reply empty to avoid blocking
            continue

        # Decrypt message to get distance, freq info for simulation
        try:
            plaintext = decrypt_message(nonce, ciphertext)
        except Exception:
            # If corrupted, just forward as is but note corrupted
            plaintext = None

        # Simulate distance & signal quality (for demo fixed distance)
        distance_km = 150
        signal_quality = max(0.1, 1 - (distance_km / 500))

        # Apply noise on plaintext before sending to ground station
        if plaintext:
            noisy_text = simulate_noise(plaintext, signal_quality)
        else:
            noisy_text = None  # corrupted message

        # Encrypt again (simulate actual data sent)
        if noisy_text:
            n_nonce, n_ciphertext = encrypt_message(noisy_text)
        else:
            n_nonce, n_ciphertext = nonce, ciphertext  # corrupted, pass as is

        # Send to ground station
        sock_ground.send(pickle.dumps((n_nonce, n_ciphertext)))
        # Receive reply from ground
        rep = sock_ground.recv()
        g_nonce, g_ciphertext = pickle.loads(rep)

        # Simulate message loss on ground to aircraft
        if random.random() < MESSAGE_LOSS_PROB:
            print("[Medium] Message lost from Ground Station to Aircraft")
            sock_aircraft.send(pickle.dumps((b"", b"")))
            continue

        # Decrypt ground reply to apply noise
        try:
            ground_reply = decrypt_message(g_nonce, g_ciphertext)
        except Exception:
            ground_reply = None

        if ground_reply:
            noisy_reply = simulate_noise(ground_reply, signal_quality)
        else:
            noisy_reply = None

        if noisy_reply:
            r_nonce, r_ciphertext = encrypt_message(noisy_reply)
        else:
            r_nonce, r_ciphertext = g_nonce, g_ciphertext

        # Reply to aircraft
        sock_aircraft.send(pickle.dumps((r_nonce, r_ciphertext)))


if __name__ == "__main__":
    run_medium()


