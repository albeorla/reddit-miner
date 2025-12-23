import httpx
import pytest
import respx

from pain_radar.reddit_async import RedditPost, fetch_more_comments


@pytest.mark.asyncio
async def test_fetch_more_comments():
    post = RedditPost(
        id="post1",
        subreddit="test",
        title="Title",
        body="Body",
        created_utc=0,
        score=0,
        num_comments=0,
        url="https://www.reddit.com/r/test/comments/post1/title/",
        permalink="/r/test/comments/post1/title/",
    )

    with respx.mock(base_url="https://www.reddit.com") as respx_mock:
        # Mock JSON for comments - skip first 2, get next 2
        json_content = [
            {},
            {
                "data": {
                    "children": [
                        {"kind": "t1", "data": {"body": "Comment 1"}},
                        {"kind": "t1", "data": {"body": "Comment 2"}},
                        {"kind": "t1", "data": {"body": "Comment 3"}},
                        {"kind": "t1", "data": {"body": "Comment 4"}},
                    ]
                }
            },
        ]
        respx_mock.get("/r/test/comments/post1/title/.json").mock(return_value=httpx.Response(200, json=json_content))

        async with httpx.AsyncClient() as client:
            comments = await fetch_more_comments(client, post, start_index=2, limit=2)

        assert len(comments) == 2
        assert comments[0] == "Comment 3"
        assert comments[1] == "Comment 4"


@pytest.mark.asyncio
async def test_search_related_posts():
    with respx.mock(base_url="https://www.reddit.com") as respx_mock:
        # Mock search RSS
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>t3_post2</id>
                <link href="https://www.reddit.com/r/test/comments/post2/related/"/>
                <title>Related Post</title>
                <content type="html">&lt;div&gt;Related Body&lt;/div&gt;</content>
            </entry>
        </feed>"""
        respx_mock.get("/r/test/search.rss").mock(return_value=httpx.Response(200, text=rss_content))

        from pain_radar.reddit_async import search_related_posts

        async with httpx.AsyncClient() as client:
            posts = await search_related_posts(client, subreddit="test", query="relevant", limit=1)

        assert len(posts) == 1
        assert posts[0].id == "post2"
        assert posts[0].title == "Related Post"
