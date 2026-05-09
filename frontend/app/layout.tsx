import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import Script from 'next/script';
import { PHProvider } from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

const GA_ID = process.env.NEXT_PUBLIC_GA_ID || '';

export const metadata: Metadata = {
  title: 'RivalEdge — Win Visibility in Both Markets and AI',
  description: 'Know your competition. Get cited by AI. Competitive intelligence + generative engine optimization in one platform. From $49/mo.',
  keywords: ['competitor monitoring', 'competitive intelligence', 'AI competitor tracking', 'generative engine optimization', 'GEO', 'AI search optimization', 'LLM optimization', 'AI visibility', 'ChatGPT citations', 'Perplexity optimization', 'Crayon alternative'],
  authors: [{ name: 'RivalEdge' }],
  metadataBase: new URL('https://www.rivaledge.ai'),
  icons: {
    icon: '/logo.jpg',
    apple: '/logo.jpg',
  },
  openGraph: {
    title: 'RivalEdge — Win Visibility in Both Markets and AI',
    description: 'Know your competition. Get cited by AI. Competitive intelligence + generative engine optimization. From $49/mo.',
    url: 'https://www.rivaledge.ai',
    siteName: 'RivalEdge',
    images: [{ url: '/hero.jpg', width: 1200, height: 630, alt: 'RivalEdge — CI + GEO Platform' }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RivalEdge — Win Visibility in Both Markets and AI',
    description: 'Know your competition. Get cited by AI. $49/month.',
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
      <PHProvider>
          {children}
      </PHProvider>

          {/* Google Analytics — lazyOnload to avoid appendChild crash */}
          {GA_ID && (
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
              strategy="lazyOnload"
            />
          )}
        </body>
      </html>
    </ClerkProvider>
  );
}
