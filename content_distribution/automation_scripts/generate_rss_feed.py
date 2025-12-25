#!/usr/bin/env python3
"""
RSS Feed Generator for UR Trading Expert Blog
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_rss_feed():
    """Generate RSS feed from blog posts"""

    blog_dir = Path("blog")
    rss_template_path = Path("content_distribution/rss_template.xml")

    # Collect all blog posts
    posts = []
    for category_dir in blog_dir.iterdir():
        if category_dir.is_dir():
            for md_file in category_dir.glob("*.md"):
                # Parse frontmatter and content
                post_data = parse_markdown_file(md_file)
                if post_data:
                    posts.append(post_data)

    # Sort by date (newest first)
    posts.sort(key=lambda x: x.get('date', datetime.now()), reverse=True)

    # Generate RSS XML
    rss_content = generate_rss_xml(posts, rss_template_path)

    # Save RSS feed
    rss_path = Path("static/feed.xml")
    rss_path.parent.mkdir(exist_ok=True)

    with open(rss_path, 'w', encoding='utf-8') as f:
        f.write(rss_content)

    print(f"Generated RSS feed with {len(posts)} posts")

def parse_markdown_file(filepath):
    """Parse markdown file with frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple frontmatter parsing (between --- markers)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body = parts[2]

                # Parse frontmatter as simple key-value
                frontmatter = {}
                for line in frontmatter_text.strip().split('
'):
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        frontmatter[key.strip()] = value.strip()

                return {
                    'title': frontmatter.get('title', '').strip('"'),
                    'description': frontmatter.get('description', '').strip('"'),
                    'slug': frontmatter.get('slug', ''),
                    'date': datetime.now(),  # Would parse actual date
                    'category': frontmatter.get('categories', ''),
                    'tags': frontmatter.get('tags', '[]'),
                    'content': body.strip()
                }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")

    return None

def generate_rss_xml(posts, template_path):
    """Generate RSS XML from template and posts"""
    # Simple template replacement (would use Jinja2 in production)
    rss_content = '<?xml version="1.0" encoding="UTF-8"?>
'
    rss_content += '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
'
    rss_content += '    <channel>
'
    rss_content += '        <title>UR Trading Expert Blog</title>
'
    rss_content += '        <description>Professional trading signals, market analysis, and educational content</description>
'
    rss_content += '        <link>https://urtradingexpert.com/blog</link>
'
    rss_content += '        <atom:link href="https://urtradingexpert.com/feed.xml" rel="self" type="application/rss+xml"/>
'
    rss_content += '        <language>en-us</language>
'
    rss_content += '        <lastBuildDate>' + datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT') + '</lastBuildDate>
'
    rss_content += '        <generator>UR Trading Expert Bot</generator>
'

    for post in posts[:20]:  # Limit to 20 most recent posts
        rss_content += '        <item>
'
        rss_content += f'            <title>{post["title"]}</title>
'
        rss_content += f'            <description>{post["description"]}</description>
'
        rss_content += f'            <link>https://urtradingexpert.com/blog/{post["slug"]}</link>
'
        rss_content += f'            <guid>https://urtradingexpert.com/blog/{post["slug"]}</guid>
'
        rss_content += f'            <pubDate>{post["date"].strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
'
        rss_content += '            <author>UR Trading Expert Team</author>
'
        rss_content += f'            <category>{post["category"]}</category>
'
        rss_content += '        </item>
'

    rss_content += '    </channel>
'
    rss_content += '</rss>
'

    return rss_content

if __name__ == "__main__":
    generate_rss_feed()
