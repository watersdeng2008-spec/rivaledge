import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'RivalEdge — AI Competitor Monitoring',
  description: 'Track your rivals. Get weekly AI briefings. $49/month.',
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
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
