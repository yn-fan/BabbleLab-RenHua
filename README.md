# BabbleLab-RenHua · 人话

让文字更清楚，也更像作者自己。

RenHua 是一套以中文为主、兼顾英文的编辑技能。它把 [lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) 的中文检测方法与 [humanizer](https://github.com/blader/humanizer) 的编辑经验整合成一个入口：找到具体问题，做有依据的修改，检查有没有改丢信息。

**许可：公开源码，非商业使用。** 融合内容采用 [CC BY-NC 4.0](LICENSE)，受 lieflat 上游非商用条款约束；humanizer 的原有 MIT 权利与声明保留。它不是允许任意商用的 OSI 开源许可证。商业使用须先取得相关权利人的许可，我们不能代替上游授权。详见[来源与许可](skills/babblelab-renhua/THIRD_PARTY.md)。

## 能做什么

- **改稿**：清理空话、模板化铺垫、重复收尾和不必要的翻译腔，保留事实、语气与作者习惯。
- **诊断**：指出原文位置、具体问题、建议改法和应当保留的表达。
- **复核**：比较改前改后，核对数字、限定词、引文、来源和观点有没有变化。

适合文章、公众号草稿、邮件、评论和产品说明。中文检测脚本只提供候选与统计；改写由运行技能的模型完成。脚本本地运行，无第三方依赖，不上传文章；使用技能时，文章仍会进入你选择的模型会话。

它不判断作者是不是 AI，不给“AI 率”，不承诺通过任何检测器。

## 快速开始

```bash
git clone https://github.com/yn-fan/BabbleLab-RenHua.git
cd BabbleLab-RenHua
```

### Codex

把完整技能复制到个人技能目录；已有同名目录时安装器会停止：

```bash
python3 tools/install.py --to ~/.agents/skills
```

在会话中使用：

```text
$babblelab-renhua 帮我把下面这段改得自然一些。保留事实和原有立场，直接给成稿。
```

技能发现路径依据 [OpenAI 官方技能文档](https://developers.openai.com/codex/skills/)。若界面尚未显示新技能，重新打开会话或重启客户端。

### Claude Code

```bash
python3 tools/install.py --to ~/.claude/skills
```

```text
/babblelab-renhua 先诊断这篇文章，列出具体问题，暂时不改。
```

安装位置与命令格式见 [Claude Code 官方技能文档](https://code.claude.com/docs/en/skills)。

其他支持 `SKILL.md` 的工具，可导入整个 [skills/babblelab-renhua](skills/babblelab-renhua) 文件夹。没有技能功能时，也可以把 [SKILL.md](skills/babblelab-renhua/SKILL.md) 和需要的参考文件交给模型作为编辑说明。

### 按需求工作

| 你这样说 | 技能会这样做 |
|---|---|
| “去掉 AI 味，直接改” | 完成保守改写与内部复核，交付成稿 |
| “先看看问题” | 给诊断与例句，保留原稿 |
| “可以重排，改得彻底一点” | 重组表达与段落，仍保留事实和论证关系 |
| “按这篇样稿的风格” | 以样稿的语气、标点和节奏为准 |
| “只检查改前改后有没有漏信息” | 核对差异，不继续润色 |

## 本地检测与前后对照

需要 Python 3.9 或以上。以下命令在仓库根目录运行，只读输入；`--out` 只能创建新文件，不能覆盖原稿或已有结果。

```bash
# 中文写作候选；短文也能检查，但不据此评价全文分布
python3 skills/babblelab-renhua/scripts/renhua.py analyze examples/zh-before.md

# 保存原始指标，便于追溯
python3 skills/babblelab-renhua/scripts/renhua.py analyze examples/zh-before.md --json --out before.json

# 抽取需要结合语境判断的候选；脚本不会代替模型打标签
python3 skills/babblelab-renhua/scripts/renhua.py candidates examples/zh-before.md --out candidates.json

# 比较原稿和编辑稿，导出静态 HTML 对照
python3 skills/babblelab-renhua/scripts/renhua.py compare examples/zh-before.md examples/zh-after.md --format html --out comparison.html
```

`compare` 也支持 Markdown（默认）和 JSON。英文稿按英文规则做语义编辑，中文统计不适用于英文。原始引擎存在 Markdown 粗解析和候选抽样限制，详见[工具说明](docs/tooling.md)；命中数量减少不等于文字变好。

## 我们怎样融合

| 来源 | 保留的能力 | RenHua 的调整 |
|---|---|---|
| lieflat-less-ai-tone | 中文句式统计、四类语义候选、最小修改、改前改后复核 | 按用户意图决定是否先出报告；统计作为线索；研究数字不包装成我们的实验结论 |
| humanizer | 段落与篇章检查、26 类编辑模式、作者声音、事实复核 | 中文与英文分别适配；真实转折和正常格式保留；不用补写经历或情绪制造“人味” |
| BabbleLab | 统一入口、本地命令、可安装技能包、原创示例与回归用例 | 事实优先；改稿和诊断分开；输出成稿为默认 |

两套规则发生冲突时的选择记录在[整合决策](docs/integration.md)。上游固定提交与文件校验值见 [sources.lock.json](skills/babblelab-renhua/sources.lock.json)。

## 示例与开发

- 中文：[改前](examples/zh-before.md) / [改后](examples/zh-after.md)
- 英文：[改前](examples/en-before.md) / [改后](examples/en-after.md)
- 编辑示例的说明：[examples/README.md](examples/README.md)
- 参与维护：[CONTRIBUTING.md](CONTRIBUTING.md)
- 首版检查范围：[验证记录](docs/validation.md)

```bash
python3 -m unittest discover -s tests -v
```

本地检查覆盖命令输入输出、输入保护、HTML 转义、安装包完整性与上游文件校验。文风效果需要结合具体文章评审，自动检查不能证明改写质量，也不能证明模型客户端已经完成兼容性实测。

## 致谢

感谢 shiujan / [larashero3-dotcom](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) 和 Siqi Chen / [blader](https://github.com/blader/humanizer) 的工作。RenHua 是独立维护的改编项目；上游作者未为本项目背书。
