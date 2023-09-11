import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot
from YoutubeAudioSource import YoutubeAudioSource

@CommandDeclaration("stream", CommandHandler("Streams the specified query (can be a link or a search query)"))
@CommandDeclaration("play", CommandHandler("Alias for the command \"stream\""))
async def cmd_stream(instance : SelfMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1:
        await message.reply(":x: No query specified!")
        return

    if instance.is_searching:
        await message.reply(":x: Cannot search for another query when already searching")
        return

    query = " ".join(args)
    instance.logger.info(f"Getting data for query \"{query}\"...")
    stream_msg = await message.reply(f":hourglass: Resolving query `{query}`...")

    async def stream_callback(error_msg):
        if error_msg:
            await stream_msg.edit(f":x: An error has occured: {error_msg}")
        else:
            audio_data = instance.get_voice_client().source.data
            await stream_msg.edit(f":notes: Now streaming [{audio_data['title']}]({audio_data['webpage_url']})" + 
                                f" (duration: {Utils.get_secs_formatted(audio_data['duration'])})")

    try:
        instance.is_searching = True
        audio_data = await YoutubeAudioSource.get_data_from_query(query)
        audio_data["discord_user_id"] = message.author.id
    except Exception as ex:
        await stream_callback(str(ex))
        return
    finally:
        instance.is_searching = False

    if instance.get_voice_client().source:
        instance.music_queue.append(audio_data)
        instance.logger.info(f"Added \"{audio_data['url']}\" to the queue")
        await stream_msg.edit(f":white_check_mark: Added [{audio_data['title']}]({audio_data['webpage_url']}) to the queue" + 
                            f" (duration: {Utils.get_secs_formatted(audio_data['duration'])})")
        return

    await instance.stream_data_voice_channel(audio_data, stream_callback)