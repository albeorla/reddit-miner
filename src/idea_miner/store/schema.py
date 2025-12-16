"""Database schema for Idea Miner."""

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    created_utc INTEGER NOT NULL,
    score INTEGER NOT NULL,
    num_comments INTEGER NOT NULL,
    url TEXT,
    permalink TEXT,
    top_comments TEXT,  -- JSON array
    fetched_at TEXT NOT NULL,
    processed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    run_id INTEGER,
    cluster_id TEXT,
    
    -- Extraction state
    extraction_state TEXT NOT NULL DEFAULT 'extracted',  -- extracted, not_extractable, disqualified
    not_extractable_reason TEXT,
    
    -- Extraction fields
    idea_summary TEXT NOT NULL,
    target_user TEXT,
    pain_point TEXT,
    proposed_solution TEXT,
    evidence TEXT,  -- JSON array of EvidenceSignal objects with source attribution
    evidence_strength INTEGER DEFAULT 0,
    evidence_strength_reason TEXT,
    risk_flags TEXT,  -- JSON array
    
    -- Legacy field for backward compatibility
    evidence_signals TEXT,  -- JSON array (deprecated, use evidence)
    
    -- Score fields
    disqualified INTEGER DEFAULT 0,
    disqualify_reasons TEXT,  -- JSON array
    practicality INTEGER,
    profitability INTEGER,
    distribution INTEGER,
    competition INTEGER,
    moat INTEGER,
    total_score INTEGER,
    confidence REAL,
    
    -- Enhanced distribution analysis
    distribution_wedge TEXT,  -- ecosystem, partner_channel, seo, influencer_affiliate, community, product_led
    distribution_wedge_detail TEXT,
    
    -- Enhanced competition analysis
    competition_landscape TEXT,  -- JSON array of CompetitorNote objects
    
    -- Reasoning
    why TEXT,  -- JSON array
    next_validation_steps TEXT,  -- JSON array
    
    -- Metadata
    created_at TEXT NOT NULL,
    raw_extraction TEXT,  -- Full JSON
    raw_score TEXT,  -- Full JSON
    
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    subreddits TEXT,  -- JSON array
    posts_fetched INTEGER DEFAULT 0,
    posts_analyzed INTEGER DEFAULT 0,
    ideas_saved INTEGER DEFAULT 0,
    qualified_ideas INTEGER DEFAULT 0,
    not_extractable INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',  -- running, completed, failed
    report_path TEXT
);

CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, processing, completed, failed
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);
CREATE INDEX IF NOT EXISTS idx_posts_processed ON posts(processed);
CREATE INDEX IF NOT EXISTS idx_ideas_post_id ON ideas(post_id);
CREATE INDEX IF NOT EXISTS idx_ideas_run_id ON ideas(run_id);
CREATE INDEX IF NOT EXISTS idx_ideas_total_score ON ideas(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_ideas_disqualified ON ideas(disqualified);
CREATE INDEX IF NOT EXISTS idx_ideas_extraction_state ON ideas(extraction_state);

-- Prevent duplicate ideas for the same post in the same run
CREATE UNIQUE INDEX IF NOT EXISTS idx_ideas_post_run_unique ON ideas(post_id, run_id);
"""
