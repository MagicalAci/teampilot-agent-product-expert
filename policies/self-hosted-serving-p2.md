# 自托管推理服务（P2 · 仅未来自托管小模型时）

这是 `cost-discipline-methodology.md` 的"重 serving"延伸。结论先行：本仓库是 **Cursor 原生、模型由 IDE 提供、无自有 serving**，所以 vLLM/SGLang/量化/解耦服务**当前一律不适用**。本文件只在**未来要本地化 router / embedding / rerank 小模型**时提供选型，避免临时抓瞎；现在**不引入任何依赖**。

> 来源 `findings/12-model-routing-cost.md`。务必先用 RouterBench/RouterArena 式基准**证伪"贵=好"**，确认本地小模型确有 ROI 再自托管。

---

## 0. 触发判定（默认全否）

| 触发条件 | 才考虑自托管 |
|---|---|
| 隐私/合规要求模型不出内网 | 是 |
| 高频固定负载（router/embedding/rerank）API 成本已显著 | 是 |
| 需要 API 不提供的定制小模型 | 是 |
| 单用户、按需、用 IDE 模型 | **否（当前）** |

## 1. 哪些组件值得本地化（按性价比排序）

1. **embedding / rerank 小模型**（BGE-M3 / bge-reranker）——最该先本地化：高频、模型小、省 API 调用，服务于 `advanced-retrieval-p2.md` §1。
2. **router 小模型**（语义路由 encoder）——毫秒级、可全本地，服务于 `intent-routing-and-dialog.md` 语义层。
3. **生成大模型**——最重、最不划算自托管，除非强合规；优先继续用 API/IDE。

## 2. Serving 选型（触发后）

| 引擎 | 强项 | 何时选 |
|---|---|---|
| **vLLM** | PagedAttention + APC 默认 + continuous batching | 高并发、唯一前缀多 |
| **SGLang** | RadixAttention token 级前缀复用 | 高前缀重用场景 |
| **TGI** | 生态广、易部署 | 通用、HuggingFace 栈 |
| **TensorRT-LLM / Dynamo** | 极致延迟 / 解耦 prefill-decode + KV-aware 路由 | 大规模、低延迟 SLA |

- **量化（awareness）**：显存紧 → FP8 / AWQ / GPTQ（INT8/INT4）；先评精度损失。
- **推理优化**：speculative decoding（低延迟）、prefix/KV 复用、cache-aware routing。

## 3. 与本仓库接线
- `cost-discipline-methodology.md` 的"P2 自托管"指向本文件；明确触发条件 = 本地化小模型且证明 ROI。
- 本地 embedding/rerank 落地后，作 `advanced-retrieval-p2.md` §1 的密集层后端（`scripts/retrieval_index.py` 的 `EMBED_ENDPOINT` 可指向本地 vLLM `/embeddings`）。

## 何时查阅
- 出现强合规/高频成本/定制模型需求 → §0 判触发 → §1–§2 选型
- 否则不查（当前不适用）
