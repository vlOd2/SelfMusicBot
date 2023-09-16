from typing import Any
import discord
import Utils
import YoutubeDL
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot

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

    if instance.is_resolving:
        await message.reply(":x: Cannot resolve for another query when already resolving")
        return

    query = " ".join(args)
    instance.logger.info(f"Getting data for query \"{query}\"...")
    stream_msg = await message.reply(f":hourglass: Resolving query `{query}`...")

    async def stream_callback(error_msg):
        if error_msg:
            await stream_msg.edit(f":x: An error has occured: {error_msg}")
        else:
            stream_data = instance.get_voice_client().source.data
            title = Utils.strip_unicode(stream_data["title"])
            await stream_msg.edit(f":notes: Now streaming [`{title}`]({stream_data['webpage_url']})" + 
                                f" (duration: {Utils.get_secs_formatted(stream_data['duration'])})")

    try:
        instance.is_resolving = True

        instance.logger.info("Getting flat data first for query to know if it is a playlist")
        flat_stream_data = await YoutubeDL.get_flat_query_raw_data(query)
        flat_stream_data_length = len(flat_stream_data["entries"]) if "entries" in flat_stream_data else 0
        stream_data = None

        # Check if the provided query is a playlist
        if flat_stream_data_length > 1:
            instance.logger.info("Query is a playlist, adding entries to queue")

            flat_stream_data_entries : list[dict[str, Any]] = flat_stream_data["entries"]
            items_added = 0

            i = 0
            while i < len(flat_stream_data_entries):
                entry = flat_stream_data_entries[i]

                if i == 0:
                    try:
                        instance.logger.info("Using first entry as play target")
                        stream_data = await YoutubeDL.get_query_data(entry["url"])
                    except Exception as ex:
                        instance.logger.error(f"Attempting to resolve first entry failed, trying next one as first: {ex}")
                        flat_stream_data_entries.remove(entry)
                        continue
                else:
                    entry["__discord_user_id"] = message.author.id
                    entry["__is_flat_queue"] = True
                    instance.music_queue.append(entry)
                    instance.logger.info(f"Added \"{entry['url']}\" to the queue")
                    items_added += 1

                i += 1
            
            if not stream_data:
                raise Exception("No valid video found in the specified playlist")
            
            if items_added > 0:
                await message.reply(f":white_check_mark: Added {items_added} playlist items to the queue")
        else:
            instance.logger.info("Query is not a playlist")
            stream_data = await YoutubeDL.get_query_data(query)

        stream_data["__discord_user_id"] = message.author.id
        stream_data["__is_flat_queue"] = False
    except Exception as ex:
        await stream_callback(str(ex))
        return
    finally:
        instance.is_resolving = False

    if instance.get_voice_client().source:
        title = Utils.strip_unicode(stream_data["title"])
        instance.music_queue.append(stream_data)
        instance.logger.info(f"Added \"{stream_data['url']}\" to the queue")
        await stream_msg.edit(f":white_check_mark: Added [`{title}`]({stream_data['webpage_url']}) to the queue" + 
                            f" (duration: {Utils.get_secs_formatted(stream_data['duration'])})")
        return

    await instance.stream_data_voice_channel(stream_data, stream_callback)