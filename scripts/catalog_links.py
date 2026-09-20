import os
import re

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InvalidSlug(ValueError):
    pass


def resolve_url(tool, affiliate_links):
    slug = tool["id"]
    official = tool["official_url"]
    mapped = affiliate_links.get(slug)
    if mapped:
        return mapped
    return official


def safe_content_path(content_dir, slug):
    if not SLUG_RE.match(slug or ""):
        raise InvalidSlug(slug)
    root = os.path.realpath(content_dir)
    path = os.path.realpath(os.path.join(root, f"{slug}.md"))
    if os.path.commonpath([root, path]) != root:
        raise InvalidSlug(slug)
    return path
