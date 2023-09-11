import discord
import textwrap
from Commands.CommandHandler import CommandDeclaration, CommandHandler, REGISTERED_CMDS
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("help", CommandHandler("Provides a list of available commands",
                                           needs_join_voice_channel=False, 
                                           needs_listening_executor=False, 
                                           needs_same_guild=False))
async def cmd_help(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    help_message = ":information_source: Available commands:\n\n** Users **\n"
    for cmd, cmd_handler in REGISTERED_CMDS.items():
        if cmd_handler.needs_admin: continue
        help_message += f"{cmd} - {cmd_handler.description}\n"
        
    help_message += "\n** Administrators **\n"
    for cmd, cmd_handler in REGISTERED_CMDS.items():
        if not cmd_handler.needs_admin: continue
        help_message += f"{cmd} - {cmd_handler.description}\n"

    for msg_chunk in textwrap.wrap(help_message, width=2000, break_long_words=False, replace_whitespace=False):
        await message.reply(msg_chunk)