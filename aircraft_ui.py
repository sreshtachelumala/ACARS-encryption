import tkinter as tk
from tkinter import messagebox, scrolledtext
from aircraft import send_message

class AircraftApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aircraft ACARS Console")

        tk.Label(root, text="Enter ACARS Message:").pack(pady=5)
        self.msg_entry = tk.Entry(root, width=60)
        self.msg_entry.pack(pady=5)

        self.send_btn = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_btn.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=25, state='disabled')
        self.log_area.pack(pady=10)

    def log(self, text):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{text}\n")
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            messagebox.showwarning("Empty Message", "Please enter a message to send.")
            return

        self.log(f"[Aircraft] Original message: {msg}")

        try:
            nonce_hex, ciphertext_hex, reply = send_message(msg)
            self.log(f"[Aircraft] Encrypted message nonce (hex): {nonce_hex}")
            self.log(f"[Aircraft] Encrypted message ciphertext (hex): {ciphertext_hex}")
            self.log(f"[Ground Station] Reply (decrypted): {reply}")
        except Exception as e:
            self.log(f"[Error] Failed to send message: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AircraftApp(root)
    root.mainloop()

