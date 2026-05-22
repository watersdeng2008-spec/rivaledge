import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import Script from 'next/script';
import { PHProvider } from './providers';
import './globals.css';

const SCHEMA_JSON = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://www.rivaledge.ai/#organization",
      "name": "RivalEdge.ai",
      "alternateName": "RivalEdge",
      "url": "https://www.rivaledge.ai",
      "logo": "https://www.rivaledge.ai/logo.jpg",
      "sameAs": [
        "https://www.linkedin.com/company/rivaledge",
        "https://twitter.com/RivalEdgeAI"
      ],
      "founder": {
        "@type": "Person",
        "name": "Waters Deng",
        "jobTitle": "Founder"
      },
      "foundingDate": "2025",
      "description": "AI-powered competitive intelligence platform that monitors competitors 24/7 and delivers weekly AI-generated briefings. Starting at $49/month.",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Chicago",
        "addressRegion": "IL",
        "addressCountry": "US"
      }
    },
    {
      "@type": "SoftwareApplication",
      "name": "RivalEdge",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Web",
      "offers": [
        {
          "@type": "Offer",
          "name": "Solo",
          "price": "49",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock"
        },
        {
          "@type": "Offer",
          "name": "Pro",
          "price": "99",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock"
        }
      ],
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "127"
      }
    }
  ]
};

const inter = Inter({ subsets: ['latin'] });

const GOOGLE_ADS_ID = process.env.NEXT_PUBLIC_GOOGLE_ADS_ID || 'AW-18049491672';
const GA_ID = process.env.NEXT_PUBLIC_GA_ID || '';
const GOOGLE_TAG_IDS = Array.from(new Set([GOOGLE_ADS_ID, GA_ID].filter(Boolean)));
const PRIMARY_GOOGLE_TAG_ID = GOOGLE_TAG_IDS[0] || '';

export const metadata: Metadata = {
  title: 'RivalEdge — Win Visibility in Both Markets and AI',
  description: 'Competitor monitoring from $49/mo. AI search visibility from $999/mo. Competitive intelligence + generative engine optimization in one platform.',
  keywords: ['competitor monitoring', 'competitive intelligence', 'AI competitor tracking', 'generative engine optimization', 'GEO', 'AI search optimization', 'LLM optimization', 'AI visibility', 'ChatGPT citations', 'Perplexity optimization', 'Crayon alternative'],
  authors: [{ name: 'RivalEdge' }],
  metadataBase: new URL('https://www.rivaledge.ai'),
  icons: {
    icon: '/logo.jpg',
    apple: '/logo.jpg',
  },
  openGraph: {
    title: 'RivalEdge — Win Visibility in Both Markets and AI',
    description: 'Competitor monitoring from $49/mo. AI search visibility from $999/mo. Competitive intelligence + generative engine optimization.',
    url: 'https://www.rivaledge.ai',
    siteName: 'RivalEdge',
    images: [{ url: '/hero.jpg', width: 1200, height: 630, alt: 'RivalEdge — CI + GEO Platform' }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RivalEdge — Win Visibility in Both Markets and AI',
    description: 'Competitor monitoring from $49/mo. AI visibility from $999/mo.',
    images: ['/hero.jpg'],
    creator: '@RivalEdgeAI',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={`${inter.className} bg-slate-950 text-white antialiased`}>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(SCHEMA_JSON) }}
          />
      <PHProvider>
          {children}
      </PHProvider>

          {/* Google tag for Google Ads and Analytics */}
          {PRIMARY_GOOGLE_TAG_ID && (
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${PRIMARY_GOOGLE_TAG_ID}`}
              strategy="afterInteractive"
            />
          )}
          {PRIMARY_GOOGLE_TAG_ID && (
            <Script
              id="google-tag"
              strategy="afterInteractive"
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  ${GOOGLE_TAG_IDS.map((id) => `gtag('config', '${id}');`).join('\n                  ')}
                `,
              }}
            />
          )}
        </body>
      </html>
    </ClerkProvider>
  );
}
