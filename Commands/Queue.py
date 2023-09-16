import discord
import textwrap
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot
from FFmpegAudioSource import FFmpegAudioSource

@CommandDeclaration("queue", CommandHandler("Provides a list of the queue"))
async def cmd_queue(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(instance.music_queue) < 1:
        await message.reply(":information_source: There are no songs in the queue")
        return

    page_size = 5
    pages_data = []
    page_index = int(args[0]) if len(args) > 0 and args[0].isnumeric() else 0

    # Calculate the queue pages
    for i in range(0, len(instance.music_queue), page_size): 
        pages_data.append(instance.music_queue[i:i + page_size])

    if page_index < 0 or page_index > len(pages_data) - 1:
        await message.reply(":x: Page index is outside the queue range!")
        return

    queue_message = ":arrow_right_hook: Songs in the queue list:\n\n"
    queue_message += f"📃 Queue page {page_index}/{len(pages_data) - 1}\n"

    current_audio_source : (FFmpegAudioSource | None) = instance.get_voice_client().source
    if current_audio_source:
        current_audio_data = current_audio_source.data
        current_audio_title = Utils.strip_unicode(current_audio_data["title"])
        queue_message += f":notes: Currently streaming [`{current_audio_title}`](<{current_audio_data['webpage_url']}>)\n\n"
    else:
        queue_message += f":information_source: Nothing is being streamed right now\n\n"

    for song in pages_data[page_index]:
        requester = instance.get_user(song['__discord_user_id'])
        is_flat_queue : bool = song["__is_flat_queue"]

        title = Utils.strip_unicode(song["title"])
        url = song["webpage_url"] if not is_flat_queue else song["url"]
        duration = Utils.get_secs_formatted(song['duration']) if not is_flat_queue else "-"

        queue_message += f"{instance.music_queue.index(song)}\. [{duration}]" 
        queue_message += f" [`{title}`](<{url}>) - {requester}\n"

    for msg_chunk in textwrap.wrap(queue_message, width=2000, break_long_words=False, replace_whitespace=False):
        await message.reply(msg_chunk)