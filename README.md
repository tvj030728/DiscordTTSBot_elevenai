# Discord TTS Bot

A Text-to-Speech (TTS) bot that converts Discord chat messages into voice and plays them in voice channels.

## Key Features

- Converts text messages from designated channels into speech
- High-quality voice synthesis using ElevenLabs API
- Multi-voice queue system
- Automatic voice channel join/leave
- Automatic idle detection and disconnection (after 5 minutes)
- Bot status display (Online/Offline)

## Installation

1. Install required packages:
```bash
pip install discord.py elevenlabs python-dotenv
```
2. Environment Configuration:
   - `DISCORD_TOKEN`: Discord bot token
   - `VOICE_ID`: ElevenLabs voice ID
   - `TARGET_CHANNEL_ID`: Discord channel ID for TTS
   - `ELEVEN_API_KEYS`: List of ElevenLabs API keys

## Usage

1. Run the bot:
```python script1.py```
2. Messages entered in the designated channel will automatically be converted to speech and played.

## Important Notes

- TTS functionality is only available when connected to a voice channel.
- The bot will automatically disconnect after 5 minutes of voice inactivity.
- It is recommended to manage API keys as environment variables for security.

## License

This project is licensed under the MIT License.




# Discord TTS Bot (KO)

Discord 채팅을 음성으로 변환하여 음성 채널에서 재생하는 Text-to-Speech (TTS) 봇입니다.

## 주요 기능

- 지정된 채널의 텍스트 메시지를 음성으로 변환
- ElevenLabs API를 활용한 고품질 음성 합성
- 다중 음성 대기열 시스템
- 자동 음성 채널 참여/퇴장
- 비활성 상태 자동 감지 및 연결 해제 (5분 후)
- 봇 상태 표시 (온라인/오프라인)

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install discord.py elevenlabs python-dotenv
```
2. 환경 설정:
   - `DISCORD_TOKEN`: Discord 봇 토큰
   - `VOICE_ID`: ElevenLabs 음성 ID
   - `TARGET_CHANNEL_ID`: TTS를 적용할 Discord 채널 ID
   - `ELEVEN_API_KEYS`: ElevenLabs API 키 목록

## 사용 방법

1. 봇을 실행합니다:
```python script1.py```
2. 지정된 채널에서 메시지를 입력하면 자동으로 음성으로 변환되어 재생됩니다.

## 주의사항

- 음성 채널에 참여한 상태에서만 TTS 기능을 사용할 수 있습니다.
- 봇이 음성을 재생하지 않는 상태로 5분이 경과하면 자동으로 연결이 해제됩니다.
- API 키는 보안을 위해 환경 변수로 관리하는 것을 권장합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
