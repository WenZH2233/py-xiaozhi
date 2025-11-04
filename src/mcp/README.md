# MCP 服务器实现文档

## 📋 概述

本目录实现了基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2024-11-05) 的服务器端功能，为 AI 语音助手提供了丰富的工具调用能力。MCP 是一个标准化的协议，用于 AI 模型与外部工具/服务的交互。

### 核心组件

- **`mcp_server.py`**: MCP 服务器核心实现，负责消息解析、工具管理和协议通信
- **`tools/`**: 工具模块目录，包含各类功能工具的实现

## 🏗️ 架构设计

### 1. 核心类

#### `McpServer` - 服务器主类
- 单例模式设计
- 负责工具注册、消息路由和协议处理
- 支持 JSONRPC 2.0 协议

#### `McpTool` - 工具定义类
- 封装工具的名称、描述、参数和回调函数
- 自动处理参数验证和类型转换
- 支持同步和异步回调函数

#### `PropertyList` & `Property` - 参数定义类
- 定义工具的输入参数
- 支持类型验证（Boolean、Integer、String）
- 支持默认值和范围限制

### 2. 工具模块

当前已实现的工具模块：

| 模块 | 路径 | 功能描述 |
|------|------|----------|
| **系统工具** | `tools/system/` | 设备状态查询、音量控制、应用管理（启动/关闭/扫描） |
| **日程管理** | `tools/calendar/` | 创建/查询/更新/删除日程事件，支持提醒和分类 |
| **倒计时器** | `tools/timer/` | 创建/取消倒计时，查询活动计时器 |
| **音乐播放** | `tools/music/` | 搜索播放、播放控制、歌词获取、列表管理 |
| **摄像头** | `tools/camera/` | 拍照、图像识别、OCR、问答、二维码识别 |
| **截图** | `tools/screenshot/` | 桌面截图、屏幕分析、界面识别 |
| **八字命理** | `tools/bazi/` | 八字计算、命理分析、婚配分析 |

## 🚀 如何新增 MCP 工具

### 方式一：创建独立工具模块（推荐）

适用于功能复杂、需要多个工具的场景。

#### 步骤 1: 创建工具目录结构

```
voice_rec/mcp/tools/
└── your_module/          # 你的模块名称
    ├── __init__.py       # 模块导出
    ├── manager.py        # 工具管理器
    ├── tools.py          # 工具实现函数
    └── models.py         # 数据模型（可选）
```

#### 步骤 2: 实现工具函数 (`tools.py`)

```python
"""你的工具模块实现."""

from typing import Dict, Any
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def your_tool_function(args: Dict[str, Any]) -> str:
    """
    工具函数实现.
    
    Args:
        args: 参数字典，包含用户传入的参数
        
    Returns:
        str: 工具执行结果（字符串形式）
    """
    try:
        # 1. 提取参数
        param1 = args.get("param1")
        param2 = args.get("param2", "default_value")  # 带默认值
        
        # 2. 执行业务逻辑
        result = f"处理结果: {param1}, {param2}"
        
        # 3. 返回结果
        logger.info(f"工具执行成功: {result}")
        return result
        
    except Exception as e:
        logger.error(f"工具执行失败: {e}", exc_info=True)
        raise
```

#### 步骤 3: 创建管理器 (`manager.py`)

```python
"""你的工具管理器."""

from src.utils.logging_config import get_logger
from .tools import your_tool_function

logger = get_logger(__name__)

class YourToolsManager:
    """工具管理器类."""
    
    def __init__(self):
        self._initialized = False
        logger.info("[YourManager] 工具管理器初始化")
    
    def init_tools(self, add_tool, PropertyList, Property, PropertyType):
        """
        注册工具到 MCP 服务器.
        
        Args:
            add_tool: MCP 服务器的工具注册函数
            PropertyList: 属性列表类
            Property: 属性类
            PropertyType: 属性类型枚举
        """
        try:
            logger.info("[YourManager] 开始注册工具")
            
            # 定义工具参数
            tool_props = PropertyList([
                Property("param1", PropertyType.STRING),  # 必需参数
                Property("param2", PropertyType.INTEGER, default_value=10),  # 可选参数
                Property("param3", PropertyType.BOOLEAN, default_value=False),
            ])
            
            # 注册工具
            add_tool(
                (
                    "your.tool.name",  # 工具名称（唯一标识）
                    (
                        "工具描述信息（中文）\n"
                        "Use this tool when:\n"
                        "1. User wants to do something\n"
                        "2. Another use case\n"
                        "\nArgs:\n"
                        "  param1: 参数1说明（必需）\n"
                        "  param2: 参数2说明（可选，默认10）\n"
                        "  param3: 参数3说明（可选，默认False）"
                    ),
                    tool_props,
                    your_tool_function,  # 回调函数
                )
            )
            
            self._initialized = True
            logger.info("[YourManager] 工具注册完成")
            
        except Exception as e:
            logger.error(f"[YourManager] 工具注册失败: {e}", exc_info=True)
            raise

# 单例模式
_manager_instance = None

def get_your_manager():
    """获取管理器单例实例."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = YourToolsManager()
    return _manager_instance
```

#### 步骤 4: 配置模块导出 (`__init__.py`)

```python
"""你的工具模块."""

from .manager import YourToolsManager, get_your_manager

__all__ = ["YourToolsManager", "get_your_manager"]
```

#### 步骤 5: 在 MCP 服务器中注册

编辑 `mcp_server.py` 的 `add_common_tools()` 方法，添加你的工具：

```python
def add_common_tools(self):
    """添加通用工具."""
    # ... 现有代码 ...
    
    # 添加你的工具模块
    from src.mcp.tools.your_module import get_your_manager
    
    your_manager = get_your_manager()
    your_manager.init_tools(self.add_tool, PropertyList, Property, PropertyType)
    
    # ... 其他工具 ...
```

### 方式二：直接添加简单工具

适用于功能简单、独立的单个工具。

```python
# 在 mcp_server.py 的 add_common_tools() 中直接添加

def simple_tool_callback(args: Dict[str, Any]) -> str:
    """简单工具回调."""
    param = args.get("param")
    return f"结果: {param}"

# 注册工具
properties = PropertyList([
    Property("param", PropertyType.STRING)
])

self.add_tool(
    McpTool(
        "simple.tool",
        "简单工具描述",
        properties,
        simple_tool_callback,
    )
)
```

## 📝 参数类型说明

### PropertyType 枚举

| 类型 | 说明 | Python 类型 | 示例 |
|------|------|-------------|------|
| `PropertyType.BOOLEAN` | 布尔值 | `bool` | `True`, `False` |
| `PropertyType.INTEGER` | 整数 | `int` | `10`, `-5`, `100` |
| `PropertyType.STRING` | 字符串 | `str` | `"hello"`, `"2024-01-01"` |

### 参数定义示例

```python
# 必需的字符串参数
Property("name", PropertyType.STRING)

# 可选参数（带默认值）
Property("count", PropertyType.INTEGER, default_value=5)

# 带范围限制的整数
Property("volume", PropertyType.INTEGER, min_value=0, max_value=100)

# 布尔参数
Property("enabled", PropertyType.BOOLEAN, default_value=True)
```

## 🔧 高级特性

### 1. 异步工具支持

工具回调函数可以是异步函数：

```python
async def async_tool_function(args: Dict[str, Any]) -> str:
    """异步工具函数."""
    result = await some_async_operation()
    return result
```

### 2. 工具链调用

工具可以内部调用其他工具或服务：

```python
def complex_tool(args: Dict[str, Any]) -> str:
    """复杂工具示例."""
    # 调用其他服务
    from src.mcp.tools.calendar import get_calendar_manager
    calendar = get_calendar_manager()
    
    # 执行复杂逻辑
    events = calendar.get_upcoming_events()
    return f"找到 {len(events)} 个事件"
```

### 3. Vision 能力集成

通过 `capabilities.vision` 参数可以配置图像识别服务：

```python
# MCP 初始化时会自动解析 vision 配置
capabilities = {
    "vision": {
        "url": "http://your-vision-service.com/api",
        "token": "your-auth-token"
    }
}
```

## 📊 MCP 协议消息示例

### 初始化请求

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "vision": {
        "url": "http://localhost:8000/explain",
        "token": "secret-token"
      }
    }
  }
}
```

### 工具列表请求

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {
    "cursor": ""
  }
}
```

### 工具调用请求

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "self.calendar.create_event",
    "arguments": {
      "title": "团队会议",
      "start_time": "2024-01-15T14:00:00",
      "description": "讨论项目进度",
      "category": "工作"
    }
  }
}
```

## 🐛 调试建议

### 1. 日志输出

使用统一的日志系统：

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("信息日志")
logger.warning("警告日志")
logger.error("错误日志", exc_info=True)  # 包含堆栈信息
```

### 2. 参数验证

确保在工具函数中验证参数：

```python
def your_tool(args: Dict[str, Any]) -> str:
    param = args.get("param")
    if not param:
        raise ValueError("参数 param 不能为空")
    
    if not isinstance(param, str):
        raise TypeError("参数 param 必须是字符串")
    
    # 继续处理...
```

### 3. 错误处理

使用 try-except 捕获异常：

```python
def your_tool(args: Dict[str, Any]) -> str:
    try:
        # 业务逻辑
        result = do_something()
        return result
    except SpecificError as e:
        logger.error(f"特定错误: {e}")
        raise
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        raise
```

## 📚 最佳实践

### 1. 工具命名规范

- 使用点分命名：`category.action` 或 `self.module.action`
- 例如：`self.calendar.create_event`, `self.audio_speaker.set_volume`

### 2. 描述编写规范

- **中英文双语**：支持多语言用户
- **明确使用场景**：说明何时应该调用此工具
- **详细参数说明**：列出每个参数的含义和要求

### 3. 错误处理规范

- 所有工具函数都应该有异常处理
- 记录详细的错误日志
- 向用户返回友好的错误信息

### 4. 性能优化

- 避免在工具函数中执行耗时操作
- 使用异步函数处理 I/O 密集型任务
- 合理使用缓存减少重复计算

### 5. 测试建议

- 为每个工具编写单元测试
- 测试边界条件和异常情况
- 验证参数类型和范围限制

## 🔗 参考资料

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io/specification/2024-11-05)
- [JSONRPC 2.0 规范](https://www.jsonrpc.org/specification)
- 项目内其他工具模块实现（参考 `tools/` 目录下的现有模块）

## 📞 常见问题

### Q: 工具名称冲突怎么办？

A: 使用命名空间前缀，如 `self.module.action` 格式，确保唯一性。

### Q: 如何支持可选参数？

A: 在 Property 定义中使用 `default_value` 参数。

### Q: 工具返回值只能是字符串吗？

A: 可以返回 `bool`、`int` 或 `str`，服务器会自动转换为字符串。

### Q: 如何访问应用的其他服务？

A: 通过导入相应的管理器或服务类，例如 `from src.mcp.tools.calendar import get_calendar_manager`。

---

**最后更新**: 2025年11月4日  
**维护者**: Orangepi-Util 开发团队
