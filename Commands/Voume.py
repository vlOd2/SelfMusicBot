import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot
from FFmpegAudioSource import FFmpegAudioSource

@CommandDeclaration("volume", CommandHandler("Gets/Sets the player volume", needs_admin=True))
async def cmd_volume(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    volume_level = float(args[0]) if len(args) > 0 and args[0].isnumeric() else 0
    audio_source : (FFmpegAudioSource | None) = instance.get_voice_client().source

    if len(args) < 1 or not args[0].isnumeric():
        await message.reply(f":information_source: Current volume is {instance.voice_volume * 100}")
        return

    if volume_level < 0 or volume_level > 200:
        await message.reply(":x: Volume must be between 0 and 200 (inclusive)!")
        return

    instance.voice_volume = volume_level / 100
    if audio_source: audio_source.volume = instance.voice_volume
    await message.add_reaction("✅")