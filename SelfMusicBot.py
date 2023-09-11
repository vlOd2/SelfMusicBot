import discord
import logging
import asyncio
from Config import Config
from Commands.CommandHandler import REGISTERED_CMDS, CommandHandler
from YoutubeAudioSource import YoutubeAudioSource
from typing import Any
from time import time

COMMAND_PREFIX = "-"

class SelfMusicBot(discord.Client):
    def __init__(self, config : Config, **options) -> None:
        super().__init__(**options)
        self.config : Config = config
        self.voice_channel : (discord.channel.VoiceChannel | None) = None
        self._voice_client : (discord.voice_client.VoiceClient | None) = None
        self.voice_volume = self.config.DEFAULT_VOICE_VOLUME
        self.music_queue : list[dict[str, Any]] = []
        self.is_searching = False
        self.suppress_queue_stream_on_stop = False
    
    async def on_ready(self):
        self.logger = logging.getLogger("SelfMusicBot")
        self.logger.info(f"Logged in as {self.user}")
        await self.change_presence(activity=discord.activity.Game("music to you"))

        if self.config.OPERATING_GUILD != None and self.config.VOICE_CHANNEL != None:
            guild = self.get_guild(self.config.OPERATING_GUILD)
            if not guild:
                self.logger.warn("Invalid operating guild specified in config!")
                return
            
            channel = guild.get_channel(self.config.VOICE_CHANNEL)
            if not channel or not isinstance(channel, discord.channel.VoiceChannel):
                self.logger.warn("Invalid voice channel specified in config!")
                return
            
            self.voice_channel = channel

    async def on_message(self, message : discord.message.Message):
        if message.author == self.user or message.author.bot or not isinstance(message.channel, discord.channel.TextChannel):
            return

        message_content = message.content
        if message_content.startswith(COMMAND_PREFIX):
            content_parsed = message_content.split(" ")
            cmd = content_parsed[0].removeprefix(COMMAND_PREFIX)
            cmd_args = content_parsed[1:]
            await self.on_command(message, message.channel, message.guild, cmd, cmd_args)

    async def on_command(self, 
                         message : discord.message.Message, 
                         channel : discord.channel.TextChannel, 
                         guild : discord.guild.Guild, 
                         cmd : str, 
                         args : list[str]):
        cmd_handler : CommandHandler = REGISTERED_CMDS.get(cmd)
        self.logger.info(f"Received command \"{cmd}\" ({','.join(args)}) from {message.author}")

        if cmd_handler:
            self.logger.info(f"Executing handler for commnad \"{cmd}\"...")

            if self.is_banned(message.author) and not self.is_administrator(message.author):
                self.logger.warn(f"Banned user ({message.author}) attempted to execute a command!")
                return

            if cmd_handler.needs_join_voice_channel:
                if not self.get_voice_client():
                    await message.reply(":x: I haven't joined the voice channel!")
                    return

            if cmd_handler.needs_same_guild:
                if guild.id != self.voice_channel.guild.id:
                    await message.reply(":x: The current guild doesn't match the guild of the voice channel")
                    return

            if cmd_handler.needs_listening_executor:
                if not message.author.voice or message.author.voice.channel.id != self.voice_channel.id:
                    await message.reply(":x: You must be listening in my voice channel to execute that command!")
                    return

            if cmd_handler.needs_admin:
                if not self.is_administrator(message.author):
                    await message.reply(":x: You must be an administrator to execute that command! (defined in the config)")
                    return

            await cmd_handler.func(self, message, channel, guild, args)
        else:
            self.logger.warn(f"\"{cmd}\" is not a valid command!")
            await message.reply(":x: Invalid command!")

    async def stream_data_voice_channel(self, data, callback):
        if not self.get_voice_client():
            self.logger.warn("Attempted to stream, but not in the voice channel")
            await callback("Not in a voice channel")
            return
        
        try:
            audio_source = await YoutubeAudioSource.get_from_data(data, self.voice_volume)
        except Exception as ex:
            await callback(str(ex))
            return
        
        self.get_voice_client().stop()
        self.get_voice_client().play(audio_source, after=lambda e:
                                     asyncio.run_coroutine_threadsafe(self.on_stream_end(e), self.loop))
        audio_source.start_time = int(time())

        self.logger.info(f"Now streaming audio from \"{audio_source.data['url']}\"" + 
                         f" (start time: {audio_source.start_time}, duration: {audio_source.data['duration']})")
        await callback(None)

    async def leave_voice_channel(self):
        if self._voice_client:
            self.logger.info(f"Leaving voice channel...")
            await self._voice_client.disconnect()
        self._voice_client = None

    def get_voice_client(self) -> (discord.voice_client.VoiceClient | None):
        if self._voice_client and not self._voice_client.is_connected():
            self._voice_client = None
        return self._voice_client
    
    def is_banned(self, user : discord.Member):
        if user.id in self.config.BANNED_USERS:
            return True
        
        for role in user.roles:
            if role.id in self.config.BANNED_ROLES:
                return True

        return False

    def is_administrator(self, user : discord.Member):
        if user.id in self.config.ADMIN_USERS:
            return True
        
        for role in user.roles:
            if role.id in self.config.ADMIN_ROLES:
                return True
            
        return False
    
    async def stream_next_queue_item(self):
        self.logger.info("Getting next item from queue...")

        if (len(self.music_queue) > 0):
            async def stream_callback(error_msg): pass
            audio_data = self.music_queue.pop(0)
            await self.stream_data_voice_channel(audio_data, stream_callback)
        else:
            self.logger.info("Nothing to stream from the queue")

    async def on_stream_end(self, error):
        self.logger.info("Streaming ended")

        if error: 
            self.logger.error(f"Streaming error: {error}")

        if not self.suppress_queue_stream_on_stop:
            if self.get_voice_client(): 
                self._voice_client.stop()

            if self.get_voice_client(): 
                await self.stream_next_queue_item()
        else:
            self.logger.info("Streaming next item from the queue has been suppressed")
            self.suppress_queue_stream_on_stop = False