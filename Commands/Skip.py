import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("skip", CommandHandler("Skips the current song and streams the next item in queue"))
async def cmd_skip(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    instance.get_voice_client().stop()
    await message.add_reaction("✅")