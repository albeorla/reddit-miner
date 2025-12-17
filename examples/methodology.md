# Pain Radar Methodology

> How we detect, cluster, and report on Reddit pain points

## Overview

Pain Radar is a signal intelligence tool that helps you understand what Redditors are struggling with. This page explains exactly how it works.

## Data Collection

### What we collect

- **Public Reddit posts** via RSS feeds (`reddit.com/r/{subreddit}/new.rss`)
- **Public comments** via JSON endpoints (`reddit.com/comments/{id}.json`)

### What we DON'T collect

- ❌ Private messages
- ❌ User profiles or history
- ❌ Email addresses
- ❌ Any data requiring authentication

## Signal Extraction

Each post is analyzed by AI to extract "pain signals" - expressions of frustration, unmet needs, or failed solutions.

### Signal Types

| Type | Description | Example |
|------|-------------|---------|
| `pain` | Expression of frustration | "I've wasted 3 weeks trying to get this to work" |
| `alternatives` | Solutions that failed | "I tried Zapier, IFTTT, and n8n but none of them..." |
| `willingness_to_pay` | Budget mentions | "I'd pay $50/month for something that actually works" |
| `urgency` | Time pressure | "Need this done by Friday" |
| `repetition` | Multiple voices | Detected when clustering multiple posts |
| `budget` | Specific amounts | "Our budget is $500/month" |

### Filtering

We automatically filter out:

- **Self-promotion posts** - "Check out my new tool!"
- **Celebration posts** - "Finally got my first customer!"
- **Meta discussions** - "Why is this subreddit so quiet?"
- **Generic questions** - "How do I learn to code?"

## Clustering

Individual pain signals are grouped into "Pain Clusters" - themes that appear across multiple posts.

### Clustering Criteria

A cluster must have:
- At least 2 signals pointing to the same pain
- A common target audience
- Quotable evidence

### What makes a good cluster

✅ **Good cluster**: "Shopify checkout fails silently on mobile"
- 5 posts about the same issue
- Specific, actionable
- Clear who it affects

❌ **Bad cluster**: "General frustration with e-commerce"
- Too vague
- Not actionable
- No clear pattern

## Quote Selection

When generating digests, we select quotes that are:

✅ **Emotionally resonant**: "I've wasted 3 weeks on this"
✅ **Specific**: "Every checkout plugin breaks with Shopify 2.0"
✅ **Quotable**: Works in a weekly digest post

We avoid quotes that are:
❌ Generic: "This is frustrating"
❌ Too long
❌ Full of jargon

## Digest Generation

Weekly digests include:

1. **Cluster title** - Catchy description of the pattern
2. **Summary** - One sentence synthesis
3. **Verbatim quotes** - 2-3 best quotes
4. **Who it affects** - Target audience
5. **Source links** - Original threads

## Ethical Guidelines

### What we do

- ✅ Only use public data
- ✅ Cite all sources with links
- ✅ Filter out self-promotion
- ✅ Provide opt-in alerts only
- ✅ Be transparent about methodology

### What we don't do

- ❌ Scrape private data
- ❌ Auto-DM users
- ❌ Spam subreddits
- ❌ Hide our methodology
- ❌ Make up quotes or data

## Questions?

If you have questions about our methodology, please open an issue on GitHub or reach out directly.
