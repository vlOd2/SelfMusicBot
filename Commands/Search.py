import discord
import asyncio
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from SelfMusicBot import SelfMusicBot
from YoutubeAudioSource import YoutubeAudioSource
from .Stream import cmd_stream

@CommandDeclaration("search", CommandHandler("Searches a query and provides the results",
                                           needs_join_voice_channel=True, 
                                           needs_listening_executor=True, 
                                           needs_same_guild=True))
async def cmd_search(instance : SelfMusicBot, 
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
    instance.logger.info(f"Getting raw data for query \"{query}\"...")
    search_msg = await message.reply(f":hourglass: Resolving query `{query}`...")

    try:
        instance.is_searching = True
        search_data = await YoutubeAudioSource.get_raw_data_from_query(f"ytsearch10:{query}", True)
        search_entries = search_data["entries"]
    except Exception as ex:
        await message.reply(f":x: An error has occured: {ex}")
        return
    finally:
        instance.is_searching = False

    if not "entries" in search_data or len(search_entries) < 1:
        await message.reply(":x: No results were found")
        return
    
    search_msg_content = ":mag: Search entries:\n\n"
    for index, entry in enumerate(search_entries):
        title = Utils.strip_unicode(entry["title"])
        search_msg_content += f"`{index}.` [{title}](<{entry['url']}>)\n"

    await search_msg.edit(search_msg_content)
    search_msg_reactions = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    valid_msg_reactions = []

    for i in range(len(search_entries)):
        await search_msg.add_reaction(search_msg_reactions[i])
        valid_msg_reactions.append(search_msg_reactions[i])

    async def add_reaction(reaction : discord.Reaction, user : discord.User):
        if not str(reaction.emoji) in valid_msg_reactions:
            await search_msg.edit(":x: Invalid reaction!")
            return
        
        match str(reaction.emoji):
            case "0️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[0]["url"]])
            case "1️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[1]["url"]])
            case "2️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[2]["url"]])
            case "3️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[3]["url"]])
            case "4️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[4]["url"]])
            case "5️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[5]["url"]])
            case "6️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[6]["url"]])
            case "7️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[7]["url"]])
            case "8️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[8]["url"]])
            case "9️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[9]["url"]])

    await instance.wait_for("reaction_add", check=lambda reaction, user: 
                            asyncio.run_coroutine_threadsafe(add_reaction(reaction, user), instance.loop))