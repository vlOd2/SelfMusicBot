import subprocess
from datetime import datetime, timezone

def get_video_duration(input):
    args = f"ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}"
    process = subprocess.Popen(args, text=True, stdout=subprocess.PIPE)
    ffprobe_result = process.stdout.readline().strip()
    process.kill()

    if not ffprobe_result or len(ffprobe_result) < 1:
        return -1
    
    try:
        return int(float(ffprobe_result) * 1000)
    except:
        return -1

def get_secs_formatted(seconds):
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return timestamp.strftime('%H:%M:%S') if timestamp.hour > 0 else timestamp.strftime('%M:%S')

def strip_unicode(str):
    return str.encode("ascii", "ignore").decode("ascii")

def get_progress_bar(blocks_done, size=10):
    progress_bar = ""

    for i in range(size):
        if i <= int(blocks_done * size):
            progress_bar += ":white_large_square:"
        else:
            progress_bar += ":black_large_square:"
    
    return progress_bar