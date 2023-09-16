import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("remove", CommandHandler("Removes a song from the queue"))
async def cmd_remove(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1 or not args[0].isdigit():
        await message.reply(":information_source: remove <number>")
        return

    song_number = int(args[0])
    if song_number < 0 or song_number > (len(instance.music_queue) - 1):
        await message.reply(f":x: Song with the number {song_number} is not in the queue range")
        return
    
    del instance.music_queue[song_number]
    await message.add_reaction("✅")