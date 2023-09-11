import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("join", CommandHandler("Joins the defined voice channel",
                                           needs_join_voice_channel=False, 
                                           needs_listening_executor=False))
async def cmd_join(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if not instance.voice_channel:
        await message.reply(":x: The voice channel for me to join into hasn't been defined!")
        return

    if instance.get_voice_client():
        await message.reply(":x: I am already in the voice channel!")
        return
    
    instance.logger.info(f"Joining voice channel {instance.voice_channel.id} in guild {guild.id}...")
    instance._voice_client = await instance.voice_channel.connect()
    await message.add_reaction("✅")