# 来源与搜索

## 覆盖优先级

优先跟踪一线模型厂商及其相邻生态信号：
- OpenAI
- Gemini / Google DeepMind
- Anthropic
- Meta AI
- DeepSeek
- ByteDance / 豆包 / Seed
- Zhipu AI / GLM
- Alibaba Cloud / Qwen / 通义千问

二级关注：
- NVIDIA、Microsoft AI、xAI、AWS AI、Mistral AI、Cohere 等会影响模型能力、部署、推理成本或生态格局的更新
- 对全球前沿产生实质影响的开源模型、Agent、推理框架、评测、基础设施和开发者工具社区

## 发现渠道

将以下渠道作为发现最近 24 小时内重要事项的主入口：

1. GitHub Trending、关键仓库 Release、PR、Issue、Discussion、Star 增速和热门 AI 项目
2. X 上一线模型厂商、创始人、研究员、产品负责人、开源维护者和高信号策展账号的帖子
3. Hacker News 首页、newest、Ask/Show HN 以及 AI 相关讨论线程

发现后，用以下来源核验：

1. 官方公告、Release note、博客、文档、研究页、投资者关系页面
2. GitHub Release、仓库 README、Issue/PR 讨论、benchmark repo
3. arXiv、会议页面、论文主页
4. 必要时参考可靠科技或财经媒体的高信号报道

## 模型厂商重点

围绕 OpenAI、Gemini、Anthropic、Meta、DeepSeek、ByteDance、Zhipu AI、Alibaba Cloud 优先查找：
- 新模型、推理模型、多模态模型、语音/视频/图像模型发布
- API、SDK、价格、上下文长度、速率限制、可用区域、企业版能力变化
- 评测、系统卡、技术报告、论文、模型卡、开源权重或许可更新
- 官方产品入口变化，例如 ChatGPT、Gemini、Claude、Meta AI、DeepSeek、豆包、GLM、通义千问/Qwen
- 开发者可直接使用的仓库、示例、cookbook、benchmark 或部署工具更新

同等条件下，模型能力或开发者可用性变化优先于融资、人事、泛观点文章。

## GitHub 指引

重点查找：
- 一线模型厂商官方组织和相关仓库的最近 24 小时 Release、tag、README 重大更新
- GitHub Trending 中与大模型、Agent、推理、训练、RAG、评测、MLOps、开发者工具相关的新项目
- Star、fork、watch 或贡献者活动的异常增长
- Issue、PR、Discussion 中暴露出的真实采用、性能、兼容性或安全信号
- 官方组织仓库与核心维护者账号发布的源头信息

优先引用仓库、Release 或 PR 等可验证链接。不要只用第三方榜单或转发帖作为证据。

## X 指引

重点查找：
- 官方公司账号发布的产品、模型、API、研究和价格更新
- 创始人、模型研究员、开源维护者、基础设施负责人的源头帖子
- 围绕同一发布形成的独立讨论簇
- 补充具体技术细节、benchmark 限制、价格上下文、部署影响的引用帖

将 X 互动量视为热度信号，不视为事实证明。

## Hacker News 指引

重点查找：
- 首页或接近首页的 AI 发布帖
- 多个线程反复出现的同一主题
- 评论中指出实际影响、质疑点或缺失背景的强信号
- 指向原始发布、仓库、论文或 demo 的链接

优先打开原始链接，不要只总结 HN 讨论本身。

## 建议搜索批次

使用多个聚焦搜索，而不是一个宽泛查询。示例：

- `OpenAI model API release last 24 hours`
- `Gemini Google DeepMind model update last 24 hours`
- `X Anthropic Claude latest`
- `X Gemini latest model launch`
- `X OpenAI launch latest`
- `X DeepSeek model latest`
- `X ByteDance Seed Doubao model latest`
- `Zhipu AI GLM model release last 24 hours`
- `Alibaba Cloud Qwen Tongyi model release last 24 hours`
- `GitHub OpenAI Anthropic Gemini DeepSeek Qwen GLM release last 24 hours`
- `GitHub Trending AI LLM agents inference today`
- `site:news.ycombinator.com OpenAI OR Anthropic OR Gemini OR DeepSeek OR Qwen OR GLM AI`
- `frontier AI model benchmark paper release arXiv last 24 hours`

## 来源启发

将以下内容视为高优先级触发器：
- 新旗舰模型、推理模型或多模态模型发布
- 对开发者有影响的 API、SDK、价格、速率限制、上下文窗口或产品可用性变化
- 官方技术报告、系统卡、模型卡、论文和 benchmark
- 开源权重、许可、推理部署、工具链或 cookbook 更新
- 可能改变前沿认知的 benchmark 结果
- 有商业影响的安全、政策、许可、出口管制动态

除非影响面很大，否则降低以下内容优先级：
- 泛泛而谈的观点文章
- 重复性盘点文章
- 没有模型能力或开发者影响的小功能更新
- 缺少可验证源材料的孤立爆款帖子
- 超出最近 24 小时窗口的旧闻

## 时间窗口

只使用最近 24 小时内发布或实质更新的信息。

不要扩展到 72 小时。当天信息较少时，发送较短但高质量的简报，并在 `观察清单` 中标注仍需等待主源确认的事项。

最终简报始终使用绝对日期。

## 每日运行预期

假设该流程用于每天本地时间 `01:00` 的固定收集整理运行，覆盖此前 24 小时内的一线模型厂商动态、GitHub/X/Hacker News 热点和夜间升温内容。每天 `09:00` 只负责推送已生成的 PDF 简报，不重新扩大采集窗口。
