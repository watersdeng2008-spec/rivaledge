import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import Script from 'next/script';
import { PHProvider } from './providers';
import PostHogPageLeave from '@/components/PostHogPageLeave';
import './globals.css';

const SCHEMA_JSON = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://www.rivaledge.ai/#website",
      "url": "https://www.rivaledge.ai",
      "name": "RivalEdge",
      "description": "AI-native competitive intelligence and GEO platform",
      "publisher": {
        "@id": "https://www.rivaledge.ai/#organization"
      }
    },
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
      "description": "AI-native competitive intelligence and GEO platform. Track competitors, win AI visibility, and move faster than your market. Starting at $49/month.",
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
        },
        {
          "@type": "Offer",
          "name": "GEO Self-Service",
          "price": "299",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock"
        },
        {
          "@type": "Offer",
          "name": "GEO Managed",
          "price": "999",
          "priceCurrency": "USD",
          "availability": "https://schema.org/InStock"
        }
      ],
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "127"
      }
    },
    {
      "@type": "FAQPage",
      "@id": "https://www.rivaledge.ai/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is RivalEdge?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "RivalEdge is an AI-native competitive intelligence and market visibility platform. We help B2B companies track competitors, monitor AI citations, and optimize for Generative Engine Optimization (GEO)."
          }
        },
        {
          "@type": "Question",
          "name": "What is the difference between SEO and GEO?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "SEO optimizes for Google search rankings. GEO (Generative Engine Optimization) optimizes for AI model citations — when ChatGPT, Claude, or Perplexity recommend brands in response to user questions. Different signals, different strategies."
          }
        },
        {
          "@type": "Question",
          "name": "How much does RivalEdge cost?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "RivalEdge Solo starts at $49/month for up to 3 competitors with weekly AI digests. Pro is $99/month for up to 10 competitors with daily digests. GEO Self-Service is $299/month and includes AI visibility tools. GEO Managed is $999/month with done-for-you GEO services."
          }
        },
        {
          "@type": "Question",
          "name": "Does RivalEdge have a free trial?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. RivalEdge Solo and Pro offer a 14-day free trial with no credit card required. GEO Self-Service and Enterprise do not include a trial."
          }
        },
        {
          "@type": "Question",
          "name": "What is Generative Engine Optimization (GEO)?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "GEO is the practice of optimizing your brand's visibility in AI-generated responses. It includes creating llms.txt files, optimizing robots.txt for AI crawlers, implementing schema markup, and monitoring how often ChatGPT, Claude, and Perplexity cite your brand."
          }
        }
      ]
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
  other: {
    'msvalidate.01': '52069F992AB64725EFBBDF0DC42CC5ED',
  },
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
          <PostHogPageLeave />
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
