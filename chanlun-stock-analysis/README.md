# 缠论股票分析 Skill

基于缠论理论的股票分析 OpenClaw Skill，提供缠论位置分析、历史回测、走势预测等功能。

## 功能特性

- **位置分析**：分析股票当前在缠论中的位置（中枢、买卖点等）
- **历史回测**：基于缠论买卖点进行历史数据回测
- **走势预测**：结合缠论理论预测股票未来走势
- **可视化展示**：生成K线图、中枢、买卖点等可视化图表

## 安装

### 从源码安装

```bash
cd chanlun-stock-analysis
pip install -r requirements.txt
pip install -e .
```

### 配置

1. 复制配置文件模板
```bash
cp skill/config.yaml skill/config.yaml.local
```

2. 修改配置文件，填入Tushare Token（如果使用Tushare数据源）
```yaml
data_source:
  tushare:
    token: "your_tushare_token"
```

## 快速开始

### 1. 位置分析

分析股票当前在缠论中的位置：

```python
from openclaw_sdk import SkillContext
from skill.main import ChanLunStockAnalysisSkill

skill = ChanLunStockAnalysisSkill()
context = SkillContext(
    command="分析 000001 缠论位置"
)
result = await skill.execute(context)
print(result)
```

### 2. 历史回测

回测股票历史数据：

```python
context = SkillContext(
    command="回测 000001 2023-01-01 2023-12-31"
)
result = await skill.execute(context)
print(result)
```

### 3. 走势预测

预测股票未来走势：

```python
context = SkillContext(
    command="预测 000001 走势"
)
result = await skill.execute(context)
print(result)
```

## 缠论概念说明

### 分型
- **顶分型**：相邻三根K线中，中间K线的高点和低点都是最高的
- **底分型**：相邻三根K线中，中间K线的高点和低点都是最低的

### 笔
连接相邻顶底分型的线段，是缠论分析的基本单位。

### 线段
由至少3笔组成，代表更高级别的走势。

### 中枢
由至少3段连续的线段重叠区域构成，是缠论的核心概念。

### 买卖点
- **第一类买点**：走势离开中枢后出现背驰，形成买点
- **第二类买点**：回拉不破中枢形成的买点
- **第三类买点**：新中枢形成后的回拉买点
- **卖点**：与买点对称

## 配置说明

详细配置说明请参考 `skill/config.yaml` 文件。

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码规范

- 遵循 PEP8 代码规范
- 使用类型注解
- 编写文档字符串

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

## 联系方式

- Email: chanlun@example.com
- GitHub: https://github.com/chanlun/chanlun-stock-analysis
