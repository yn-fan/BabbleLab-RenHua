# BabbleLab-RenHua · 人话

把套话改掉，留下作者自己的表达。

RenHua 帮你修改已经写好的文章，以中文为主，也支持英文。它结合了 [lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) 的中文检测方法和 [humanizer](https://github.com/blader/humanizer) 的编辑规则：先找出哪些地方读着费劲、哪些话重复了，再修改表达，核对有没有改丢原意。

**源码公开，限非商业使用。** 融合版采用 [CC BY-NC 4.0](LICENSE)，需要遵守 lieflat 的非商用条款；humanizer 原有的 MIT 授权与声明仍然保留。CC BY-NC 不属于 OSI 定义的开源许可证。商业使用须先取得相关权利人的许可，BabbleLab 无权代上游授权。详见[来源与许可](skills/babblelab-renhua/THIRD_PARTY.md)。

## 能做什么

- 改稿：去掉空话、反复的铺垫和收尾，理顺生硬的翻译腔，保留事实、语气和作者的习惯。
- 诊断：指出哪句话有问题，解释原因并给出改法；有用的表达会说明为什么保留。
- 复核：对照两稿，检查数字、限定词、引文、来源和观点有没有变化。

文章、公众号草稿、邮件、评论和产品说明都可以交给它。改写由你使用的模型完成，中文检测脚本负责统计和找出待检查的片段。脚本在本地运行，没有第三方依赖，也不上传文章；把稿件交给技能编辑时，内容会进入你选择的模型会话。

它不判断作者是不是 AI，不给“AI 率”，不承诺通过任何检测器。

## 快速开始

```bash
git clone https://github.com/yn-fan/BabbleLab-RenHua.git
cd BabbleLab-RenHua
```

### Codex

运行下面的命令，将完整技能安装到个人目录。如果已有同名目录，安装器会停止。

```bash
python3 tools/install.py --to ~/.agents/skills
```

在会话中使用：

```text
$babblelab-renhua 帮我把下面这段改得自然一些。保留事实和原有立场，直接给成稿。
```

安装位置见 [OpenAI 官方技能文档](https://developers.openai.com/codex/skills/)。如果界面里还没出现新技能，重新打开会话或重启客户端。

### Claude Code

```bash
python3 tools/install.py --to ~/.claude/skills
```

```text
/babblelab-renhua 先诊断这篇文章，列出具体问题，暂时不改。
```

安装位置与命令格式见 [Claude Code 官方技能文档](https://code.claude.com/docs/en/skills)。

其他支持 `SKILL.md` 的工具，可以导入整个 [skills/babblelab-renhua](skills/babblelab-renhua) 文件夹。如果工具没有技能功能，把 [SKILL.md](skills/babblelab-renhua/SKILL.md) 和需要的参考文件作为编辑说明交给模型也可以。

### 按需求工作

| 你这样说 | 技能会这样做 |
|---|---|
| “去掉 AI 味，直接改” | 完成保守改写与内部复核，交付成稿 |
| “先看看问题” | 给诊断与例句，保留原稿 |
| “可以重排，改得彻底一点” | 重组表达与段落，仍保留事实和论证关系 |
| “按这篇样稿的风格” | 以样稿的语气、标点和节奏为准 |
| “只检查改前改后有没有漏信息” | 核对差异，不继续润色 |

## 本地检测与前后对照

需要 Python 3.9 或以上。在仓库根目录运行下面的命令，原稿不会被修改。`--out` 只能创建新文件，不能覆盖原稿或已有结果。

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

`compare` 默认输出 Markdown，也可以输出 JSON。英文稿需要按英文规则阅读和修改，中文统计不适用于英文。检测脚本对 Markdown 的解析比较粗；语义候选过多时还会抽样，具体限制见[工具说明](docs/tooling.md)。检测项变少，不代表文章就更好了，仍要读一遍改稿。

## 我们怎样融合

| 来源 | 保留的能力 | RenHua 的调整 |
|---|---|---|
| lieflat-less-ai-tone | 中文句式统计、四类语义候选、最小修改、改前改后复核 | 按用户意图决定是否先出报告；统计作为线索；研究数字不包装成我们的实验结论 |
| humanizer | 段落与篇章检查、26 类编辑模式、作者声音、事实复核 | 中文与英文分别适配；真实转折和正常格式保留；不用补写经历或情绪制造“人味” |
| BabbleLab | 统一入口、本地命令、可安装技能包、原创示例与回归用例 | 事实优先；改稿和诊断分开；输出成稿为默认 |

两套规则有些地方意见不同，我们的取舍写在[整合决策](docs/integration.md)里。使用了上游哪个提交、文件校验值是多少，都记在 [sources.lock.json](skills/babblelab-renhua/sources.lock.json) 中。

## 示例与开发

- 中文：[改前](examples/zh-before.md) / [改后](examples/zh-after.md)
- 英文：[改前](examples/en-before.md) / [改后](examples/en-after.md)
- 编辑示例的说明：[examples/README.md](examples/README.md)
- 参与维护：[CONTRIBUTING.md](CONTRIBUTING.md)
- 首版检查范围：[验证记录](docs/validation.md)

```bash
python3 -m unittest discover -s tests -v
```

这些检查验证命令能否正确读写、原稿是否受到保护、HTML 是否正确转义、安装包和上游文件是否完整。改稿是否合适，还得结合具体文章判断；测试通过也不等于已经在各个模型客户端里实际用过。

## 致谢

感谢 shiujan / [larashero3-dotcom](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) 和 Siqi Chen / [blader](https://github.com/blader/humanizer) 的工作。RenHua 是 BabbleLab 独立维护的改编项目，上游作者未为本项目背书。
