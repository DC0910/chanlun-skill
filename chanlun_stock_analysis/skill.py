"""
OpenClaw Skill 主类实现

符合OpenClaw Skill开发规范的缠论股票分析Skill。
"""
import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "chanlun-stock-analysis"))

from skill.main import ChanLunStockAnalysisSkill


class ChanLunSkill:
    """
    OpenClaw Skill 标准接口
    
    这是OpenClaw平台调用的入口类，封装了缠论股票分析功能。
    """
    
    def __init__(self):
        """初始化Skill"""
        self._skill = ChanLunStockAnalysisSkill()
        self._metadata = self._get_metadata()
    
    def _get_metadata(self) -> Dict[str, Any]:
        """获取Skill元数据"""
        return {
            "name": "chanlun-stock-analysis",
            "version": "1.0.0",
            "description": "基于缠论理论的股票分析Skill，提供分型识别、笔线段划分、中枢识别、买卖点判断、历史回测和走势预测功能",
            "author": "ChanLun Team",
            "license": "MIT",
            "homepage": "https://github.com/chanlun/chanlun-stock-analysis",
            "keywords": ["缠论", "股票分析", "量化交易", "技术分析", "买卖点识别"],
            "commands": [
                {
                    "name": "analyze",
                    "description": "分析指定股票的缠论结构",
                    "parameters": {
                        "stock_code": {
                            "type": "string",
                            "required": True,
                            "description": "股票代码，如 '000001.SZ'"
                        },
                        "start_date": {
                            "type": "string",
                            "required": False,
                            "description": "开始日期，格式 'YYYY-MM-DD'"
                        },
                        "end_date": {
                            "type": "string",
                            "required": False,
                            "description": "结束日期，格式 'YYYY-MM-DD'"
                        },
                        "level": {
                            "type": "string",
                            "required": False,
                            "default": "day",
                            "description": "分析级别，可选 'day', 'hour', '30min', '5min'"
                        }
                    }
                },
                {
                    "name": "backtest",
                    "description": "对指定股票进行历史回测",
                    "parameters": {
                        "stock_code": {
                            "type": "string",
                            "required": True,
                            "description": "股票代码"
                        },
                        "start_date": {
                            "type": "string",
                            "required": True,
                            "description": "回测开始日期"
                        },
                        "end_date": {
                            "type": "string",
                            "required": True,
                            "description": "回测结束日期"
                        },
                        "initial_capital": {
                            "type": "number",
                            "required": False,
                            "default": 100000,
                            "description": "初始资金"
                        }
                    }
                },
                {
                    "name": "predict",
                    "description": "基于缠论理论预测未来走势",
                    "parameters": {
                        "stock_code": {
                            "type": "string",
                            "required": True,
                            "description": "股票代码"
                        },
                        "horizon": {
                            "type": "number",
                            "required": False,
                            "default": 5,
                            "description": "预测时间范围（天）"
                        }
                    }
                },
                {
                    "name": "signals",
                    "description": "查询指定股票的买卖点信号",
                    "parameters": {
                        "stock_code": {
                            "type": "string",
                            "required": True,
                            "description": "股票代码"
                        },
                        "signal_type": {
                            "type": "string",
                            "required": False,
                            "default": "all",
                            "description": "信号类型，可选 'buy1', 'buy2', 'buy3', 'sell1', 'sell2', 'sell3', 'all'"
                        }
                    }
                }
            ],
            "permissions": [
                {
                    "name": "network",
                    "description": "允许访问网络获取股票数据"
                },
                {
                    "name": "filesystem",
                    "description": "允许读写本地缓存和配置文件",
                    "scope": ["./data/", "./cache/", "./config/"]
                }
            ]
        }
    
    @classmethod
    def info(cls) -> Dict[str, Any]:
        """
        返回Skill信息（OpenClaw标准接口）
        
        Returns:
            Skill元数据字典
        """
        return cls()._get_metadata()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Skill（OpenClaw标准接口）
        
        Args:
            context: 执行上下文，包含以下字段：
                - command: str, 用户输入的命令
                - params: dict, 解析后的参数（可选）
                - config: dict, 配置信息（可选）
        
        Returns:
            执行结果字典，包含以下字段：
                - success: bool, 是否成功
                - message: str, 结果消息
                - data: dict, 结果数据
                - error: str, 错误信息（如果失败）
        """
        try:
            # 调用内部skill执行
            result = await self._skill.execute(context)
            
            # 转换为标准格式
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "error": None if result.success else result.message
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"执行失败: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """
        验证输入（OpenClaw标准接口）
        
        Args:
            context: 执行上下文
        
        Returns:
            是否有效
        """
        return await self._skill.validate(context)
    
    def help(self) -> str:
        """
        获取帮助信息（OpenClaw标准接口）
        
        Returns:
            帮助文本
        """
        return self._skill.get_help()
    
    def get_commands(self) -> List[Dict[str, Any]]:
        """
        获取支持的命令列表
        
        Returns:
            命令列表
        """
        return self._metadata["commands"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取完整元数据
        
        Returns:
            元数据字典
        """
        return self._metadata


# OpenClaw Skill 工厂函数
def create_skill() -> ChanLunSkill:
    """
    创建Skill实例（OpenClaw标准入口）
    
    Returns:
        Skill实例
    """
    return ChanLunSkill()


# 用于直接运行的测试
if __name__ == "__main__":
    import asyncio
    
    async def test():
        skill = create_skill()
        print("Skill Info:")
        print(skill.info())
        
        print("\nHelp:")
        print(skill.help())
        
        print("\nTest Execute:")
        context = {"command": "分析 000001 缠论位置"}
        result = await skill.execute(context)
        print(result)
    
    asyncio.run(test())
