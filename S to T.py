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
import audioop
import numpy as np


warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# ------------------------------
# SETTINGS
# ------------------------------
config = configparser.ConfigParser()
settings_file = "settings.ini"


def load_settings():
    # Load existing if present
    if os.path.exists(settings_file):
        config.read(settings_file)

    # Ensure sections exist
    if "Keys" not in config:
        config["Keys"] = {}
    if "Audio" not in config:
        config["Audio"] = {}

    # Set defaults if missing (auto-upgrade old settings.ini)
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

    # If we added anything, write it back once
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



def check_gpu():
    if torch.cuda.is_available():
        print(f"✅ GPU FOUND: {torch.cuda.get_device_name(0)}")
        return "cuda"
    print("⚠️ GPU NOT FOUND: Using CPU (Slower)")
    return "cpu"


# ------------------------------
# HELPERS
# ------------------------------
def flush_console_input():
    """Prevents 'gibberish' keys showing up in the console after hook-based input."""
    if os.name == "nt":
        import msvcrt

        while msvcrt.kbhit():
            msvcrt.getch()


def scan_code_to_name(scan_code):
    """Best-effort mapping scan code -> readable key name."""
    try:
        for k, codes in keyboard.key_to_scan_codes.items():
            if scan_code in codes:
                return k.title()
    except Exception:
        pass
    return f"Scan Code {scan_code}"


# ------------------------------
# SCAN CODE KEY STATE TRACKING (CRITICAL FOR VTT)
# ------------------------------
pressed_scan_codes = set()


def key_state_handler(event):
    if event.event_type == keyboard.KEY_DOWN:
        pressed_scan_codes.add(event.scan_code)
    elif event.event_type == keyboard.KEY_UP:
        pressed_scan_codes.discard(event.scan_code)


# ------------------------------
# KEY TESTER (NAME + SCANCODE)
# ------------------------------
def run_key_tester():
    _, _, quit_key, quit_name, _ = load_settings()

    print("\n" + "=" * 35)
    print("KEY TESTER MODE")
    print("Press any key to see name + scan code")
    print(f"Press {quit_name} to return")
    print("=" * 35)

    running = True

    def on_event(event):
        nonlocal running
        if event.event_type == keyboard.KEY_DOWN:
            if event.scan_code == quit_key:
                running = False
                return
            name = event.name or "Unknown"
            print(f"Key: {name.title()} | Scan Code: {event.scan_code}")

    hook = keyboard.hook(on_event)
    while running:
        time.sleep(0.01)
    keyboard.unhook(hook)

    flush_console_input()


# ------------------------------
# PRESS-A-KEY-TO-BIND (SIMPLE)
# ------------------------------
def capture_key_once():
    print("\nPress a key now...")

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


def key_menu():
    while True:
        record_key, record_name, quit_key, quit_name, _ = load_settings()

        os.system("cls" if os.name == "nt" else "clear")
        print("==============================")
        print("  CHANGE KEYS")
        print("==============================")
        print(f"Record Key: {record_name} (Scan Code {record_key})")
        print(f"Quit Key:   {quit_name} (Scan Code {quit_key})")
        print("------------------------------")
        print("1. Set Record Key")
        print("2. Set Quit Key")
        print("3. Back")

        choice = input("\nSelect (1-3): ")

        if choice == "1":
            scan, name = capture_key_once()
            save_key("record_key", "record_name", scan, name)
            print(f"Saved Record Key: {name.title()} (Scan Code {scan})")
            time.sleep(1)

        elif choice == "2":
            scan, name = capture_key_once()
            save_key("quit_key", "quit_name", scan, name)
            print(f"Saved Quit Key: {name.title()} (Scan Code {scan})")
            time.sleep(1)

        elif choice == "3":
            break



# ------------------------------
# VOICE TOOL (SCAN-CODE SAFE)
# ------------------------------
def run_voice_tool():
    record_key, record_name, quit_key, quit_name, model_size = load_settings()
    device = check_gpu()

    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size, device=device)

    print("\n✅ READY!")
    print(f"Hold {record_name} to talk")
    print(f"Press {quit_name} to return")

    hook = keyboard.hook(key_state_handler)

    while True:
        if record_key in pressed_scan_codes:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
            )

            frames = []
            winsound.Beep(800, 100)
            print("🔴 Recording...")

            while record_key in pressed_scan_codes:
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)

            winsound.Beep(400, 150)
            print("⏳ Processing...")

            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Join recorded frames (16-bit PCM @ 44100 Hz)
            pcm_44k = b"".join(frames)

            # Resample to 16000 Hz (Whisper expects 16 kHz audio)
            pcm_16k, _ = audioop.ratecv(pcm_44k, 2, 1, 44100, 16000, None)

            # Convert to float32 numpy array in [-1, 1]
            audio_np = np.frombuffer(pcm_16k, np.int16).astype(np.float32) / 32768.0

            # Transcribe directly from audio array (no ffmpeg needed)
            result = model.transcribe(audio_np)
            text = result["text"].strip()

            if text:
                pyperclip.copy(text)
                print(f"Copied: {text}")
                winsound.Beep(523, 150)
                winsound.Beep(659, 200)
            else:
                print("⚠️ No speech detected.")

        if quit_key in pressed_scan_codes:
            break

        time.sleep(0.01)

    keyboard.unhook(hook)
    pressed_scan_codes.clear()


# ------------------------------
# MAIN MENU
# ------------------------------
def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("==============================")
        print("  GAMER S TO T TOOL")
        print("==============================")
        print("1. Start Voice-to-Text")
        print("2. Find a Key (Key Tester)")
        print("3. Change Keys")
        print("4. Exit")

        flush_console_input() 
        choice = input("\nSelect (1-4): ")

        if choice == "1":
            run_voice_tool()
        elif choice == "2":
            run_key_tester()
        elif choice == "3":
            key_menu()
        elif choice == "4":
            break


if __name__ == "__main__":
    main()
