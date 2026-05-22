# PiM 校验工具

希尔顿欢朋中国区 Pre-opening PiM Pack 自动校验工具。

## 在线使用

**网址**：https://maxhu0321-source-pim-optimizer-app-r7mqo2.streamlit.app

操作：上传 PiM Pack (.xlsb) + PMS标准代码表 (.xlsx) → 点"开始校验" → 查看结果 → 下载PDF报告

## 功能

### 1. 自动校验
上传两个文件，自动检测 30+ 条规则：

| 类别 | 说明 | 规则数 |
|------|------|--------|
| A 跨文件一致性 | PiM与PMS房型代码、房量匹配 | 3 |
| B 内部一致性 | 无烟房/沙发/连通房等数据前后一致 | 6 |
| C 品牌标准 | 无烟≥30%、连通≥2、无障碍、SLS沙发床 | 7 |
| D 必填项 | 描述/ADR/电话/经纬度/安保/城市 | 9 |
| E 格式检查 | 面积整数、字符限制、经纬度格式 | 7 |

### 2. 房型明细对照
同时上传两个文件时，显示 PiM 与 PMS 的房型对照表（代码、房量、匹配状态）。

### 3. PDF报告下载
生成带品牌字体的中文PDF校验报告，含错误位置指引和修改建议。

### 4. 规则管理（密码保护）
侧边栏进入，可调整品牌标准阈值（无烟比例、连通房数等）。

## 本地运行

```bash
pip install -r requirements.txt
# Web界面
python -m streamlit run app.py
# CLI
python cli.py validate --pim apac.xlsb --pms pms.xlsx --out report.md
```

## 项目结构

```
├── app.py                          # Streamlit Web界面
├── cli.py                          # 命令行入口
├── requirements.txt
├── packages.txt                    # Streamlit Cloud系统依赖
├── fonts/                          # 品牌字体（思源黑体+HamptonSans）
├── error_catalog.md                # 错误对照库
├── pim_optimizer/
│   ├── config.py                   # 字段映射 + 品牌标准常量
│   ├── models.py                   # 数据模型
│   ├── location_labels.py          # 错误位置→用户友好描述
│   ├── extractors/
│   │   ├── pim_extractor.py        # PiM .xlsb 读取（动态列检测）
│   │   └── pms_extractor.py        # PMS .xlsx 读取
│   ├── validators/
│   │   ├── engine.py               # 规则注册+执行引擎
│   │   ├── rules_cross_file.py     # A类
│   │   ├── rules_internal.py       # B类
│   │   ├── rules_brand.py          # C类
│   │   ├── rules_completeness.py   # D类
│   │   └── rules_format.py         # E类
│   └── reporters/
│       ├── pdf_reporter.py         # PDF报告
│       ├── json_reporter.py        # JSON报告
│       └── markdown_reporter.py    # Markdown报告
└── .streamlit/config.toml
```

## 技术说明

- PiM Pack (.xlsb) 通过 pyxlsb 只读解析，支持多版本模板（动态列检测）
- PMS (.xlsx) 通过 openpyxl 解析，自动识别房型汇总区与房号明细区的边界
- 跨文件匹配逻辑：PiM房型代码 ↔ PMS希尔顿渠道代码（非内部代码）
- 规则引擎基于装饰器注册，新增规则只需加一个函数

## 新增规则

在对应 `rules_*.py` 中添加：
```python
@rule("C08", "brand", "error")
def new_rule(pim: PiMData, pms: PMSData | None) -> list[ValidationError]:
    errors = []
    # 校验逻辑
    return errors
```

## 部署

- 仓库为 private
- Streamlit Cloud 自动从 GitHub main 分支部署
- push 后约1-2分钟自动更新
