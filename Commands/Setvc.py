import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("setvc", CommandHandler("Defines the voice channel to join (only for this session)",
                                            needs_join_voice_channel=False, 
                                            needs_listening_executor=False, 
                                            needs_same_guild=False,
                                            needs_admin=True))
async def cmd_setvc(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1 or not args[0].isnumeric():
        await message.reply(f":information_source: setvc <channel ID>")
        return
    
    await instance.leave_voice_channel()
    channel_id = int(args[0])
    channel = guild.get_channel(channel_id)

    if not channel or not isinstance(channel, discord.channel.VoiceChannel):
        await message.reply(f":x: Not a voice channel!")
        return

    instance.voice_channel = channel
    instance.logger.info(f"Set the voice channel to {instance.voice_channel.id} in guild")
    await message.reply(f":white_check_mark: Set the voice channel to {channel.jump_url}")