import argparse
import subprocess
import sys
import time
from pathlib import Path

try:
    import speech_recognition as sr
except ImportError:
    print("Missing dependency: SpeechRecognition. Install with: pip install SpeechRecognition")
    raise


def run_batch_file(batch_file_path: Path) -> None:
    """Run a .bat file in a new console window on Windows."""
    if not batch_file_path.exists():
        print(f"Error: Batch file not found: {batch_file_path}")
        return

    # Use cmd to execute the batch file so PATH and internal commands work as expected
    try:
        subprocess.Popen(
            ["cmd", "/c", str(batch_file_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print(f"Launched: {batch_file_path}")
    except Exception as exc:
        print(f"Failed to launch batch file: {exc}")


    


def listen_and_execute(target_phrase: str, batch_file_path: Path) -> None:
    """Continuously listen on the default microphone and execute the batch file when the target phrase is heard."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        microphone = sr.Microphone()
    except OSError as exc:
        print("No microphone found or microphone is unavailable.")
        print(exc)
        sys.exit(1)

    print("Initializing microphone. Please remain quiet...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2.0)
    print("Listening for the phrase:", f'"{target_phrase}"')

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            try:
                text = recognizer.recognize_google(audio)
                normalized = text.strip().lower()
                print(f"Heard: {text}")
                if target_phrase.lower() in normalized:
                    print("Trigger phrase detected. Executing batch file...")
                    run_batch_file(batch_file_path)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as exc:
                print(f"Speech recognition service error: {exc}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except sr.WaitTimeoutError:
            continue
        except Exception as exc:
            print(f"Unexpected error: {exc}")
            time.sleep(5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Listen for 'launch jarvis' and run JARVIS_START.bat.")
    parser.add_argument(
        "--bat",
        dest="bat_path",
        type=str,
        default=str(Path(__file__).parent.parent / "JARVIS_START.bat"),
        help="Path to the .bat file to execute when the phrase is detected (default: JARVIS_START.bat in parent directory)",
    )
    parser.add_argument(
        "--phrase",
        dest="phrase",
        type=str,
        default="launch jarvis",
        help="The wake phrase to listen for (default: 'launch jarvis')",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch_file_path = Path(args.bat_path).expanduser().resolve()
    
    # Verify the batch file exists before starting
    if not batch_file_path.exists():
        print(f"Error: Batch file not found: {batch_file_path}")
        print("Please ensure the JARVIS_START.bat file exists in the project root directory.")
        sys.exit(1)
    
    print(f"Using batch file: {batch_file_path}")
    listen_and_execute(args.phrase, batch_file_path)


if __name__ == "__main__":
    main()


