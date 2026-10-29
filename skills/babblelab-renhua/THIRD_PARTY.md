# 来源、改编与许可

BabbleLab-RenHua 由 BabbleLab 独立维护。Copyright (c) 2026 BabbleLab contributors。

融合内容与本项目新增文件采用 [CC BY-NC 4.0](LICENSE)。允许在遵守署名、标注修改等条件的前提下进行非商业分享和改编。完整条款以许可证为准；公开仓库不等于任意商用许可，也不属于 OSI 定义的开源许可证。

下述第三方材料仍保留原作者版权与原许可。MIT 原有授权不被本文件撤销；但不能因此把含 CC BY-NC 材料的融合版本作为无非商用限制的整体分发或使用。商业使用须先向相关权利人取得许可，本项目无权代上游授权。上游作者未赞助或认可本项目。

## lieflat-less-ai-tone

- 项目：[larashero3-dotcom/lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone)
- 作者与版权：**Copyright (c) 2026 shiujan**。
- 固定提交：[fe13f1a0712cd2c138b6cdc500a77927d5bf04ec](https://github.com/larashero3-dotcom/lieflat-less-ai-tone/tree/fe13f1a0712cd2c138b6cdc500a77927d5bf04ec)
- 原许可：[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)，[上游原始声明](scripts/vendor/lieflat/LICENSE) 原样保留。上游注明商业授权另行联系作者。
- 原样收录：`scripts/detect.py` → `scripts/vendor/lieflat/detect.py`；`LICENSE` → `scripts/vendor/lieflat/LICENSE`。文件内容未修改，仅移动目录；SHA-256 见 [sources.lock.json](sources.lock.json)。
- 改编：主技能的保守编辑与复核流程、中文规则、四类语义候选判断方法。参考了上游 `SKILL.md`、`DETECT.md`、`references/semantic-criteria.md` 和研究说明。
- 修改：由用户意图决定诊断或直接改写；允许结合完整上下文复核；给语言现象与编辑处置分开记录；统计只做线索；改用原创保真示例。没有收录上游的文章案例、完整研究语料、研究文档、旧报告生成器和语料比较脚本。

## humanizer

- 项目：[blader/humanizer](https://github.com/blader/humanizer)
- 作者与版权：**Copyright (c) 2025 Siqi Chen**。
- 固定提交：[0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0](https://github.com/blader/humanizer/tree/0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0)，技能版本 3.1.0。
- 原许可：[MIT 完整许可](licenses/humanizer-MIT.txt)，原样保留。
- 改编：`SKILL.md` 中的 26 类模式、段落级检查、作者风格优先与事实复核。英文参考按原模式编号映射到 10 组；主技能和中文规则吸收适用的编辑原则。
- 修改：语言与体裁分别处理；保留真实否定、正常清单与必要标点；不添加作者未表达的经历或情绪；默认只交付最终稿。未复制上游示例或 README。

humanizer 将 Wikipedia 的 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) 列为其参考背景。本仓库不复制该百科页面，也不把它当作作者身份检测依据。

## 新增内容与验证范围

BabbleLab 编写统一入口、安装器、对照输出、原创示例、整合决策和回归用例。文稿编辑由用户选择的模型执行；本仓库不提供模型、账号、外部 API 或上游商业授权。

上游关于语料规模与统计研究的描述属于上游自述，BabbleLab 未独立复现完整研究。文件哈希验证只能确认快照一致，不能验证研究结论或保证编辑效果。

分发完整技能目录时请保留本文件、`LICENSE`、`licenses/`、`sources.lock.json` 与 `scripts/vendor/lieflat/LICENSE`。
