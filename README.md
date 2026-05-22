# PiM 优化工具

希尔顿欢朋中国区 Pre-opening PiM Pack 校验与AI辅助填写工具。

## 功能

### 1. 自动校验 (validate)
上传 PiM Pack(.xlsb) + PMS代码表(.xlsx)，自动检测30+种常见错误：
- **A类** 跨文件一致性：房型代码/房量 PiM↔PMS 匹配
- **B类** PiM内部一致性：无烟房/沙发/连通房等数据前后矛盾
- **C类** 品牌标准：无烟≥30%、连通房≥2、无障碍房、SLS沙发床
- **D类** 必填项：描述/ADR/电话/经纬度/安保/城市/到达信息
- **E类** 格式：面积整数、字数限制、经纬度、楼层数

### 2. AI描述生成 (generate)
输入酒店基础信息JSON，Claude API自动生成：
- 酒店描述（中英文）
- Tagline
- 各房型描述（short/line1-3/long，含字符限制校验）

## 使用

```bash
pip install -r requirements.txt

# 校验（输出Markdown报告）
python cli.py validate --pim apac.xlsb --pms pms.xlsx --out report.md

# 校验（输出JSON）
python cli.py validate --pim apac.xlsb --out report.json

# AI生成 - 先初始化模板
python cli.py generate --init-template hotel_info.json
# 填写后生成
python cli.py generate --input hotel_info.json --out descriptions.json
```

## 项目结构

```
├── cli.py                       # 统一CLI入口
├── requirements.txt             # openpyxl, pyxlsb, anthropic
├── pim_ai_descriptions.py       # AI生成（独立脚本，可单独运行）
├── pim_room_check.py            # 旧版房型对比脚本（已被新引擎替代）
└── pim_optimizer/               # 核心包
    ├── models.py                # 数据模型
    ├── config.py                # 字段映射 + 品牌常量
    ├── extractors/
    │   ├── pim_extractor.py     # PiM .xlsb 读取（PiM-1/2/5）
    │   └── pms_extractor.py     # PMS .xlsx 读取（1.4 酒店客房）
    ├── validators/
    │   ├── engine.py            # 规则注册+执行引擎
    │   ├── rules_cross_file.py  # A类规则
    │   ├── rules_internal.py    # B类规则
    │   ├── rules_brand.py       # C类规则
    │   ├── rules_completeness.py # D类规则
    │   └── rules_format.py      # E类规则
    ├── generators/              # AI生成（待重构）
    └── reporters/
        ├── json_reporter.py
        └── markdown_reporter.py
```

## 新增规则方法

在对应 `rules_*.py` 文件中添加：
```python
@rule("C08", "brand", "error")
def new_rule(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    errors = []
    # 校验逻辑...
    return errors
```
无需修改引擎代码。

## 开发状态

- [x] 数据提取器（PiM xlsb + PMS xlsx）
- [x] 校验引擎 + 30条规则
- [x] 报告输出（Markdown + JSON）
- [x] CLI
- [ ] PiM-5设施列精确映射（需真实已填数据）
- [ ] AI生成模块重构进包
- [ ] 飞书机器人对接

## 部署规划

Phase 1: 本地CLI（当前）
Phase 2: FastAPI后端 + 飞书自定义机器人（不用妙搭，无法解析xlsb/调API）
