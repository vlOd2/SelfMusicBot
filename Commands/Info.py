import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot
from YoutubeAudioSource import YoutubeAudioSource
from time import time

@CommandDeclaration("info", CommandHandler("Gets information on what is currently being streamed"))
@CommandDeclaration("nowplaying", CommandHandler("Alias for the command \"info\""))
@CommandDeclaration("np", CommandHandler("Alias for the command \"info\""))
async def cmd_info(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    audio_source : (YoutubeAudioSource | None) = instance.get_voice_client().source

    if audio_source:
        audio_data = audio_source.data
        audio_title = Utils.strip_unicode(audio_data["title"])
        audio_requester = instance.get_user(audio_data['discord_user_id'])

        audio_duration = audio_data['duration']
        audio_time_elapsed = int(time()) - audio_source.start_time if audio_duration > 0 else 0
        progress_bar_progress = audio_time_elapsed / audio_duration if audio_duration > 0 else 0

        info_msg = f":notes: Currently streaming [{audio_title}](<{audio_data['webpage_url']}>):\n"
        info_msg += f":arrow_up: Requested by {audio_requester}\n"
        info_msg += f":clock3: {Utils.get_secs_formatted(audio_time_elapsed)}/{Utils.get_secs_formatted(audio_duration)}\n"
        info_msg += f"{Utils.get_progress_bar(progress_bar_progress)} "

        await message.reply(info_msg)
    else:
        await message.reply(f":information_source: Nothing is being streamed right now")