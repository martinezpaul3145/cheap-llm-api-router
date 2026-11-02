import json
from dataclasses import dataclass

@dataclass
class Offer:
    provider: str
    model: str
    input_price: float
    output_price: float
    latency_ms: int
    official: bool = True

OFFERS = [
    Offer('openai', 'gpt-4o-mini', 0.15, 0.60, 420, True),
    Offer('relay-a', 'gpt-4o-mini', 0.10, 0.45, 780, False),
    Offer('relay-b', 'gpt-4o-mini', 0.08, 0.50, 1100, False),
    Offer('anthropic', 'claude-3-haiku', 0.25, 1.25, 500, True),
    Offer('relay-c', 'claude-3-haiku', 0.18, 0.95, 900, False),
]

def estimate(offer, input_tokens, output_tokens, require_official=False):
    if require_official and not offer.official:
        return None
    return (offer.input_price * input_tokens + offer.output_price * output_tokens) / 1_000_000

def cheapest(model, input_tokens=1000, output_tokens=500, require_official=False):
    candidates = []
    for o in OFFERS:
        if o.model != model:
            continue
        cost = estimate(o, input_tokens, output_tokens, require_official)
        if cost is not None:
            candidates.append((cost, o.latency_ms, o))
    if not candidates:
        raise ValueError(f'No offer for {model}')
    cost, latency, offer = min(candidates, key=lambda x: (x[0], x[1]))
    return {
        'provider': offer.provider,
        'model': offer.model,
        'estimated_cost_usd': round(cost, 6),
        'latency_ms': latency,
        'official': offer.official,
    }

if __name__ == '__main__':
    query = {
        'model': 'gpt-4o-mini',
        'input_tokens': 2000,
        'output_tokens': 800,
        'require_official': False,
    }
    result = cheapest(**query)
    print(json.dumps(result, indent=2))
    print('All offers:')
    for row in OFFERS:
        cost = estimate(row, query['input_tokens'], query['output_tokens'], query['require_official'])
        print(row.provider, cost)