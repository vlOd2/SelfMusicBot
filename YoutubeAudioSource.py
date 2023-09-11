import discord
import yt_dlp
import asyncio
from Utils import get_video_duration

def match_func(info_dict, incomplete=False):
    if "playlist" in info_dict and info_dict["playlist"] == "recommended":
        return "The playlist recommended is not allowed!"

    return None

YOUTUBEDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "break_on_reject": True,
    "match_filter": match_func,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": False,
    "no_warnings": False,
    "color": "no_color",
    "default_search": "auto",
    "source_address": "0.0.0.0"
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2",
    "options": "-vn"
}

class YoutubeAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.start_time = 0

    @classmethod
    async def get_from_data(clazz, data, volume=1):
        return clazz(discord.FFmpegPCMAudio(data["url"], **FFMPEG_OPTIONS), data, volume)
    
    @classmethod
    async def get_data_from_query(clazz, query):
        youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_OPTIONS)
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: youtubedl.extract_info(query, download=False))

        if "entries" in data:
            if len(data["entries"]) < 1:
                raise ValueError("The query has returned 0 results")
            data = data["entries"][0]

        # Calculate the duration if it doesn't exist (and also round it down)
        data["duration"] = int(data["duration"]) if "duration" in data else int(get_video_duration(data["url"]) / 1000)
        
        if data["duration"] < 0: 
            data["duration"] = 0

        return data
    
    @classmethod
    async def get_raw_data_from_query(clazz, query, flat=False):
        options = YOUTUBEDL_OPTIONS.copy()
        options["extract_flat"] = True
        youtubedl = yt_dlp.YoutubeDL(options)
        return await asyncio.get_event_loop().run_in_executor(None, lambda: youtubedl.extract_info(query, download=False))