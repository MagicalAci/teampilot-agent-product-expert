import re


PRICE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)")


def analyze_monetization(evidence_records: list[dict]) -> dict:
    pricing_records = [
        record
        for record in evidence_records
        if record["channel"] in {"pricing", "web"} and "pricing" in record["evidence_pool"]
    ]
    extracted_prices = []
    for record in pricing_records:
        extracted_prices.extend(PRICE_PATTERN.findall(record["summary"]))

    unique_prices = []
    for price in extracted_prices:
        if price not in unique_prices:
            unique_prices.append(price)

    return {
        "pricing_records_count": len(pricing_records),
        "price_points": unique_prices[:8],
        "value_gate_signals": infer_value_gate_signals(pricing_records),
        "candidate_questions": build_monetization_questions(pricing_records, unique_prices[:8]),
        "signal_summary": "已提取价格点和付费触发相关文本信号，适合继续和用户一起确认商业化路径。",
    }


def infer_value_gate_signals(pricing_records: list[dict]) -> list[str]:
    joined = " ".join(record["summary"] for record in pricing_records)
    signals = []
    if any(keyword in joined for keyword in ["免费试用", "试用", "限免"]):
        signals.append("出现试用相关信号")
    if any(keyword in joined for keyword in ["会员", "高级版", "pro"]):
        signals.append("出现会员拦截信号")
    if not signals:
        signals.append("缺少明显的付费触发信号")
    return signals


def build_monetization_questions(pricing_records: list[dict], price_points: list[str]) -> list[str]:
    questions = []
    if price_points:
        questions.append(f"当前已识别价格点：{', '.join(price_points)}，这些价格点分别对应什么权益？")
    if pricing_records:
        questions.append("当前页面里能否看出免费版与付费版的边界？")
    else:
        questions.append("当前缺少定价页或会员页证据，是否需要补截图或支付前页面？")
    questions.append("价值兑现发生在注册前、试用后，还是核心功能被锁定之后？")
    return questions
