import subprocess
import re

def configure_audio_mixer(card_num=3):
    """
    配置音频混音器设置，模拟 test_record.sh 的行为
    """
    commands = [
        f"tinymix -D {card_num} 3 4",   # ALC Capture Max PGA -> 4
        f"tinymix -D {card_num} 4 2",   # ALC Capture Min PGA -> 2
        f"tinymix -D {card_num} 14 192", # Capture Digital Volume -> 192
        f"tinymix -D {card_num} 16 0",  # Left Channel Capture Volume -> 0
        f"tinymix -D {card_num} 17 0",  # Right Channel Capture Volume -> 0
        f"tinymix -D {card_num} 31 1",  # Left PGA Mux -> Line 2L
        f"tinymix -D {card_num} 32 1",  # Right PGA Mux -> Line 2R
        f"tinymix -D {card_num} 33 1",  # Differential Mux -> Line 2
    ]

    print(f"正在配置声卡 {card_num} 的混音器设置...")
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            # print(f"执行成功: {cmd}")
        except subprocess.CalledProcessError as e:
            print(f"执行失败: {cmd}, 错误: {e}")

def get_es8388_card_num():
    try:
        result = subprocess.check_output("aplay -l | grep 'es8388'", shell=True).decode()
        # card 3: rockchipes8388 ...
        match = re.search(r"card (\d+):", result)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 3 # 默认值
