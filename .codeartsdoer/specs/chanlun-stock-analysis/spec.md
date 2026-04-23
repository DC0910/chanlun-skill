# 缠论股票分析 Skill 需求规格文档

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 功能名称 | chanlun-stock-analysis |
| 版本 | v1.0.0 |
| 创建日期 | 2026-04-21 |
| 文档状态 | 待审核 |
| 目标平台 | OpenClaw Skill |

## 2. 项目概述

### 2.1 项目背景
本项目旨在为OpenClaw平台开发一个缠论分析skill，基于已有的缠论量化分析系统（包含分型、笔、线段、中枢等核心组件），提供智能化的股票分析能力。该skill将帮助用户快速识别股票在缠论理论中的位置，进行历史回测，并预测未来走势。

### 2.2 项目目标
开发一个可安装在OpenClaw的skill，实现：
- 基于缠论理论的股票位置识别
- 历史数据回测分析
- 结合缠论理论的走势预测

### 2.3 系统范围

**包含范围：**
- OpenClaw skill接口实现
- 缠论核心分析功能集成
- 买卖点识别与提示
- 历史回测功能
- 走势预测功能
- 用户交互界面

**不包含范围：**
- 实时行情数据采集（依赖外部数据源）
- 自动交易执行
- 多市场支持（仅支持A股）

## 3. 功能需求

### 3.1 缠论位置分析

#### FR-3.1.1 分型识别
**需求描述：** 系统应能够自动识别K线图中的顶分型和底分型。

**验收标准：**
- **When** 输入股票K线数据 **the system shall** 识别出所有顶分型和底分型
- **When** 存在包含关系 **the system shall** 进行包含处理后再识别分型
- **When** 识别到分型 **the system shall** 输出分型类型、位置、价格信息

#### FR-3.1.2 笔的构建
**需求描述：** 系统应能够根据分型构建笔。

**验收标准：**
- **When** 识别出相邻的顶底分型 **the system shall** 判断是否构成一笔
- **When** 分型之间不满足笔的条件 **the system shall** 继续寻找下一个分型
- **When** 构建完成 **the system shall** 输出笔的起止点、方向、长度

#### FR-3.1.3 线段划分
**需求描述：** 系统应能够根据笔划分线段。

**验收标准：**
- **When** 输入笔序列 **the system shall** 识别线段的特征序列
- **When** 特征序列满足条件 **the system shall** 划分线段
- **When** 线段划分完成 **the system shall** 输出线段的起止笔、方向

#### FR-3.1.4 中枢识别
**需求描述：** 系统应能够识别走势中的中枢。

**验收标准：**
- **When** 输入线段序列 **the system shall** 识别至少3段重叠区域
- **When** 重叠区域满足中枢定义 **the system shall** 构建中枢
- **When** 中枢识别完成 **the system shall** 输出中枢区间、级别、延伸段数

#### FR-3.1.5 买卖点识别
**需求描述：** 系统应能够识别缠论定义的买卖点。

**验收标准：**
- **When** 走势离开中枢后发生背驰 **the system shall** 识别第一买卖点
- **When** 第二次回拉不破中枢 **the system shall** 识别第二买卖点
- **When** 新中枢形成后回拉 **the system shall** 识别第三买卖点
- **When** 识别到买卖点 **the system shall** 输出买卖点类型、位置、置信度

### 3.2 历史回测

#### FR-3.2.1 回测配置
**需求描述：** 用户应能够配置回测参数。

**验收标准：**
- **When** 用户设置回测参数 **the system shall** 接受股票代码、时间范围、初始资金等参数
- **When** 参数不合法 **the system shall** 提示错误并拒绝执行
- **When** 参数合法 **the system shall** 保存配置并准备回测

#### FR-3.2.2 回测执行
**需求描述：** 系统应能够执行历史数据回测。

**验收标准：**
- **When** 启动回测 **the system shall** 按时间顺序遍历历史数据
- **When** 遇到买卖点信号 **the system shall** 模拟交易执行
- **When** 回测完成 **the system shall** 计算收益率、胜率、最大回撤等指标

#### FR-3.2.3 回测报告
**需求描述：** 系统应生成详细的回测报告。

**验收标准：**
- **When** 回测结束 **the system shall** 生成包含交易明细的报告
- **When** 生成报告 **the system shall** 包含资金曲线、收益统计、风险指标
- **When** 用户请求 **the system shall** 支持导出报告为PDF或Excel格式

### 3.3 走势预测

#### FR-3.3.1 走势分类
**需求描述：** 系统应能够对当前走势进行分类。

**验收标准：**
- **When** 分析当前走势 **the system shall** 判断是盘整还是趋势
- **When** 是趋势走势 **the system shall** 判断趋势方向和强度
- **When** 是盘整走势 **the system shall** 判断中枢级别和震荡幅度

#### FR-3.3.2 未来走势推演
**需求描述：** 系统应基于缠论理论推演未来可能的走势。

**验收标准：**
- **When** 当前走势明确 **the system shall** 推演未来可能的走势分类
- **When** 存在多种可能 **the system shall** 给出每种可能性的概率评估
- **When** 推演完成 **the system shall** 给出关键观察点和转折信号

#### FR-3.3.3 风险评估
**需求描述：** 系统应评估预测的风险水平。

**验收标准：**
- **When** 给出预测 **the system shall** 评估预测的可靠性
- **When** 走势复杂 **the system shall** 提示风险等级提高
- **When** 关键位置 **the system shall** 提示需要重点关注的价位

### 3.4 OpenClaw Skill接口

#### FR-3.4.1 Skill注册
**需求描述：** skill应能够正确注册到OpenClaw平台。

**验收标准：**
- **When** 安装skill **the system shall** 向OpenClaw注册skill元数据
- **When** 注册成功 **the system shall** 在OpenClaw技能列表中显示
- **When** 用户调用 **the system shall** 响应OpenClaw的调用请求

#### FR-3.4.2 命令处理
**需求描述：** skill应处理用户的自然语言命令。

**验收标准：**
- **When** 用户输入分析命令 **the system shall** 解析股票代码和分析类型
- **When** 用户输入回测命令 **the system shall** 解析回测参数
- **When** 命令不明确 **the system shall** 提示用户补充信息

#### FR-3.4.3 结果展示
**需求描述：** skill应以友好方式展示分析结果。

**验收标准：**
- **When** 分析完成 **the system shall** 以图表和文字结合展示结果
- **When** 展示买卖点 **the system shall** 在K线图上标注位置
- **When** 展示中枢 **the system shall** 用矩形框标识中枢区间

## 4. 非功能需求

### 4.1 性能需求

#### NFR-4.1.1 响应时间
- **When** 分析单只股票 **the system shall** 在5秒内完成基础分析
- **When** 执行回测 **the system shall** 在30秒内完成1年历史数据回测

#### NFR-4.1.2 并发能力
- **When** 多用户同时使用 **the system shall** 支持至少10个并发请求

### 4.2 可用性需求

#### NFR-4.2.1 易用性
- **When** 用户首次使用 **the system shall** 提供使用指南和示例
- **When** 输出结果 **the system shall** 使用通俗易懂的语言解释缠论概念

#### NFR-4.2.2 容错性
- **When** 数据异常 **the system shall** 给出明确错误提示而非崩溃
- **When** 网络中断 **the system shall** 支持断点续传或重试

### 4.3 可维护性需求

#### NFR-4.3.1 代码质量
- **When** 开发 **the system shall** 遵循PEP8代码规范
- **When** 提交代码 **the system shall** 包含单元测试，覆盖率不低于80%

#### NFR-4.3.2 文档完整性
- **When** 发布 **the system shall** 提供完整的API文档和用户手册
- **When** 更新 **the system shall** 维护变更日志

## 5. 约束条件

### 5.1 技术约束
- 必须兼容OpenClaw skill开发规范
- 必须复用现有缠论分析系统核心代码
- 必须支持Python 3.8+

### 5.2 业务约束
- 仅支持A股市场
- 不提供投资建议，仅供研究参考
- 必须标注数据来源和免责声明

### 5.3 法律约束
- 遵守相关证券法律法规
- 不得用于非法用途
- 保护用户数据隐私

## 6. 依赖关系

### 6.1 内部依赖
- 依赖现有缠论分析系统（chanlun包）
- 依赖核心类型定义（Fractal, Pen, Segment, Pivot）
- 依赖分析器（ChanLunAnalyzer）
- 依赖回测框架（Backtester）

### 6.2 外部依赖
- OpenClaw平台SDK
- 数据源接口（tushare/akshare）
- 可视化库（matplotlib）

## 7. 验收标准

### 7.1 功能验收
- 所有功能需求项均有对应测试用例并通过
- 能够正确识别缠论各元素（分型、笔、线段、中枢）
- 能够准确识别买卖点
- 回测功能正常运行并生成报告
- 预测功能给出合理推演

### 7.2 性能验收
- 响应时间满足NFR-4.1要求
- 并发测试通过

### 7.3 集成验收
- 成功注册到OpenClaw平台
- 能够响应OpenClaw调用
- 结果展示正常

## 8. 术语表

| 术语 | 定义 |
|------|------|
| 分型 | K线图中由三根K线构成的顶底结构 |
| 笔 | 两个相邻的顶底分型之间的走势 |
| 线段 | 由至少三笔构成的趋势段落 |
| 中枢 | 至少三段重叠区域构成的价格区间 |
| 第一买点 | 走势离开中枢后发生背驰形成的买点 |
| 第二买点 | 第一次回拉不破中枢形成的买点 |
| 第三买点 | 新中枢形成后回拉形成的买点 |
| 背驰 | 走势力度减弱的现象 |
| OpenClaw | 开放的AI助手插件平台 |
| Skill | OpenClaw平台的功能插件 |

---

**文档结束**
