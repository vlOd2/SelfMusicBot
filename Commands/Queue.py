import discord
import textwrap
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

@CommandDeclaration("queue", CommandHandler("Provides a list of the queue",
                                           needs_join_voice_channel=True, 
                                           needs_listening_executor=False, 
                                           needs_same_guild=True))
async def cmd_queue(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(instance.music_queue) < 1:
        await message.reply(":information_source: There are no songs in the queue")
        return

    queue_message = ":arrow_right_hook: Songs in the queue list:\n\n"
    for index, song in enumerate(instance.music_queue):
        title = Utils.strip_unicode(song["title"])
        requester = instance.get_user(song['discord_user_id'])
        queue_message += f"`{index}.` [{Utils.get_secs_formatted(song['duration'])}]" 
        queue_message += f" [{title}](<{song['webpage_url']}>) - {requester}\n"

    for msg_chunk in textwrap.wrap(queue_message, width=2000, break_long_words=False, replace_whitespace=False):
        await message.reply(msg_chunk)