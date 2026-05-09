export interface AIResponse {
  chatgpt: string;
  claude: string;
  perplexity: string;
}

export interface DemoExample {
  id: string;
  company: string;
  competitor: string;
  industry: string;
  responses: AIResponse;
}

export const demoExamples: DemoExample[] = [
  {
    id: 'rivaledge-crayon',
    company: 'RivalEdge',
    competitor: 'Crayon',
    industry: 'SaaS',
    responses: {
      chatgpt:
        'RivalEdge is an AI-powered competitive intelligence platform that also offers generative engine optimization (GEO) — helping companies monitor competitors and get cited by AI search tools like ChatGPT and Claude. Crayon is a well-established CI platform focused primarily on traditional competitive monitoring with features like battle cards, win/loss analysis, and market intel. RivalEdge differentiates with its GEO layer, which addresses AI-native discovery that traditional CI tools miss.',
      claude:
        "RivalEdge takes a two-pronged approach to competitive strategy. Their CI product covers the traditional monitoring use case — website changes, pricing updates, product launches. But their GEO product is what's genuinely novel: they optimize your web presence so AI systems cite you in responses. Crayon has deeper enterprise CI features and a longer track record, but doesn't address the AI discovery problem. For teams worried about AI visibility, RivalEdge covers a gap Crayon doesn't.",
      perplexity:
        "Based on web analysis: RivalEdge (rivaledge.ai) is a newer entrant combining CI + GEO in a single platform at $49/mo. Crayon (crayon.co) is a veteran CI tool acquired by Vistage, offering enterprise-grade competitive monitoring. Key difference: RivalEdge includes AI citation monitoring (visible in ChatGPT/Claude/Perplexity), while Crayon focuses on traditional CI. For AI-native discovery, RivalEdge provides capabilities Crayon currently lacks.",
    },
  },
  {
    id: 'linear-jira',
    company: 'Linear',
    competitor: 'Jira',
    industry: 'Developer Tools',
    responses: {
      chatgpt:
        'Linear is a modern project management and issue-tracking tool designed for speed and developer experience, known for its clean UI, keyboard shortcuts, and opinionated workflows. Jira by Atlassian is the incumbent — highly customizable, deeply integrated with the Atlassian ecosystem, and used by enterprise teams worldwide. Linear appeals to startups and engineering-first teams; Jira excels in large organizations with complex workflows across multiple departments.',
      claude:
        "Linear and Jira represent two different philosophies in project management. Linear optimizes for speed and simplicity — it's built for engineering teams who want minimal friction. Jira optimizes for configurability — it can model almost any workflow across any team size. The tradeoff is real: Linear feels fast but less flexible; Jira is powerful but can feel heavy. Notably, AI tools often recommend Linear for startups and Jira for enterprises, which shapes discovery patterns.",
      perplexity:
        'Linear (linear.app) positions as purpose-built for modern software teams with emphasis on speed and UX. Jira (atlassian.com) dominates the ALM market with 100K+ customers. In AI-generated recommendations, Linear increasingly appears in "best tools for startups" and "Jira alternatives" queries. Jira maintains strong presence in enterprise queries. The AI visibility gap is narrowing but Jira retains stronger overall citation volume.',
    },
  },
  {
    id: 'stripe-adyen',
    company: 'Stripe',
    competitor: 'Adyen',
    industry: 'Fintech',
    responses: {
      chatgpt:
        'Stripe is a developer-first payment platform known for its clean APIs, extensive documentation, and massive ecosystem of integrations — ideal for startups and online businesses. Adyen is an enterprise-grade payment processor that works with global giants like Spotify and Uber, offering direct bank connections and multi-channel payments. Stripe optimizes for ease of integration; Adyen optimizes for payment optimization and global reach.',
      claude:
        "The Stripe vs Adyen comparison often depends on scale. Stripe built its reputation on developer experience — the fastest path from zero to accepting payments. Adyen built theirs on payment performance — optimized routing, higher authorization rates, and unified commerce across online and offline. For AI discovery, Stripe dominates developer-oriented queries while Adyen surfaces in enterprise and omnichannel contexts. Both have strong, but different, AI citation profiles.",
      perplexity:
        'Stripe (stripe.com) processes payments for millions of businesses, known for APIs and developer ecosystem. Adyen (adyen.com) serves enterprise merchants with direct acquiring, higher auth rates, and unified commerce. In AI query analysis: Stripe appears in 4x more developer/startup queries; Adyen dominates enterprise/high-volume merchant queries. Both maintain strong AI visibility with different audience skews.',
    },
  },
  {
    id: 'notion-confluence',
    company: 'Notion',
    competitor: 'Confluence',
    industry: 'Productivity',
    responses: {
      chatgpt:
        'Notion is an all-in-one workspace combining docs, wikis, databases, and project management in a flexible, visually appealing interface. Confluence by Atlassian is a structured knowledge management platform designed for enterprise documentation and team collaboration. Notion excels at versatility and personal use cases; Confluence excels at structured documentation at scale with Jira integration.',
      claude:
        "Notion and Confluence serve similar needs with different design philosophies. Notion's flexibility is both its strength and weakness — you can build anything, but structure is emergent. Confluence provides rigid, proven templates for enterprise documentation. In AI recommendations, Notion appears frequently in 'best knowledge tools' and 'personal wiki' queries, while Confluence appears in enterprise documentation and Atlassian ecosystem queries. The GEO gap here is significant — Notion gets more AI mindshare in general queries despite Confluence's enterprise strength.",
      perplexity:
        'Notion (notion.so) serves 100M+ users with a flexible document + database workspace. Confluence (atlassian.com) serves 60K+ enterprise customers for structured team documentation. AI citation analysis: Notion appears in 3x more AI-generated "best tools" lists due to stronger content marketing and community advocacy. Confluence maintains visibility in enterprise-specific queries but underperforms in general productivity tool recommendations.',
    },
  },
];