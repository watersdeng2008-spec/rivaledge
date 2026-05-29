import asyncio
import sys
sys.path.insert(0, '.')

from agents.geo_audit_generator import (
    check_robots_txt, check_llms_txt, check_sitemap, 
    check_schema_markup, check_crawler_access,
    calculate_technical_score
)

async def test():
    url = 'https://rivaledge.ai'
    print(f'Testing GEO Audit on {url}...\n')
    
    # Run technical checks
    robots = await check_robots_txt(url)
    llms = await check_llms_txt(url)
    sitemap = await check_sitemap(url)
    schema = await check_schema_markup(url)
    crawler = await check_crawler_access(url)
    
    print('=== TECHNICAL AUDIT RESULTS ===')
    print(f'\n1. robots.txt: {"✅ Found" if robots["present"] else "❌ Missing"}')
    if robots["present"]:
        print(f'   URL: {robots["url"]}')
        print(f'   AI Crawlers: {len([v for v in robots["crawler_rules"].values() if v == "allowed"])} allowed')
    if robots["issues"]:
        print(f'   Issues: {robots["issues"]}')
    
    print(f'\n2. llms.txt: {"✅ Found" if llms["present"] else "❌ Missing"}')
    if llms["present"]:
        print(f'   URL: {llms["url"]}')
        print(f'   Sections: {llms["sections"]}')
    if llms["issues"]:
        print(f'   Issues: {llms["issues"]}')
    
    print(f'\n3. Sitemap: {"✅ Found" if sitemap["present"] else "❌ Missing"}')
    if sitemap["present"]:
        print(f'   URL: {sitemap["url"]}')
        print(f'   URLs: {sitemap["url_count"]}')
        print(f'   Last Modified: {sitemap["last_modified"]}')
    if sitemap["issues"]:
        print(f'   Issues: {sitemap["issues"]}')
    
    print(f'\n4. Schema Markup: {"✅ Found" if schema["present"] else "❌ Missing"}')
    if schema["present"]:
        print(f'   Types: {schema["types_found"]}')
    if schema["issues"]:
        print(f'   Issues: {schema["issues"]}')
    
    print(f'\n5. Crawler Access:')
    for crawler_name, result in crawler["results"].items():
        status = "✅" if result == "accessible" else "❌"
        print(f'   {status} {crawler_name}: {result}')
    if crawler["issues"]:
        print(f'   Issues: {crawler["issues"]}')
    
    # Calculate score
    score = calculate_technical_score(robots, llms, sitemap, schema, crawler)
    print(f'\n=== TECHNICAL SCORE: {score}/40 ===')

asyncio.run(test())
