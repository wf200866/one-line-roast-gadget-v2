"""One-line roast generator built around a streaming app's bingeing nag.

The behaviour we are poking at: after a handful of episodes the player pauses
to ask "Are you still watching?". In practice that automated prompt is the only
thing checking in on the viewer, and actually answering it turns into a hunt
for a remote that vanished several episodes back.
"""

import os
import stat
import tempfile

JOKE = (
    "Netflix asks 'Are you still watching?' after three episodes — my only "
    "wellness check, and answering it means finding the remote I lost two "
    "episodes ago."
)

LIMITS = (1, 200)
DEST_DIR = "/output"
DEST_FILE = "entry.txt"


def validate(text):
    """Gate the payload: non-blank and inside the allowed width."""
    if text is None or not text.strip():
        raise ValueError("refusing blank text")
    low, high = LIMITS
    size = len(text)
    if size < low or size > high:
        raise ValueError("length %d outside [%d, %d]" % (size, low, high))
    return text


def _mkdir_traversable(path):
    os.makedirs(path, exist_ok=True)
    entry = os.stat(path)
    if not stat.S_IMODE(entry.st_mode) & 0o111:
        raise PermissionError(path + " is not traversable")


def _write_temp(directory, payload):
    fd, temp_path = tempfile.mkstemp(prefix=".entry-", suffix=".tmp", dir=directory)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(payload)
    return temp_path


def _promote(temp_path, destination):
    os.chmod(temp_path, 0o644)
    os.replace(temp_path, destination)
    os.chmod(destination, 0o644)


def main():
    payload = validate(JOKE)
    _mkdir_traversable(DEST_DIR)
    destination = os.path.join(DEST_DIR, DEST_FILE)
    scratch = _write_temp(DEST_DIR, payload)
    try:
        _promote(scratch, destination)
    except BaseException:
        if os.path.exists(scratch):
            os.unlink(scratch)
        raise
    print("wrote %d chars to %s" % (len(payload), destination))


if __name__ == "__main__":
    main()
