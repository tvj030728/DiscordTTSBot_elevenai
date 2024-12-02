# Configuration Constants
VOICE_ID = "Eleven API voice ID"
TARGET_CHANNEL_ID = "Your Chatting Channel ID"
DISCORD_TOKEN = "Discord Bot Token"

ELEVEN_API_KEYS = [
    "Eleven API KEY",
    # API KEYS
]
ELEVEN_MODEL = "eleven_multilingual_v2"


# Imports
import discord
from discord.ext import commands
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import asyncio
import io
from collections import deque
from typing import Dict
import random
import time

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ElevenLabs 클라이언트 풀 생성
eleven_clients = [ElevenLabs(api_key=key) for key in ELEVEN_API_KEYS]

class QueueItem:
    def __init__(self, text: str):
        self.text = text
        self.audio = None

class VoiceState:
    def __init__(self):
        self.voice_client = None
        self.queue = deque()
        self.is_playing = False
        self.messages_to_delete = []
        self.last_activity = time.time()  # Track the last activity time

voice_states: Dict[int, VoiceState] = {}

async def prepare_audio(text: str) -> io.BytesIO:
    try:
        # 랜덤하게 클라이언트 선택
        eleven = random.choice(eleven_clients)
        
        audio_stream = eleven.generate(
            text=text,
            voice=VOICE_ID,
            model=ELEVEN_MODEL,
            stream=True
        )
        
        audio_bytes = b''
        for chunk in audio_stream:
            audio_bytes += chunk
        
        return io.BytesIO(audio_bytes)
    except Exception as e:
        print(f"Error preparing audio: {e}")
        return None

async def play_next(guild_id: int):
    if not voice_states[guild_id].queue:
        voice_states[guild_id].is_playing = False
        return

    state = voice_states[guild_id]
    
    try:
        # 대기열에서 다음 항목 가져오기
        queue_item = state.queue.popleft()
        
        if queue_item.audio:
            # 음성 재생
            state.voice_client.play(
                discord.FFmpegPCMAudio(queue_item.audio, pipe=True),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(guild_id), bot.loop
                )
            )
    except Exception as e:
        print(f"Error in play_next: {e}")
        state.is_playing = False

async def check_inactivity():
    while True:
        for guild_id, state in voice_states.items():
            if state.voice_client and not state.is_playing:
                # Check if 5 minutes have passed since the last activity
                if time.time() - state.last_activity > 300:  # 300 seconds = 5 minutes
                    await disconnect_voice_client(guild_id)
        await asyncio.sleep(60)  # Check every minute

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    bot.loop.create_task(check_inactivity())  # Start the inactivity check task
    await update_bot_status()  # Update the bot's status on startup

async def update_bot_status():
    # Check if the bot is connected to any voice channel
    is_connected = any(state.voice_client for state in voice_states.values())
    if is_connected:
        await bot.change_presence(status=discord.Status.online)
    else:
        await bot.change_presence(status=discord.Status.offline)

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = member.guild.voice_client
    if voice_client:
        voice_channel = voice_client.channel
        # Count non-bot members in the voice channel
        members = len([m for m in voice_channel.members if not m.bot])
        
        if members == 0:
            guild_id = member.guild.id
            if guild_id in voice_states:
                # Clear the queue and reset the state
                state = voice_states[guild_id]
                state.queue.clear()
                state.is_playing = False
                state.voice_client = None
            
            await voice_client.disconnect()
    
    await update_bot_status()  # Update the bot's status after voice state changes

@bot.event
async def on_message(message):
    if message.channel.id == TARGET_CHANNEL_ID:
        # Update last activity time
        guild_id = message.guild.id
        if guild_id in voice_states:
            voice_states[guild_id].last_activity = time.time()

        # 봇 메시지는 무시
        if message.author == bot.user:
            return
            
        if not message.author.voice:
            # 음성 채널 참여 요청 메시지 보내기
            reply = await message.reply("음성 대화방에 참여해주세요!")
            
            # 1초 후 사용자의 메시지와 봇의 답장 삭제
            await asyncio.sleep(1)
            try:
                await message.delete()
                await reply.delete()
            except Exception as e:
                print(f"Failed to delete messages: {e}")
            return
            
        if guild_id not in voice_states:
            voice_states[guild_id] = VoiceState()
        
        state = voice_states[guild_id]
        
        try:
            user_voice_channel = message.author.voice.channel
            if not state.voice_client or state.voice_client.channel != user_voice_channel:
                if state.voice_client:
                    await state.voice_client.disconnect()
                
                state.voice_client = await user_voice_channel.connect()
                
                # 봇이 접속할 때 채팅창의 모든 메시지 삭제
                target_channel = bot.get_channel(TARGET_CHANNEL_ID)
                try:
                    await target_channel.purge(limit=None)
                except Exception as e:
                    print(f"Failed to purge messages: {e}")
                
            queue_item = QueueItem(message.content)
            queue_item.audio = await prepare_audio(message.content)
            
            state.queue.append(queue_item)
            
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except Exception as e:
                print(f"Failed to delete message: {e}")
            
            if not state.is_playing:
                state.is_playing = True
                await play_next(guild_id)
            
        except Exception as e:
            print(f"Error occurred: {e}")
            if message.guild.voice_client:
                await message.guild.voice_client.disconnect()
                state.voice_client = None
                state.is_playing = False
                state.queue.clear()

    await bot.process_commands(message)
    await update_bot_status()  # Update the bot's status after processing messages

async def disconnect_voice_client(guild_id):
    state = voice_states.get(guild_id)
    if state and state.voice_client:
        await state.voice_client.disconnect()
        state.voice_client = None
        state.is_playing = False
        state.queue.clear()
        
        # Delete all messages that were not deleted
        for msg in state.messages_to_delete:
            try:
                await msg.delete()
            except discord.NotFound:
                pass
            except Exception as e:
                print(f"Failed to delete message: {e}")
        state.messages_to_delete.clear()

# Example command to disconnect the bot
@bot.command()
async def leave(ctx):
    await disconnect_voice_client(ctx.guild.id)

# Run the bot
bot.run(DISCORD_TOKEN)

