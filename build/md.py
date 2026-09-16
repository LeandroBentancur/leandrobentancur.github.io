"""Deliberately tiny Markdown: paragraphs, *emphasis*, **strong**, [links](url).
That is all academic prose needs here, and it keeps CI to two dependencies.
If a page ever needs lists or footnotes, pipe that file through pandoc instead."""
import html
import re


def render(text):
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        s = html.escape(" ".join(block.split()))
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        out.append(f"<p>{s}</p>")
    return "\n".join(out)
