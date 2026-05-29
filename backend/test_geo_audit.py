import asyncio
import sys
import os
sys.path.insert(0, '.')

# Load API key
import json
with open(os.path.expanduser('~/.openclaw/secrets.json')) as f:
    secrets = json.load(f)
os.environ['OPENROUTER_API_KEY'] = secrets['openrouter']['api_key']

from agents.geo_audit_generator import generate_geo_audit

async def test():
    print('Testing GEO Audit on rivaledge.ai...')
    audit = await generate_geo_audit(
        url='https://rivaledge.ai',
        company_name='RivalEdge',
        industry='competitive intelligence',
        competitors=['https://www.crayon.co'],
        tier='pro'
    )
    print(f'\n=== RIVALEDGE.AI GEO AUDIT ===')
    print(f'Overall Score: {audit.overall_score}/100 (Grade {audit.grade})')
    print(f'Technical: {audit.technical.score}/40')
    print(f'AI Citations: {audit.ai_citations.score}/30')
    print(f'Competitors: {audit.competitors.score}/20')
    print(f'\nTop Recommendations:')
    for i, rec in enumerate(audit.recommendations[:5], 1):
        print(f'{i}. [{rec["priority"]}] {rec["action"]}')
    
    # Save to file
    import json
    from agents.geo_audit_generator import audit_to_dict
    with open('/tmp/rivaledge_audit.json', 'w') as f:
        json.dump(audit_to_dict(audit), f, indent=2, default=str)
    print('\nSaved to /tmp/rivaledge_audit.json')

asyncio.run(test())
