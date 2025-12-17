import logging
from typing import Callable, Optional
from src.display.base_display import BaseDisplay

class ServiceDisplay(BaseDisplay):
    """
    服务模式显示类 - 仅在控制台输出日志，无交互界面
    """
    def __init__(self):
        super().__init__()
        # 使用专门的 logger，或者复用父类的 self.logger
        # 父类 BaseDisplay 已经初始化了 self.logger = get_logger(self.__class__.__name__)
        pass

    async def set_callbacks(
        self,
        press_callback: Optional[Callable] = None,
        release_callback: Optional[Callable] = None,
        mode_callback: Optional[Callable] = None,
        auto_callback: Optional[Callable] = None,
        abort_callback: Optional[Callable] = None,
        send_text_callback: Optional[Callable] = None,
    ):
        """
        设置回调函数 - 服务模式不需要交互回调
        """
        pass

    async def update_button_status(self, text: str):
        """
        更新按钮状态
        """
        self.logger.info(f"[Button] {text}")

    async def update_status(self, status: str, connected: bool):
        """
        更新状态
        """
        conn_str = "Connected" if connected else "Disconnected"
        self.logger.info(f"[Status] {status} ({conn_str})")

    async def update_text(self, text: str):
        """
        更新文本
        """
        if text and text.strip():
            self.logger.info(f"[Text] {text.strip()}")

    async def update_emotion(self, emotion_name: str):
        """
        更新表情
        """
        self.logger.info(f"[Emotion] {emotion_name}")

    async def start(self):
        """
        启动显示
        """
        self.logger.info("Service Display Started - Running in headless mode")
