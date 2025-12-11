import asyncio
import sys
import wave
import os
import numpy as np
import sounddevice as sd
from src.utils.config_manager import ConfigManager
from src.constants.constants import AudioConfig
from src.audio_codecs.audio_codec import AudioCodec, AudioListener

class TestListener:
    def __init__(self):
        self.audio_data = []

    def on_audio_data(self, audio_data: np.ndarray) -> None:
        max_val = np.max(np.abs(audio_data))
        if max_val == 0:
             print("收到静音帧")
             pass
        print(f"收到音频数据帧: 长度={len(audio_data)}, 最大值={max_val}")
        self.audio_data.append(audio_data)

class HardwareTester:
    def __init__(self):
        self.config = ConfigManager.get_instance()
        self.codec = AudioCodec()

    async def run_mic_test(self):
        print("开始麦克风测试...")
        print("正在初始化音频设备...")
        try:
            await self.codec.initialize()
        except Exception as e:
            print(f"初始化失败: {e}")
            return
        
        listener = TestListener()
        self.codec.add_audio_listener(listener)
        
        print(f"正在使用输入设备: {self.codec.mic_device_id} (采样率: {self.codec.device_input_sample_rate})")
        print("请说话... (按回车键停止录音)")
        
        # Wait for enter
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, sys.stdin.readline)
        
        print("停止录音...")
        # Store device ID before closing
        output_device = self.codec.speaker_device_id
        await self.codec.close()
        
        print(f"录制到的数据帧数: {len(listener.audio_data)}")
        # Concatenate data
        if not listener.audio_data:
            print("未录制到音频数据！")
            return

        recorded_audio = np.concatenate(listener.audio_data)
        duration = len(recorded_audio) / AudioConfig.INPUT_SAMPLE_RATE
        print(f"录制了 {duration:.2f} 秒音频")
        
        output_filename = "mic_test_output.wav"
        print(f"正在保存音频到文件: {output_filename} ...")
        
        try:
            with wave.open(output_filename, 'wb') as wf:
                wf.setnchannels(1) # 单声道
                wf.setsampwidth(2) # 16-bit = 2 bytes
                wf.setframerate(AudioConfig.INPUT_SAMPLE_RATE)
                wf.writeframes(recorded_audio.tobytes())
            print(f"音频已保存: {os.path.abspath(output_filename)}")
        except Exception as e:
            print(f"保存音频文件失败: {e}")

    async def run_speaker_test(self):
        print("开始扬声器测试...")
        
        # Initialize codec to get device info
        try:
            await self.codec._load_device_config()
            device_id = self.codec.speaker_device_id
            sample_rate = self.codec.device_output_sample_rate
            print(f"使用输出设备: {device_id}, 采样率: {sample_rate}")
            
            # Generate "di di di" sound
            # 1kHz sine wave, 3 beeps
            fs = int(sample_rate)
            duration = 0.2
            t = np.linspace(0, duration, int(fs * duration), False)
            tone = np.sin(2 * np.pi * 1000 * t) * 0.5 # 0.5 amplitude
            silence = np.zeros(int(fs * 0.1))
            
            audio = np.concatenate([tone, silence, tone, silence, tone])
            audio = (audio * 32767).astype(np.int16)
            
            print("播放 '嘀嘀嘀'...")
            
            sd.play(audio, samplerate=fs, device=device_id, blocking=True)
            print("播放结束")
        except Exception as e:
            print(f"播放失败: {e}")

async def run_test(test_name: str):
    tester = HardwareTester()
    if test_name == "mic":
        await tester.run_mic_test()
    elif test_name == "speaker":
        await tester.run_speaker_test()
    else:
        print(f"未知测试项目: {test_name}")
        print("可用测试: mic, speaker")
