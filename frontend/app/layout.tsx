import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import Script from 'next/script';
import { PHProvider } from './providers';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

const GA_ID = process.env.NEXT_PUBLIC_GA_ID || '';

export const metadata: Metadata = {
  title: 'RivalEdge — AI Competitor Monitoring',
  description: 'Track your rivals. Get weekly AI briefings on what competitors changed — pricing, features, messaging. $49/month. 14-day free trial.',
  keywords: ['competitor monitoring', 'competitive intelligence', 'AI competitor tracking', 'rival tracking', 'competitor analysis tool', 'Crayon alternative'],
  authors: [{ name: 'RivalEdge' }],
  metadataBase: new URL('https://www.rivaledge.ai'),
  icons: {
    icon: '/logo.jpg',
    apple: '/logo.jpg',
  },
  openGraph: {
    title: 'RivalEdge — AI Competitor Monitoring',
    description: 'Finally. Competitive intelligence that doesn\'t cost $30k/year. Track your rivals automatically. $49/mo.',
    url: 'https://www.rivaledge.ai',
    siteName: 'RivalEdge',
    images: [{ url: '/hero.jpg', width: 1200, height: 630, alt: 'RivalEdge AI Competitor Monitoring' }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RivalEdge — AI Competitor Monitoring',
    description: 'Track your rivals. Get weekly AI briefings. $49/month.',
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
