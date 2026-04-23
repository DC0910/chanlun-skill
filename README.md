# 缠论股票分析 OpenClaw Skill

基于缠论理论的股票分析 OpenClaw Skill，提供缠论位置分析、历史回测、走势预测等功能。

## 功能特性

- **位置分析**：分析股票当前在缠论中的位置（中枢、买卖点等）
- **历史回测**：基于缠论买卖点进行历史数据回测
- **走势预测**：结合缠论理论预测股票未来走势
- **可视化展示**：生成K线图、中枢、买卖点等可视化图表

## 安装

### 前置要求

- Python >= 3.8
- OpenClaw 平台

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/chanlun/chanlun-stock-analysis.git
cd chanlun-stock-analysis
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 安装Skill
```bash
pip install -e .
```

### 配置

1. 复制配置文件模板
```bash
cp chanlun-stock-analysis/skill/config.yaml chanlun-stock-analysis/skill/config.yaml.local
```

2. 修改配置文件，填入Tushare Token（如果使用Tushare数据源）
```yaml
data_source:
  tushare:
    token: "your_tushare_token"
```

## 使用方法

### 在OpenClaw中使用

安装后，Skill会自动注册到OpenClaw平台。您可以通过以下方式使用：

#### 1. 位置分析

```
分析 000001 缠论位置
```

或

```
分析平安银行最近的缠论结构
```

#### 2. 历史回测

```
回测 000001 2023-01-01 2023-12-31
```

或

```
回测平安银行2023年的缠论策略
```

#### 3. 走势预测

```
预测 000001 走势
```

或

```
预测平安银行未来一周走势
```

### 编程方式使用

```python
from chanlun_stock_analysis import ChanLunSkill
import asyncio

# 创建Skill实例
skill = ChanLunSkill()

# 查看Skill信息
print(skill.info())

# 执行分析
async def analyze():
    context = {"command": "分析 000001 缠论位置"}
    result = await skill.execute(context)
    print(result)

asyncio.run(analyze())
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

## 项目结构

```
缠论/
├── SKILL.md                    # OpenClaw Skill配置文件
├── setup.py                    # 安装配置
├── requirements.txt            # 依赖列表
├── README.md                   # 项目说明
├── chanlun_stock_analysis/     # Skill主包
│   ├── __init__.py            # 包初始化
│   └── skill.py               # OpenClaw接口实现
├── chanlun-stock-analysis/     # 核心分析模块
│   ├── skill/                 # Skill核心代码
│   │   ├── main.py           # 主逻辑
│   │   ├── models.py         # 数据模型
│   │   ├── config.py         # 配置管理
│   │   ├── parsers/          # 命令解析
│   │   ├── analyzers/        # 分析引擎
│   │   ├── detectors/        # 缠论检测
│   │   ├── formatters/       # 结果格式化
│   │   ├── renderers/        # 可视化渲染
│   │   └── utils/            # 工具函数
│   └── tests/                # 测试代码
└── chanlun/                   # 缠论核心库
```

## 开发

### 运行测试

```bash
pytest chanlun-stock-analysis/tests/
```

### 代码规范

- 遵循 PEP8 代码规范
- 使用类型注解
- 编写文档字符串

## 注意事项

1. 本Skill仅供研究和学习使用，不构成投资建议
2. 缠论分析需要一定的理论基础，建议先了解缠论基本概念
3. 数据来源于第三方，请关注数据质量和时效性
4. 预测结果仅供参考，市场有风险，投资需谨慎

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。

## 联系方式

- Email: chanlun@example.com
- GitHub: https://github.com/chanlun/chanlun-stock-analysis
