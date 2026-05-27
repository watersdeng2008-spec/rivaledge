import { NextResponse } from 'next/server';
import { auth, currentUser } from '@clerk/nextjs/server';

export const dynamic = 'force-dynamic';

interface SupabaseCrawlerVisit {
  id: string;
  crawler_name: string;
  crawler_company: string;
  crawler_pattern: string;
  page_url: string;
  ip_address: string | null;
  user_agent: string | null;
  visited_at: string;
  created_at: string;
}

export async function GET() {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const user = await currentUser();
  const isAdmin = user?.publicMetadata?.role === 'admin';

  if (!isAdmin) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !supabaseKey) {
    return NextResponse.json(
      { error: 'Supabase crawler tracking is not configured.' },
      { status: 500 },
    );
  }

  const response = await fetch(
    `${supabaseUrl.replace(/\/$/, '')}/rest/v1/ai_crawler_visits?select=*&order=visited_at.desc&limit=100`,
    {
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
      },
      cache: 'no-store',
    },
  );

  if (!response.ok) {
    return NextResponse.json(
      { error: 'Unable to load crawler visits.' },
      { status: response.status },
    );
  }

  const visits = (await response.json()) as SupabaseCrawlerVisit[];

  return NextResponse.json({ visits });
}
