import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("stop", CommandHandler("Stops the current song and clears the queue"))
async def cmd_stop(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    instance.music_queue.clear()
    instance.get_voice_client().stop()
    instance.logger.info("Stopped streaming and cleared the queue")
    await message.add_reaction("✅")