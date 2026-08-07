import streamlit as st
import time
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import random

# Try to import tkinter (only available in local deployment)
try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# --- CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="Ransomware Simulator V2",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ADVANCED CSS & MOBILE OPTIMIZATION ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;600&display=swap');

    /* Variables */
    :root {
        --neon-green: #39ff14;
        --neon-red: #ff003c;
        --neon-blue: #00f3ff;
        --bg-dark: #050505;
        --card-bg: rgba(20, 20, 20, 0.9);
    }

    /* Global Reset */
    .stApp {
        background-color: var(--bg-dark);
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(20, 20, 20, 0.8) 0%, rgba(0, 0, 0, 1) 100%),
            linear-gradient(rgba(0, 255, 0, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 0, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 20px 20px, 20px 20px;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }

    /* Typography */
    h1, h2, h3, .glitch {
        font-family: 'Share Tech Mono', monospace;
        letter-spacing: 1px;
    }
    
    h1 { 
        color: var(--neon-blue); 
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: transparent;
        border: 1px solid var(--neon-blue);
        color: var(--neon-blue);
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%; /* Mobile Friendly */
        padding: 0.8rem;
    }
    
    .stButton > button:hover {
        background: rgba(0, 243, 255, 0.1);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
        border-color: #fff;
        color: #fff;
    }

    /* Cards (Glassmorphism) */
    .cyber-card {
        background: var(--card-bg);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 3px solid var(--neon-blue);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Mobile Media Queries */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        .stButton > button { padding: 1rem; font-size: 1rem; }
        .cyber-card { padding: 1rem; }
    }
    
     /* Ransom Note Specifics */
    .ransom-container {
        border: 2px solid var(--neon-red);
        background: rgba(50, 0, 0, 0.9);
        color: var(--neon-red);
        animation: pulse 2s infinite;
        padding: 2rem;
        text-align: center;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0); }
    }

</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = 'education'
if 'target_folder' not in st.session_state: st.session_state.target_folder = None
if 'target_mode' not in st.session_state: st.session_state.target_mode = None  # 'local' or 'virtual'
if 'target_files' not in st.session_state: st.session_state.target_files = []  # list of paths or file blobs
if 'is_encrypted' not in st.session_state: st.session_state.is_encrypted = False
if 'key' not in st.session_state: st.session_state.key = b'01234567890123456789012345678901' 
if 'attack_start_time' not in st.session_state: st.session_state.attack_start_time = None
if 'quiz_score' not in st.session_state: st.session_state.quiz_score = 0
if 'attack_variant' not in st.session_state: st.session_state.attack_variant = 'Standard'

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### 🧭 NAVIGATION")
    if st.button("🏠 GO TO HOME SCREEN"):
        st.session_state.page = 'education'
        st.session_state.is_encrypted = False
        st.session_state.target_folder = None
        st.session_state.target_files = []
        st.session_state.target_mode = None
        for key in ['encrypted_files', 'encrypted_virtual', 'decrypted_virtual', 'selected_folder_path', 'original_folder_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.markdown("---")
    st.caption("Ransomware Simulator V2")

# --- LOGIC ---

def get_files_in_folder(folder_path):
    # Get ALL files from the folder (including subdirectories)
    target_files = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if not file.startswith('.'):
                    target_files.append(os.path.join(root, file))
    except Exception as e:
        st.error(f"Error reading folder: {e}")
    return target_files

def encrypt_local_file(file_path):
    try:
        # Read file from disk
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Encrypt the data
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = iv + encryptor.update(data) + encryptor.finalize()
        
        # Write encrypted data back to file
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Rename file to add .locked extension
        locked_path = file_path + ".locked"
        os.rename(file_path, locked_path)
        
        # Track encrypted files
        if 'encrypted_files' not in st.session_state:
            st.session_state.encrypted_files = []
        st.session_state.encrypted_files.append(locked_path)
        
        return True
    except Exception as e:
        st.error(f"Encryption error for {os.path.basename(file_path)}: {e}")
        return False

def decrypt_local_file(file_path):
    try:
        if not file_path.endswith(".locked"):
            return False
        
        # Read encrypted file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Decrypt the data
        iv = data[:16]
        ciphertext = data[16:]
        cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Get original filename (remove .locked)
        original_path = file_path[:-7]
        
        # Write decrypted data back
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        
        # Remove the .locked file
        os.remove(file_path)
        
        return True
    except Exception as e:
        st.error(f"Decryption error for {os.path.basename(file_path)}: {e}")
        return False

def encrypt_virtual_files(file_entries):
    """Encrypt in-memory file entries (list of dicts with name, data)."""
    if 'encrypted_virtual' not in st.session_state:
        st.session_state.encrypted_virtual = {}
    encrypted_count = 0
    for entry in file_entries:
        name = entry['name']
        data = entry['data']
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = iv + encryptor.update(data) + encryptor.finalize()
        st.session_state.encrypted_virtual[name + '.locked'] = encrypted_data
        encrypted_count += 1
    return encrypted_count

def decrypt_virtual_files():
    if 'encrypted_virtual' not in st.session_state:
        return 0
    decrypted = 0
    if 'decrypted_virtual' not in st.session_state:
        st.session_state.decrypted_virtual = {}
    for name, data in st.session_state.encrypted_virtual.items():
        try:
            iv = data[:16]
            ciphertext = data[16:]
            cipher = Cipher(algorithms.AES(st.session_state.key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            original_name = name[:-7] if name.endswith('.locked') else name
            st.session_state.decrypted_virtual[original_name] = decrypted_data
            decrypted += 1
        except Exception as e:
            st.error(f"Decryption error for {name}: {e}")
    return decrypted

def browse_folder():
    """Open folder browser dialog using tkinter"""
    if not TKINTER_AVAILABLE:
        return None
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(
            master=root,
            title="Select Folder to Encrypt"
        )
        root.destroy()
        return folder_path if folder_path else None
    except Exception as e:
        st.error(f"Browser error: {e}")
        return None

def load_demo_folder():
    # Create in-memory demo files to simulate a folder
    samples = [
        {"name": "report_Q4.pdf", "data": b"Demo PDF report content"},
        {"name": "family_photo.jpg", "data": b"JPEG_IMAGE_BYTES"},
        {"name": "song_sample.mp3", "data": b"MP3_AUDIO_BYTES"},
        {"name": "meeting_notes.txt", "data": b"These are sample meeting notes for awareness training."},
        {"name": "invoice.xlsx", "data": b"XLSX_BYTES"}
    ]
    st.session_state.target_mode = 'virtual'
    st.session_state.target_files = samples
    st.session_state.original_folder_name = 'Awareness_Demo_Folder'
    st.session_state.target_folder = 'DEMO'
    st.session_state.is_encrypted = False
    st.success("✅ Demo folder loaded (5 files)")
    return True

def set_uploaded_files(uploaded_files):
    file_entries = []
    for uf in uploaded_files:
        try:
            data = uf.read()
            file_entries.append({"name": uf.name, "data": data})
        except Exception as e:
            st.error(f"Failed to read {uf.name}: {e}")
    if file_entries:
        st.session_state.target_mode = 'virtual'
        st.session_state.target_files = file_entries
        st.session_state.original_folder_name = 'Uploaded_Folder'
        st.session_state.target_folder = 'UPLOADS'
        st.session_state.is_encrypted = False
        st.success(f"✅ Loaded {len(file_entries)} files for simulation")
        return True
    return False

def select_folder():
    st.markdown("**Select content to encrypt:**")

    # Option A: Demo virtual folder (cloud-safe)
    with st.expander("🎁 Use Demo Folder (cloud safe)", expanded=True):
        if st.button("Load Demo Folder", use_container_width=True):
            load_demo_folder()
            return 'virtual'

    # Option B: Upload multiple files (cloud safe)
    with st.expander("☁️ Upload Files (treat as folder)"):
        uploads = st.file_uploader(
            "Select multiple files (images, audio, video, docs)",
            accept_multiple_files=True,
            type=None,
            help="Uploaded files stay in memory and are encrypted/decrypted for the simulation"
        )
        if uploads:
            if set_uploaded_files(uploads):
                return 'virtual'

    # Option C: Local filesystem (requires local run)
    st.markdown("---")
    st.markdown("### 🖥️ Local Folder (requires local run)")

    if TKINTER_AVAILABLE:
        st.info("💻 Running locally - Folder browser available!")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📂 BROWSE FOLDER", use_container_width=True):
                folder = browse_folder()
                if folder:
                    st.session_state.selected_folder_path = folder
        with col2:
            default_path = st.session_state.get('selected_folder_path', '')
            folder_path = st.text_input(
                "📁 Folder Path:",
                value=default_path,
                placeholder="e.g., C:/Users/YourName/Documents/TestFolder",
                help="Browse for a folder or enter the full path manually",
                label_visibility="collapsed"
            )
    else:
        st.warning("☁️ Running on Streamlit Cloud - Local folders are unavailable. Use demo or upload files above.")
        folder_path = st.text_input(
            "📁 Folder Path (local only):",
            placeholder="Run locally to enable",
            disabled=True,
            help="Local folder access requires running 'streamlit run app.py' on your machine"
        )

    if folder_path:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            forbidden = ["Windows", "Program Files", "System32", "ProgramData"]
            if any(f in folder_path for f in forbidden):
                st.error("❌ Cannot target system folders!")
                return None
            files = get_files_in_folder(folder_path)
            if files:
                st.session_state.target_mode = 'local'
                st.session_state.target_files = files
                st.session_state.original_folder_name = os.path.basename(folder_path)
                st.session_state.target_folder = folder_path
                st.session_state.is_encrypted = False
                return folder_path
            else:
                st.error("❌ No files found in this folder")
        elif folder_path and TKINTER_AVAILABLE:
            st.error("❌ Folder path does not exist")

    return None

def restore_files():
    if not st.session_state.is_encrypted:
        return
    mode = st.session_state.get('target_mode')
    if mode == 'local' and 'encrypted_files' in st.session_state:
        file_count = len(st.session_state.encrypted_files)
        decrypted_count = 0
        for file_path in st.session_state.encrypted_files:
            if os.path.exists(file_path):
                if decrypt_local_file(file_path):
                    decrypted_count += 1
        st.session_state.is_encrypted = False
        st.success(f"✅ Folder decrypted! ({decrypted_count}/{file_count} files restored)")
    elif mode == 'virtual' and 'encrypted_virtual' in st.session_state:
        file_count = len(st.session_state.encrypted_virtual)
        decrypted_count = decrypt_virtual_files()
        st.session_state.is_encrypted = False
        st.success(f"✅ Virtual folder decrypted! ({decrypted_count}/{file_count} files restored)")

# --- PAGES ---

def page_education():
    st.markdown("<h1 style='text-align:center;'>RANSOMWARE SIMULATOR <span style='color:var(--neon-green); font-size:0.5em;'>V2.0</span></h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='cyber-card'>
        <h3>⚠️ SYSTEM WARNING</h3>
        <p>This is a safe, educational simulation environment designed to demonstrate the mechanics of ransomware attacks.</p>
        <hr style='border-color: rgba(255,255,255,0.1);'>
        <p style='color: var(--neon-green)'><b>MOBILE OPTIMIZED | REAL-TIME ENCRYPTION | INTERACTIVE LAB</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='cyber-card'><h3>🔍 The Threat</h3><p>Ransomware encrypts your data and demands payment. It often arrives via email attachments or cracked software.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='cyber-card'><h3>🛡️ The Defense</h3><p><b>Backups</b> are the only 100% guarantee. Antivirus helps, but human awareness is key.</p></div>", unsafe_allow_html=True)

    if st.button("INITIALIZE LAB ENVIRONMENT 🚀", use_container_width=True):
        st.session_state.page = "lab_setup"
        st.rerun()

def page_lab_setup():
    st.title("🧪 LAB CONFIGURATION")
    
    # Attack Variant Selector
    st.markdown("### 1. SELECT ATTACK PROFILE")
    variant = st.selectbox("Choose Malware Behavior:", ["Standard (CryptoLocker)", "Fast (WannaCry)", "Stealth (Background)"])
    st.session_state.attack_variant = variant
    
    st.markdown("### 2. SELECT BAIT FILE")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 Spotify_Premium_Mod.apk"):
            st.session_state.target_app_name = "Spotify Mod"
            st.session_state.show_warning = True
    with col2:
        if st.button("🎮 GTAV_Crack_Full.exe"):
            st.session_state.target_app_name = "GTA V Crack"
            st.session_state.show_warning = True
            
    if st.session_state.get('show_warning'):
        st.markdown(f"<div class='cyber-card' style='border-color: var(--neon-red); color: var(--neon-red);'>⚠️ WARNING: Unverified Source Detected: {st.session_state.target_app_name}</div>", unsafe_allow_html=True)
        
        if st.checkbox("IGNORE WARNING & PROCEED"):
            st.markdown("### 3. CHOOSE CONTENT SOURCE")
            selection = select_folder()
            if selection:
                folder_name = st.session_state.get('original_folder_name', 'Selected_Folder')
                files = st.session_state.get('target_files', [])
                st.success(f"📁 Target Ready: **{folder_name}** ({len(files)} files)")

                # Show file types breakdown
                file_types = {}
                for f in files:
                    ext = os.path.splitext(f if isinstance(f, str) else f['name'])[1].lower() or 'no extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                with st.expander("📂 View Contents"):
                    st.write("**File Types:**")
                    for ext, count in sorted(file_types.items()):
                        st.text(f"  {ext}: {count} file(s)")
                    st.write("\n**Files:**")
                    for f in files[:20]:  # Show first 20 files
                        fname = f if isinstance(f, str) else f['name']
                        st.text(f"📄 {os.path.basename(fname)}")
                    if len(files) > 20:
                        st.text(f"... and {len(files) - 20} more files")
                
                if st.button("☠️ EXECUTE PAYLOAD"):
                    st.session_state.page = "attack_run"
                    st.rerun()

def page_attack_run():
    st.empty()
    st.markdown("<h1 style='color:var(--neon-green); text-align:center;'>INSTALLING...</h1>", unsafe_allow_html=True)
    
    bar = st.progress(0)
    term = st.empty()
    
    speed = 0.01 if "Fast" in st.session_state.attack_variant else 0.03
    
    for i in range(100):
        time.sleep(speed)
        bar.progress(i + 1)
        if i % 10 == 0: term.code(f"> unpacking_payload_chunk_{i}.bin ... OK")
    
    st.markdown("<h1 style='color:var(--neon-red); text-align:center; animation: glitch 0.3s infinite;'>⚠️ SYSTEM BREACHED ⚠️</h1>", unsafe_allow_html=True)
    time.sleep(1)
    
    # Encryption
    mode = st.session_state.get('target_mode')
    files = st.session_state.get('target_files', [])

    if not mode or not files:
        st.error("No target selected. Please go back and choose a folder/files.")
        st.session_state.page = 'lab_setup'
        st.rerun()
    
    if not st.session_state.is_encrypted:
        encrypted_count = 0
        if mode == 'local':
            st.session_state.encrypted_files = []
            for f in files:
                if encrypt_local_file(f):
                    encrypted_count += 1
                if "Fast" not in st.session_state.attack_variant:
                    term.code(f"ENCRYPTING: {os.path.basename(f)}")
                    time.sleep(0.05)
        elif mode == 'virtual':
            st.session_state.encrypted_virtual = {}
            encrypted_count = encrypt_virtual_files(files)
            if "Fast" not in st.session_state.attack_variant:
                for entry in files[:10]:
                    term.code(f"ENCRYPTING: {os.path.basename(entry['name'])}")
                    time.sleep(0.05)
        st.session_state.is_encrypted = True
        st.session_state.attack_start_time = datetime.now()
        term.code(f"\n✓ ENCRYPTION COMPLETE: {encrypted_count} files locked")
    
    st.session_state.page = "ransom_screen"
    st.rerun()

def page_ransom_screen():
    # Timer
    remaining = timedelta(minutes=2) # Default visual
    if st.session_state.attack_start_time:
        elapsed = datetime.now() - st.session_state.attack_start_time
        remaining = timedelta(minutes=2) - elapsed
        if remaining.total_seconds() <= 0:
            restore_files()
            st.session_state.page = "quiz"
            st.rerun()
            
    folder_name = st.session_state.get('original_folder_name', 'Your Folder')
    mode = st.session_state.get('target_mode')
    if mode == 'virtual':
        file_count = len(st.session_state.get('encrypted_virtual', {}))
    else:
        file_count = len(st.session_state.get('encrypted_files', []))
    
    st.markdown(f"""
    <div class='ransom-container'>
        <h1 style='color:white; font-size: 3rem;'>FOLDER ENCRYPTED</h1>
        <p>📁 <b>{folder_name}</b> - {file_count} files locked</p>
        <p>IDENTIFIER: {st.session_state.attack_variant.upper()}</p>
        <h2 style='font-family: monospace;'>{str(remaining).split('.')[0]}</h2>
        <p>Send 0.5 BTC to unlock your data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
         if st.button("💸 PAY RANSOM (Simulate)"):
             st.error("❌ ERROR: PAYMENT SERVER OFFLINE. (Most gangs just steal your money!)")
    with col2:
        if st.button("🔓 DECRYPT (Education Mode)"):
            restore_files()
            st.session_state.page = "quiz"
            st.rerun()
    
    # Show encrypted files
    if mode == 'virtual' and st.session_state.get('encrypted_virtual'):
        with st.expander("🔒 View Encrypted Files"):
            names = list(st.session_state.encrypted_virtual.keys())
            for name in names[:30]:
                st.text(f"❌ {os.path.basename(name)}")
            if len(names) > 30:
                st.text(f"... and {len(names) - 30} more locked files")
    elif st.session_state.get('encrypted_files'):
        with st.expander("🔒 View Encrypted Files"):
            for file_path in st.session_state.encrypted_files[:30]:
                st.text(f"❌ {os.path.basename(file_path)}")
            if len(st.session_state.encrypted_files) > 30:
                st.text(f"... and {len(st.session_state.encrypted_files) - 30} more locked files")
            
    time.sleep(1)
    st.rerun()

def page_quiz():
    # removed st.balloons() here
    st.title("✅ SYSTEM RESTORED")
    st.markdown("Files recovered. Now, let's verify your knowledge.")
    
    st.markdown("<div class='cyber-card'><h3>🧠 ADVANCED KNOWLEDGE CHECK</h3>", unsafe_allow_html=True)
    
    questions = {
        "q1": {"text": "1. What is the #1 most effective defense against ransomware?", 
               "options": ["Antivirus Software", "Regular Offline Backups", "Firewalls", "Strong Passwords"], 
               "answer": "Regular Offline Backups"},
        "q2": {"text": "2. Why are 'cracked' software downloads dangerous?", 
               "options": ["They are illegal", "They are often trojans for malware", "They use too much CPU", "They don't get updates"], 
               "answer": "They are often trojans for malware"},
        "q3": {"text": "3. What should be your FIRST action if you suspect infection?", 
               "options": ["Pay the ransom", "Disconnect from the Internet/Network", "Delete all files", "Restart the computer"], 
               "answer": "Disconnect from the Internet/Network"},
        "q4": {"text": "4. What does 'Phishing' refer to?", 
               "options": ["Fishing for compliments", "Fraudulent emails mimicking trusted sources", "Hacking WiFi", "A type of virus"], 
               "answer": "Fraudulent emails mimicking trusted sources"},
        "q5": {"text": "5. Does paying the ransom GUARANTEE you get your files back?", 
               "options": ["Yes, hackers are honest", "No, there is no guarantee", "Yes, legally they must", "Only if you pay in Bitcoin"], 
               "answer": "No, there is no guarantee"},
        "q6": {"text": "6. What is the purpose of Encryption in a ransomware attack?", 
               "options": ["To steal passwords", "To mine crypto", "To make data unreadable without a key", "To delete the OS"], 
               "answer": "To make data unreadable without a key"},
        "q7": {"text": "7. Which file extension should you be most wary of receiving in email?", 
               "options": [".pdf", ".jpg", ".exe / .vbs", ".txt"], 
               "answer": ".exe / .vbs"},
        "q8": {"text": "8. What is Multi-Factor Authentication (MFA)?", 
               "options": ["Using two passwords", "Using a password + a code from your phone", "Scanning for viruses", "Changing IP address"], 
               "answer": "Using a password + a code from your phone"},
        "q9": {"text": "9. If a pop-up says 'Your Computer is Infected, Call Support', it is likely:", 
               "options": ["A helpful Microsoft alert", "A Tech Support Scam", "A Windows update", "Real antivirus"], 
               "answer": "A Tech Support Scam"},
        "q10": {"text": "10. Why do attackers prefer cryptocurrency?", 
               "options": ["It is harder to trace than bank transfers", "It is worthless", "It is easy to buy", "Banks like it"], 
               "answer": "It is harder to trace than bank transfers"}
    }
    
    score = 0
    # Use a form so the page doesn't reload on every radio click
    with st.form("quiz_form"):
        user_answers = {}
        for k, v in questions.items():
            st.markdown(f"**{v['text']}**")
            # index=None ensures no default selection
            user_answers[k] = st.radio(label="Select Answer:", options=v["options"], key=k, index=None, label_visibility="collapsed")
            st.markdown("---")
            
        submitted = st.form_submit_button("SUBMIT ANSWERS")
        
    if submitted:
        for k, v in questions.items():
            if user_answers[k] == v["answer"]:
                score += 1
        
        st.session_state.quiz_score = score
        
        if score >= 9:
            st.success(f"🏆 ELITE DEFENDER! Score: {score}/10")
        elif score >= 7:
            st.info(f"✅ PASSED. Score: {score}/10. Good job.")
        else:
            st.error(f"❌ FAILED. Score: {score}/10. You need to review cyber hygiene basics.")
            
        st.markdown("### 🔍 Attack Timeline Summary")
        folder_name = st.session_state.get('original_folder_name', 'test_folder')
        folder_path = st.session_state.get('target_folder', 'N/A')
        mode = st.session_state.get('target_mode')
        if mode == 'virtual':
            file_count = len(st.session_state.get('encrypted_virtual', {}))
            location_text = "In-memory simulation (cloud-safe)"
        else:
            file_count = len(st.session_state.get('encrypted_files', []))
            location_text = folder_path
        st.code(f"1. User downloaded {st.session_state.get('target_app_name')} (Trojan)\n2. Malware executed {st.session_state.attack_variant} encryption\n3. Target '{folder_name}' locked with AES-256\n   Location: {location_text}\n   Files affected: {file_count}\n4. Files restored with decryption key")
        
        st.success("✅ All files have been decrypted and restored!")
        
        if st.button("RESTART SIMULATION"):
            # Clear all session state
            for key in ['page', 'is_encrypted', 'attack_start_time', 'target_files', 
                       'encrypted_files', 'encrypted_virtual', 'decrypted_virtual',
                       'target_folder', 'original_folder_name', 'target_mode', 'selected_folder_path']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = 'education'
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTER ---
pages = {
    'education': page_education,
    'lab_setup': page_lab_setup,
    'attack_run': page_attack_run,
    'ransom_screen': page_ransom_screen,
    'quiz': page_quiz
}

if st.session_state.page in pages:
    pages[st.session_state.page]()
