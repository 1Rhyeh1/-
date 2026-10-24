# 实验5 - 中学生英语单词智能记忆与错词分析系统（桌面版）

面向中学生的**完全离线** AI 背单词与错题分析桌面应用。结合轻量级 NLP
（编辑距离 + 本地形近词表）与间隔重复记忆法（SM-2），实现「测试 → 错词分析 →
动态复习计划」的完整闭环。

## 特性

- **本地词库管理**：SQLite 存储，内置初/高中课标词库（各约 50 词，可扩展）。
- **单词自测与默写**：支持「拼写测试」与「词义选择」两种模式。
- **NLP 错词分析（核心）**：答错时自动区分三类错误
  - `拼写失误`：编辑距离 ≤ 2（如 `aple` → `apple`）；
  - `形近词混淆`：与同形近词组的其它词一致/更接近（如 `effect` / `affect`）；
  - `词义错误`：词义选择题答错。
- **动态间隔重复（SM-2）**：按艾宾浩斯遗忘曲线维护每个词的 EF、间隔与下次复习时间。
- **智能推送与错词本**：启动/复习时优先推送薄弱词汇，自动生成错词本，并用
  matplotlib 绘制「错误类型分布」与「薄弱词汇排行」。

## 技术栈

| 维度 | 选型 |
|---|---|
| 语言 | Python 3.10+ |
| UI | PySide6（现代扁平风格 + QSS） |
| 数据库 | SQLite（内置 `sqlite3`） |
| NLP | rapidfuzz（Levenshtein 编辑距离）+ 本地形近词表 |
| 记忆算法 | SM-2（SuperMemo-2） |
| 图表 | matplotlib（`QtAgg` 后端嵌入） |
| 打包 | PyInstaller（单文件 exe） |

> 说明：为控制 exe 体积（< 200MB），**未引入 Bert 等大模型**，错词判断采用
> 「规则匹配 + 编辑距离」方案。

## 目录结构

```
背单词应用/
├── run.py                  # 启动入口
├── app.spec                # PyInstaller 打包配置
├── build.bat               # Windows 一键打包脚本
├── requirements.txt
├── app/
│   ├── config.py           # 路径与算法参数
│   ├── db/                 # 数据库层（建表 / DAO / 种子数据）
│   ├── core/               # 核心算法（相似度 / 错词分析 / SM-2 / 学习服务）
│   ├── ui/                 # 界面（主窗口 / 三 Tab / 图表 / 测验组件）
│   └── resources/
├── tests/                  # 单元测试
└── data/                   # 运行期生成的 SQLite 数据库（已 gitignore）
```

## 快速开始

### 1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 2. 运行

```bash
python run.py
```

首次运行会自动建库并写入内置词库，在 `data/words.db` 生成数据库文件。

### 3. 运行单元测试

```bash
python -m unittest discover -s tests -t . -v
```

或使用 pytest：

```bash
python -m pytest tests -v
```

## 打包为 Windows exe

在项目根目录执行：

```bat
build.bat
```

或手动执行：

```bash
python -m PyInstaller app.spec --noconfirm
```

产物位于 `dist\WordMemorySystem.exe`，可直接双击运行（无需 Python 环境）。

## 数据库设计

| 表 | 说明 |
|---|---|
| `User` | 用户（用户名、年级） |
| `Word` | 词库（拼写、音标、释义、词性、年级、形近词组 `confusion_group`） |
| `TestRecord` | 测试记录（作答、正误、错误类型、编辑距离） |
| `ErrorBook` | 错词本（错误类型、累计次数、是否攻克） |
| `ReviewSchedule` | SM-2 复习计划（repetition / EF / 间隔 / 下次复习时间 / 状态） |

## 算法说明

- **错词分析**：`app/core/error_analyzer.py`
  - 完全匹配 → `none`
  - 命中形近词 → `confusion`
  - 编辑距离 ≤ 2 → `spelling`
  - 词义题答错 → `meaning`
- **间隔重复**：`app/core/spaced_repetition.py`
  - 答对（quality ≥ 3）：间隔按 `1 → 6 → interval × EF` 递推，repetition +1；
  - 答错（quality < 3）：repetition 归零，间隔重置为 1 天；
  - EF 按 SM-2 公式更新，下限 1.3。

## License

仅供学习与教学使用。