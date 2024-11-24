import sys
import shutil
import traceback


def check_python_compatibility(required_version: tuple) -> None:
    current = sys.version_info[:2]
    if current < required_version:
        raise RuntimeError(
            f"This bot requires Python {'.'.join(map(str, required_version))} or higher. "
            f"You are using Python {'.'.join(map(str, current))}"
        )


def check_ffmpeg() -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg not found. Please ensure FFmpeg is installed and available in PATH."
        )


if __name__ == "__main__":
    try:
        check_python_compatibility((3, 12))
        check_ffmpeg()

        import bot
        bot.run_bot()
    except Exception as e:
        print(f"Error during startup: {e}")
        print(traceback.format_exc())
        sys.exit(1)
