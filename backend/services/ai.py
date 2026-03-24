"""
AI service — generates competitor intelligence digests.
Uses Anthropic Claude Sonnet.

Day 3 feature — interface defined, stub for Day 1.
"""
import os
from typing import Optional


DIGEST_PROMPT = """You are an AI competitive intelligence analyst for RivalEdge.

Analyze the following competitor snapshots and generate a concise, actionable digest for the user.

Focus on:
- Significant changes (new features, pricing, messaging shifts)
- Strategic signals (hiring, partnerships, product launches)
- Threats and opportunities for the user's business

Format the digest in markdown with clear sections.

Competitor data:
{competitor_data}

Generate a professional, actionable digest in 300-500 words."""


async def generate_digest(
    user_id: str,
    competitors: list[dict],
    snapshots: list[dict],
) -> str:
    """
    Generate an AI digest from competitor snapshots.
    
    Args:
        user_id: The user's ID (for personalization)
        competitors: List of competitor records
        snapshots: List of recent snapshots with diffs
    
    Returns:
        Markdown-formatted digest string
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    
    import anthropic
    
    # Build context from snapshots
    competitor_data = _format_competitor_data(competitors, snapshots)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": DIGEST_PROMPT.format(competitor_data=competitor_data),
            }
        ],
    )
    
    return message.content[0].text


def _format_competitor_data(competitors: list[dict], snapshots: list[dict]) -> str:
    """Format competitor + snapshot data for the AI prompt."""
    lines = []
    
    snapshot_map = {s["competitor_id"]: s for s in snapshots}
    
    for comp in competitors:
        comp_id = comp["id"]
        snapshot = snapshot_map.get(comp_id, {})
        content = snapshot.get("content", {})
        diff = snapshot.get("diff", {})
        
        lines.append(f"## {comp.get('name') or comp.get('url')}")
        lines.append(f"URL: {comp.get('url')}")
        lines.append(f"Title: {content.get('title', 'N/A')}")
        lines.append(f"Description: {content.get('description', 'N/A')}")
        
        if diff:
            lines.append("### Changes since last scan:")
            for field, change in diff.items():
                lines.append(f"- **{field}**: {change.get('before', '')} → {change.get('after', '')}")
        
        lines.append("")
    
    return "\n".join(lines)
