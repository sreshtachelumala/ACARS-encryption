# attacker.py – Passive eavesdropper
import zmq
import pickle

context = zmq.Context()

# Receive from aircraft
sock_from_aircraft = context.socket(zmq.REP)
sock_from_aircraft.bind("tcp://*:5555")

# Forward to ground station
sock_to_ground = context.socket(zmq.REQ)
sock_to_ground.connect("tcp://localhost:5556")

print("[Attacker 👀] Passive interceptor listening...")

while True:
    try:
        data = sock_from_aircraft.recv()
        nonce, ciphertext = pickle.loads(data)

        print("[Attacker 📡] Intercepted encrypted message:")
        print(f"    Nonce: {nonce.hex()}")
        print(f"    Ciphertext: {ciphertext.hex()}")
        print("    🔒 Cannot decrypt without key.")

        # Forward message as-is
        sock_to_ground.send(pickle.dumps((nonce, ciphertext)))

        # Receive reply
        reply = sock_to_ground.recv()
        reply_nonce, reply_ciphertext = pickle.loads(reply)

        print("[Attacker 📡] Intercepted encrypted reply:")
        print(f"    Nonce: {reply_nonce.hex()}")
        print(f"    Ciphertext: {reply_ciphertext.hex()}")
        print("    🔒 Cannot decrypt without key.")

        # Forward reply back to aircraft
        sock_from_aircraft.send(pickle.dumps((reply_nonce, reply_ciphertext)))

    except Exception as e:
        print(f"[Attacker ⚠️] Error in forwarding: {e}")
