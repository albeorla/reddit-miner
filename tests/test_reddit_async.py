import httpx
import pytest
import respx
from pain_radar.reddit_async import RedditPost, _clean_html, _extract_post_id, _parse_rss_entry, fetch_all_subreddits


def test_extract_post_id():
    """Test extracting post ID from various Reddit URLs."""
    url = "https://www.reddit.com/r/SaaS/comments/1ptgval/take_these_with_a_pinch_of_salt/"
    assert _extract_post_id(url) == "1ptgval"
    assert _extract_post_id("https://google.com") == ""


def test_clean_html():
    """Test cleaning HTML content."""
    html_text = "<div>Hello &amp; welcome <p>to the <b>world</b></p></div>"
    cleaned = _clean_html(html_text)
    # The current implementation uses separator=" " in BeautifulSoup which might add extra spaces
    assert "Hello & welcome" in cleaned
    assert "to the" in cleaned
    assert "world" in cleaned


def test_parse_rss_entry():
    """Test parsing an RSS entry into a RedditPost."""
    entry = {
        "link": "https://www.reddit.com/r/test/comments/abc123/title/",
        "title": "Test Title",
        "summary": "<div>Summary content</div>",
        "published_parsed": None,
    }
    post = _parse_rss_entry(entry, "test")
    assert isinstance(post, RedditPost)
    assert post.id == "abc123"
    assert post.title == "Test Title"
    assert post.body == "Summary content"
    assert post.subreddit == "test"


@pytest.mark.asyncio
async def test_fetch_all_subreddits():
    """Test the top-level fetch_all_subreddits function with mocked HTTP."""
    with respx.mock(base_url="https://www.reddit.com") as respx_mock:
        # Mock RSS feed
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>t3_post1</id>
                <link href="https://www.reddit.com/r/test/comments/post1/title/"/>
                <title>Post Title</title>
                <content type="html">&lt;div&gt;Body&lt;/div&gt;</content>
            </entry>
        </feed>"""
        respx_mock.get("/r/test/new.rss").mock(return_value=httpx.Response(200, text=rss_content))

        # Mock JSON for comments
        json_content = [{}, {"data": {"children": [{"kind": "t1", "data": {"body": "Comment 1"}}]}}]
        respx_mock.get("/r/test/comments/post1/title/.json").mock(return_value=httpx.Response(200, json=json_content))

        posts = await fetch_all_subreddits(
            subreddits=["test"], listing="new", limit=1, top_comments=1, max_concurrency=1, user_agent="test-agent"
        )

        assert len(posts) == 1
        assert posts[0].id == "post1"
        assert posts[0].top_comments == ["Comment 1"]
