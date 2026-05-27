import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const AI_CRAWLERS: Record<string, { name: string; company: string }> = {
  GPTBot: { name: 'OpenAI GPTBot', company: 'OpenAI' },
  ClaudeBot: { name: 'Anthropic ClaudeBot', company: 'Anthropic' },
  PerplexityBot: { name: 'PerplexityBot', company: 'Perplexity' },
  'Google-Extended': { name: 'Google-Extended', company: 'Google' },
  CCBot: { name: 'Common Crawl CCBot', company: 'Common Crawl' },
  'anthropic-ai': { name: 'Anthropic AI', company: 'Anthropic' },
  'OAI-SearchBot': { name: 'OpenAI SearchBot', company: 'OpenAI' },
  'ChatGPT-User': { name: 'OpenAI ChatGPT User', company: 'OpenAI' },
  'Claude-Web': { name: 'Anthropic Claude Web', company: 'Anthropic' },
}

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/admin(.*)',
  '/api/admin(.*)',
  '/demo',
  '/pricing',
  '/geo',
  '/audit',
  '/vs(.*)',
  '/about',
  '/contact',
  '/blog(.*)',
  '/features',
  '/privacy',
  '/terms',
  '/robots.txt',
  '/sitemap.xml',
  '/llms.txt',
])

function detectAICrawler(userAgent: string) {
  for (const [pattern, crawler] of Object.entries(AI_CRAWLERS)) {
    if (userAgent.includes(pattern)) {
      return { ...crawler, pattern }
    }
  }

  return null
}

async function logAICrawlerVisit(request: Request) {
  const userAgent = request.headers.get('user-agent') || ''
  const crawler = detectAICrawler(userAgent)
  const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!crawler || !supabaseUrl || !supabaseKey) {
    return
  }

  const forwardedFor = request.headers.get('x-forwarded-for')
  const ipAddress = forwardedFor?.split(',')[0]?.trim() || request.headers.get('x-real-ip') || 'unknown'

  try {
    await fetch(`${supabaseUrl.replace(/\/$/, '')}/rest/v1/ai_crawler_visits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
      },
      body: JSON.stringify({
        crawler_name: crawler.name,
        crawler_company: crawler.company,
        crawler_pattern: crawler.pattern,
        page_url: request.url,
        ip_address: ipAddress,
        user_agent: userAgent.substring(0, 500),
      }),
    })
  } catch {
    // Crawler analytics must never block page delivery.
  }
}

export default clerkMiddleware(async (auth, request) => {
  await logAICrawlerVisit(request)

  if (!isPublicRoute(request)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jte?|ttf|woff2?|png|jpg|webp|svg|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
