#!/usr/bin/env python3
"""Convertit content/publications/publis.bib en données consommables par Hugo."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "publications" / "publis.bib"
DESTINATION = ROOT / "data" / "publications.json"


def balanced_chunk(text: str, start: int) -> tuple[str, int]:
    opening = text[start]
    closing = "}" if opening == "{" else '"'
    depth = 0
    escaped = False
    index = start + 1
    while index < len(text):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif opening == "{" and char == "{":
            depth += 1
        elif char == closing:
            if depth == 0:
                return text[start + 1:index], index + 1
            depth -= 1
        index += 1
    raise ValueError("Délimiteur BibTeX non fermé")


def parse_bibtex(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    cursor = 0
    while match := re.search(r"@(\w+)\s*\{", text[cursor:], re.I):
        entry_type = match.group(1).lower()
        start = cursor + match.end() - 1
        body, cursor = balanced_chunk(text, start)
        if "," not in body:
            continue
        key, fields_text = body.split(",", 1)
        entry = {"_type": entry_type, "key": key.strip()}
        position = 0
        while field_match := re.search(r"([\w-]+)\s*=\s*", fields_text[position:], re.I):
            name = field_match.group(1).lower()
            value_start = position + field_match.end()
            while value_start < len(fields_text) and fields_text[value_start].isspace():
                value_start += 1
            if value_start >= len(fields_text):
                break
            if fields_text[value_start] in '{"':
                value, value_end = balanced_chunk(fields_text, value_start)
            else:
                end_match = re.search(r",|\n", fields_text[value_start:])
                value_end = value_start + (end_match.start() if end_match else len(fields_text))
                value = fields_text[value_start:value_end]
            entry[name] = re.sub(r"\s+", " ", value).strip()
            position = value_end
        entries.append(entry)
    return entries


ACCENTS = {
    "'": "\N{COMBINING ACUTE ACCENT}",
    "`": "\N{COMBINING GRAVE ACCENT}",
    '"': "\N{COMBINING DIAERESIS}",
    "^": "\N{COMBINING CIRCUMFLEX ACCENT}",
    "~": "\N{COMBINING TILDE}",
    "c": "\N{COMBINING CEDILLA}",
    "v": "\N{COMBINING CARON}",
    "r": "\N{COMBINING RING ABOVE}",
}


def latex_to_text(value: str) -> str:
    value = value.replace(r"\&", "&").replace(r"\ss", "ß")
    value = re.sub(r"\\url\{([^{}]+)\}", r"\1", value)
    value = re.sub(r"\\([ij])", r"\1", value)

    braced_accent = re.compile(r"\\(['`\"\^~cvr])\s*\{\s*([A-Za-z])\s*\}")
    plain_accent = re.compile(r"\\(['`\"\^~cvr])\s*([A-Za-z])")

    def accent(match: re.Match[str]) -> str:
        return unicodedata.normalize("NFC", match.group(2) + ACCENTS[match.group(1)])

    previous = None
    while value != previous:
        previous = value
        value = braced_accent.sub(accent, value)
        value = plain_accent.sub(accent, value)
        value = re.sub(r"\{([^{}]*)\}", r"\1", value)
    value = value.replace("~", "\N{NO-BREAK SPACE}")
    return re.sub(r"\s+", " ", value).strip()


def format_names(value: str, editors: bool = False) -> str:
    names = []
    for raw_name in re.split(r"\s+and\s+", value):
        parts = [part.strip() for part in raw_name.split(",")]
        if len(parts) >= 2:
            name = f"{parts[1]} {parts[0]}"
        else:
            name = parts[0]
        names.append(latex_to_text(name))
    rendered = ", ".join(names)
    if editors and rendered:
        rendered += ", éd." if len(names) == 1 else ", éds."
    return rendered


def resolve_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    by_key = {entry["key"].lower(): entry for entry in entries}
    resolved = []
    for source in entries:
        entry = dict(source)
        if crossref := source.get("crossref"):
            parent = by_key.get(crossref.lower(), {})
            entry = {**parent, **entry}
        if "lareau" not in entry.get("author", "").lower():
            continue

        entry_type = entry.get("_type", "")
        venue = ""
        if entry_type == "article":
            venue = f"Dans {latex_to_text(entry.get('journal', ''))}"
        elif entry_type in {"inproceedings", "conference"}:
            venue = f"Dans {latex_to_text(entry.get('booktitle', ''))}"
        elif entry_type in {"incollection", "inbook"}:
            venue = f"Chapitre dans {latex_to_text(entry.get('booktitle', ''))}"
        if editor := entry.get("editor"):
            venue += f" ({format_names(editor, editors=True)})"

        publisher = latex_to_text(entry.get("publisher", ""))
        if not publisher and entry_type == "phdthesis":
            publisher = f"Thèse de doctorat, {latex_to_text(entry.get('school', ''))}"
        elif not publisher and entry_type == "mastersthesis":
            publisher = f"Mémoire de maîtrise, {latex_to_text(entry.get('school', ''))}"

        resolved.append({
            "key": source["key"],
            "title": latex_to_text(entry.get("title", "")),
            "authors": format_names(entry.get("author", "")),
            "venue": venue.strip(),
            "publisher": publisher,
            "volume": latex_to_text(entry.get("volume", "")),
            "year": latex_to_text(entry.get("year", "")),
            "note": latex_to_text(entry.get("note", entry.get("notes", ""))),
            "pdf": local_url(entry.get("pdf", "")),
            "poster": local_url(entry.get("poster", "")),
            "url": local_url(entry.get("url", "")),
        })
    return sorted(resolved, key=lambda item: item["year"], reverse=True)


def local_url(value: str) -> str:
    return re.sub(r"^https?://(?:www\.)?flareau\.ca/", "/", value)


def main() -> None:
    publications = resolve_entries(parse_bibtex(SOURCE.read_text(encoding="utf-8")))
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(
        json.dumps(publications, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(publications)} publications écrites dans {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
