# 排序、HTML/PDF 与推送格式

## 排序评分

每个条目按 1-5 分评价以下维度：

- `heat`：综合热度，优先考虑 X 讨论密度、Hacker News 排名/评论、GitHub Star/Release/Issue 活跃度、官方发布影响面和二次传播强度
- `freshness`：相对简报发送时间的新鲜度，必须在最近 24 小时内
- `strategic_value`：对模型能力、竞争格局、开发者使用或产品决策的改变程度
- `source_quality`：支持来源的直接性和权威性
- `platform_signal`：该条目在 GitHub、X、Hacker News 上浮现的强度
- `frontier_vendor_fit`：是否来自 OpenAI、Gemini、Anthropic、Meta、DeepSeek、ByteDance、Zhipu AI、Alibaba Cloud 等一线模型厂商，且与模型更新直接相关

使用加权分：

`total = heat * 0.20 + freshness * 0.20 + strategic_value * 0.25 + source_quality * 0.15 + platform_signal * 0.10 + frontier_vendor_fit * 0.10`

优先级映射：
- `P1`: total >= 4.2
- `P2`: total >= 3.4 and < 4.2
- `P3`: total < 3.4

只输出综合分最高的 10 条，并按 `total` 从高到低排序。

同分时按以下顺序打破平局：
1. `heat` 更高
2. GitHub、X、Hacker News 信号更强
3. 是否来自一线模型厂商并直接涉及模型更新
4. 主源更权威
5. 发布时间更新

## 摘要风格

每个条目控制在一个移动端卡片内：

1. 排名、优先级和日期
2. 一句话摘要
3. 一句话影响判断
4. 热度依据
5. 来源链接
6. 发现渠道，例如 `GitHub`、`X`、`Hacker News`

整份 PDF 保持足够紧凑，使读者能在 5 分钟内扫读完 Top 10。

## HTML/PDF 模板

视觉风格：

- 深色背景：`#000000`、`#05080f`、`#0f172a`
- 主文本：`#f8fafc`
- 辅助文本：`#94a3b8`
- 强调色：`#1d9bf0`、`#38bdf8`、`#22d3ee`
- 卡片边框：`rgba(148, 163, 184, 0.22)`
- 卡片背景：`rgba(15, 23, 42, 0.86)`

HTML 内容结构：

```markdown
标题：AI 技术每日简报
副标题：YYYY-MM-DD | 过去 24 小时 | Top 10 热点
摘要：一句话说明今日最高热度信号

卡片 1-10：
- #排名
- 标题
- 摘要
- 为什么重要
- 热度依据
- 组织 / 类型 / 发现渠道 / 日期
- 主源链接
```

PDF 要求：

- 先生成 HTML 文件，再转换为 PDF。
- PDF 文件名建议：`ai-tech-daily-brief-YYYY-MM-DD.pdf`。
- 保持移动端深色风格，但 PDF 页面可居中显示移动端宽度内容。
- 版式必须连续紧凑：不要一条资讯单独占一页；每条资讯之间使用固定小间隔正常排列，同一页应容纳多条资讯。
- 允许卡片在必要时自然跨页，不要使用强制整卡避分页策略造成 PDF 页数膨胀。
- 必要时减少视觉块高度、卡片内边距和摘要长度，以降低用户查阅 PDF 时的翻页和滑动成本。

## 推送格式

主题：

`AI 技术每日简报 | YYYY-MM-DD | Top 10 热点`

正文：

```markdown
今日 AI 技术每日简报已生成，附件为 PDF。

范围：过去 24 小时
内容：按热度排序的 Top 10 AI 资讯
```

优先操作顺序：
1. 使用 163 SMTP 发送邮件并附加 PDF
2. 如果 SMTP 登录失败，保留当天 PDF，不删除产物，并在日志中记录失败原因
3. 如果附件发送失败，保留当天 PDF，不静默降级
4. 只有人工运维确认后，才允许手动补发当天 PDF

收件人：

`yuzili4109@gmail.com`

## 每日节奏

每天本地时间 `01:00` 收集整理过去 24 小时资讯并生成 PDF；每天 `09:00` 推送 PDF。只纳入最近 24 小时内的信息，并将热度最高的 10 条按分数从高到低排列。
