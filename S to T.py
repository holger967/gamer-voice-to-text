import keyboard
import whisper
import pyperclip
import time
import torch
import pyaudio
import wave
import winsound
import os
import configparser
import warnings
import traceback
import datetime
import shutil

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# ------------------------------
# LOGGING SYSTEM (NEW)
# ------------------------------
LOG_FILE = "last_run_log.txt"

def start_new_log():
    """Wipes the old log and starts a new one for this session."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== SESSION STARTED: {timestamp} ===\n")

def log(message):
    """Prints to console AND writes to the log file."""
    # 1. Print to screen so you can see it
    print(message)
    
    # 2. Save to file so you can read it later if it crashes
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass # If logging fails, don't crash the program

def log_crash(e):
    """Logs the technical error details if a crash happens."""
    error_trace = traceback.format_exc()
    log(f"\n❌ CRASH DETECTED: {e}")
    
    # Write full technical details to file only
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n--- TECHNICAL ERROR DETAILS ---\n")
            f.write(error_trace)
            f.write("-------------------------------\n")
    except Exception:
        pass
    
    print("📄 Check 'last_run_log.txt' to see what happened.")


# ------------------------------
# SETTINGS
# ------------------------------
config = configparser.ConfigParser()
settings_file = "settings.ini"


def load_settings():
    if os.path.exists(settings_file):
        config.read(settings_file)

    if "Keys" not in config:
        config["Keys"] = {}
    if "Audio" not in config:
        config["Audio"] = {}

    changed = False

    if not config.has_option("Keys", "record_key"):
        config.set("Keys", "record_key", "71"); changed = True
    if not config.has_option("Keys", "record_name"):
        config.set("Keys", "record_name", "Home"); changed = True

    if not config.has_option("Keys", "quit_key"):
        config.set("Keys", "quit_key", "79"); changed = True
    if not config.has_option("Keys", "quit_name"):
        config.set("Keys", "quit_name", "End"); changed = True

    if not config.has_option("Audio", "model_size"):
        config.set("Audio", "model_size", "medium"); changed = True

    if changed:
        with open(settings_file, "w") as f:
            config.write(f)

    return (
        config.getint("Keys", "record_key"),
        config.get("Keys", "record_name"),
        config.getint("Keys", "quit_key"),
        config.get("Keys", "quit_name"),
        config.get("Audio", "model_size"),
    )


def save_key(key_code_name, key_name_name, scan_code, key_name):
    config.read(settings_file)
    if "Keys" not in config:
        config["Keys"] = {}
    config.set("Keys", key_code_name, str(scan_code))
    config.set("Keys", key_name_name, key_name.title())
    with open(settings_file, "w") as f:
        config.write(f)
    log(f"Settings saved: {key_name} assigned.")


def save_model(model_name):
    config.read(settings_file)
    if "Audio" not in config:
        config["Audio"] = {}
    config.set("Audio", "model_size", model_name)
    with open(settings_file, "w") as f:
        config.write(f)
    log(f"Settings saved: Model changed to {model_name}")


def check_gpu():
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        log(f"✅ GPU FOUND: {gpu_name}")
        return "cuda"
    log("⚠️ GPU NOT FOUND: Using CPU (Slower)")
    return "cpu"


# ------------------------------
# CLEANUP
# ------------------------------
def delete_temp_wav():
    if os.path.exists("temp.wav"):
        try:
            os.remove("temp.wav")
        except Exception:
            pass

def cleanup_models():
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
    
    if os.path.exists(cache_dir):
        print(f"\nFound Whisper cache at: {cache_dir}")
        print("⚠️  This will delete all downloaded AI models.")
        confirm = input("Are you sure? (yes/no): ").lower()
        
        if confirm == "yes":
            try:
                shutil.rmtree(cache_dir)
                log("✅ All AI models deleted. Space freed!")
            except Exception as e:
                log(f"❌ Could not delete: {e}")
        else:
            log("Cancelled.")
    else:
        log("\n✅ No cached models found.")
    
    time.sleep(2)


# ------------------------------
# MENUS
# ------------------------------
def maintenance_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("==============================")
        print("  MAINTENANCE")
        print("==============================")
        print("1. Delete AI Models (Free Space)")
        print("2. Back")
        
        choice = input("\nSelect (1-2): ")
        
        if choice == "1":
            cleanup_models()
        elif choice == "2":
            break


def change_model_menu():
    os.system("cls" if os.name == "nt" else "clear")
    print("==============================")
    print("  SELECT AI MODEL")
    print("==============================")
    print("1. tiny   (Fastest / Not smart)")
    print("2. base   (Fast / Okay)")
    print("3. small  (Balanced)")
    print("4. medium (Recommended)")
    print("5. large  (Slowest / Best)")
    print("------------------------------")
    
    choice = input("Select: ").lower().strip()
    mapping = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large"}
    if choice in mapping: choice = mapping[choice]

    if choice in ["tiny", "base", "small", "medium", "large"]:
        save_model(choice)
    else:
        log("Invalid choice.")
    time.sleep(1)


def capture_key_once():
    log("Waiting for key press...")
    captured = {}
    def on_event(event):
        if event.event_type == keyboard.KEY_DOWN:
            captured["scan_code"] = event.scan_code
            captured["name"] = event.name or "Unknown"
            keyboard.unhook(hook)
    hook = keyboard.hook(on_event)
    while "scan_code" not in captured:
        time.sleep(0.01)
    flush_console_input()
    return captured["scan_code"], captured["name"]


def key_settings_menu():
    while True:
        record_key, record_name, quit_key, quit_name, _ = load_settings()
        os.system("cls" if os.name == "nt" else "clear")
        print("==============================")
        print("  KEY SETTINGS")
        print("==============================")
        print(f"Record Key: {record_name}")
        print(f"Quit Key:   {quit_name}")
        print("------------------------------")
        print("1. Set Record Key")
        print("2. Set Quit Key")
        print("3. Back")

        choice = input("\nSelect (1-3): ")

        if choice == "1":
            scan, name = capture_key_once()
            save_key("record_key", "record_name", scan, name)
        elif choice == "2":
            scan, name = capture_key_once()
            save_key("quit_key", "quit_name", scan, name)
        elif choice == "3":
            break


# ------------------------------
# VOICE TOOL
# ------------------------------
pressed_scan_codes = set()

def key_state_handler(event):
    if event.event_type == keyboard.KEY_DOWN:
        pressed_scan_codes.add(event.scan_code)
    elif event.event_type == keyboard.KEY_UP:
        pressed_scan_codes.discard(event.scan_code)

def run_voice_tool():
    record_key, record_name, quit_key, quit_name, model_size = load_settings()
    
    log(f"Initializing Voice Tool (Model: {model_size})...")
    device = check_gpu()

    try:
        model = whisper.load_model(model_size, device=device)
        log("Model loaded successfully.")
    except Exception as e:
        log_crash(e)
        input("Press Enter to return...")
        return

    print(f"\n✅ READY! Hold {record_name} to talk, {quit_name} to return.")
    
    hook = keyboard.hook(key_state_handler)

    try:
        while True:
            if record_key in pressed_scan_codes:
                audio = pyaudio.PyAudio()
                try:
                    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
                    frames = []
                    
                    winsound.Beep(800, 100)
                    print("🔴 Recording...", end="\r") # Print without newline to keep clean

                    while record_key in pressed_scan_codes:
                        data = stream.read(1024, exception_on_overflow=False)
                        frames.append(data)

                    winsound.Beep(400, 150)
                    print("⏳ Processing...         ", end="\r")

                    stream.stop_stream()
                    stream.close()
                    audio.terminate()

                    with wave.open("temp.wav", "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(44100)
                        wf.writeframes(b"".join(frames))

                    result = model.transcribe("temp.wav")
                    text = result["text"].strip()

                    if text:
                        pyperclip.copy(text)
                        log(f"Transcribed: {text}") # Logs what you said
                        winsound.Beep(523, 150)
                        winsound.Beep(659, 200)
                    else:
                        print("⚠️ No speech detected.      ")
                        
                    delete_temp_wav()

                except Exception as e:
                    log_crash(e)
                    time.sleep(1)

            if quit_key in pressed_scan_codes:
                log("User quit Voice Tool.")
                break
            time.sleep(0.01)
            
    except Exception as e:
        log_crash(e)
        input("Critical Error. Press Enter...")

    finally:
        keyboard.unhook(hook)
        pressed_scan_codes.clear()
        delete_temp_wav()


def flush_console_input():
    if os.name == "nt":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


# ------------------------------
# MAIN
# ------------------------------
def main():
    start_new_log() # <--- Wipes log at start
    delete_temp_wav()
    
    while True:
        try:
            _, _, _, _, model_size = load_settings()

            os.system("cls" if os.name == "nt" else "clear")
            print("==============================")
            print(f"  GAMER ACCESSIBILITY TOOL ({model_size})")
            print("==============================")
            print("1. Start Voice-to-Text")
            print("2. Change AI Model")
            print("3. Change Keys")
            print("4. Maintenance")
            print("5. Exit")

            flush_console_input() 
            choice = input("\nSelect (1-5): ")

            if choice == "1":
                run_voice_tool()
            elif choice == "2":
                change_model_menu()
            elif choice == "3":
                key_settings_menu()
            elif choice == "4":
                maintenance_menu()
            elif choice == "5":
                log("Program exited by user.")
                delete_temp_wav()
                break
        
        except Exception as e:
            log_crash(e)
            input("Menu Error. Press Enter to restart...")


if __name__ == "__main__":
    main()
