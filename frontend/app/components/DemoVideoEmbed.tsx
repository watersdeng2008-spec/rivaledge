type DemoVideoEmbedProps = {
  eyebrow?: string;
  heading: string;
  className?: string;
};

export default function DemoVideoEmbed({ eyebrow, heading, className = '' }: DemoVideoEmbedProps) {
  return (
    <div className={`mx-auto max-w-4xl text-center ${className}`}>
      {eyebrow && (
        <p className="mb-3 text-sm font-medium uppercase tracking-wide text-blue-300">
          {eyebrow}
        </p>
      )}
      <h2 className="mb-5 text-2xl font-bold text-white md:text-3xl">{heading}</h2>
      <div className="overflow-hidden rounded-xl border border-slate-700 bg-slate-900 shadow-2xl shadow-blue-950/30">
        <div className="relative aspect-video w-full">
          <iframe
            className="absolute inset-0 h-full w-full"
            src="https://www.youtube.com/embed/mUryhXGlWh4"
            title="RivalEdge Demo - Competitive Intelligence Done For You"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
}
