import sys as sys
from typing import Union

from loguru._logger import Core, Logger
from nonebot.plugin import PluginMetadata

from .config import Config

config = Config()

logger = Logger(
    core=Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=True,
    raw=False,
    capture=True,
    patcher=None,
    extra={},
)
"""
loguru模块的logger，用于记录日志并保存在log文件中.

支持各种日志级别，和颜色标签<red>,<r>等等.

使用方法:
```
from src.utils.log import logger

>>>logger.info("log message")
>>>logger.success("log message")
>>>logger.debug("log message")
>>>logger.error("log message")
```
"""


class Filter:
    '''过滤器类'''

    def __init__(self) -> None:
        self.level: Union[int, str] = "DEBUG"

    def __call__(self, record):
        module_name: str = record["name"]
        module = sys.modules.get(module_name)
        if module:
            # 判断是否为插件模块
            metadata: PluginMetadata = getattr(module, "__plugin_meta__")
            if metadata:
                record['name'] = metadata.name
            else:
                module_name = getattr(module, "__module_name__", module_name)
                record["name"] = module_name.split(".")[-1]
        levelno = logger.level(self.level).no if isinstance(self.level,
                                                            str) else self.level
        return record["level"].no >= levelno


# 过滤器
default_filter = Filter()

# 是否显示到控制台
if config.logs.get("is_console"):
    console_level = config.logs.get("console_level", "INFO")
    console_format = (
        "<g>{time:MM-DD HH:mm:ss}</g> "
        "[<lvl>{level}</lvl>] "
        "<c><u>{name}</u></c> | "
        "{message}")
    # 添加到控制台
    logger.add(sys.stdout,
               filter=default_filter,
               format=console_format,
               level=console_level
               )

# ===========================添加到日志文件======================================
# 日志文件记录格式
file_format = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "<c><u>{name}</u></c> | "
    "{message}")

# 错误日志文件记录格式
error_format = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "[<c><u>{name}</u></c>] | "
    "<c>{function}:{line}</c>| "
    "{message}")

path_cfg = config.path.get("logs", "logs")

# info文件
if config.logs.get("is_file_info"):
    info_path = f"./{path_cfg}/info/"
    logger.add(
        info_path+"{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="10 days",
        level="INFO",
        format=file_format,
        filter=default_filter,
        encoding="utf-8"
    )

# debug文件
if config.logs.get("is_file_debug"):
    debug_path = f"./{path_cfg}/debug/"
    logger.add(
        debug_path+"{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="10 days",
        level="DEBUG",
        format=file_format,
        filter=default_filter,
        encoding="utf-8"
    )

# error文件
if config.logs.get("is_file_error"):
    error_path = f"./{path_cfg}/error/"
    logger.add(
        error_path+"{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="10 days",
        level="ERROR",
        format=error_format,
        filter=default_filter,
        encoding="utf-8"
    )
