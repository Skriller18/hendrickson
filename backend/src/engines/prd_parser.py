import re
import uuid
from pathlib import Path
from typing import Optional

from markdown_it import MarkdownIt


class PRDParser:
    def __init__(self):
        self.md = MarkdownIt()

    def parse_file(self, file_path: str) -> list[dict]:
        path = Path(file_path)
        if path.suffix == ".md":
            return self._parse_markdown(path)
        elif path.suffix == ".pdf":
            return self._parse_pdf(path)
        else:
            return self._parse_text(path)

    def parse_text(self, content: str, source_name: str = "inline") -> list[dict]:
        return self._extract_requirements(content, source_name)

    def _parse_markdown(self, path: Path) -> list[dict]:
        content = path.read_text(encoding="utf-8")
        return self._extract_requirements(content, path.name)

    def _parse_pdf(self, path: Path) -> list[dict]:
        from PyPDF2 import PdfReader

        reader = PdfReader(str(path))
        content = "\n".join(page.extract_text() or "" for page in reader.pages)
        return self._extract_requirements(content, path.name)

    def _parse_text(self, path: Path) -> list[dict]:
        content = path.read_text(encoding="utf-8")
        return self._extract_requirements(content, path.name)

    def _extract_requirements(self, content: str, source_name: str) -> list[dict]:
        requirements = []
        lines = content.split("\n")

        heading_pattern = re.compile(r"^#{1,4}\s+(.+)")
        list_pattern = re.compile(r"^[\s]*[-*+]\s+(.+)")
        numbered_pattern = re.compile(r"^[\s]*\d+[\.\)]\s+(.+)")
        tag_pattern = re.compile(r"@req-[\w-]+")

        current_heading = ""
        current_section = ""
        line_number = 0

        for line in lines:
            line_number += 1
            stripped = line.strip()

            heading_match = heading_pattern.match(line)
            if heading_match:
                current_heading = heading_match.group(1).strip()
                current_section = current_heading
                continue

            list_match = list_pattern.match(line) or numbered_pattern.match(line)
            if list_match and len(stripped) > 10:
                item_text = list_match.group(1).strip()
                tags = tag_pattern.findall(item_text)
                if tags or self._is_requirement_like(item_text, current_heading):
                    tag = tags[0] if tags else self._generate_tag(current_section, len(requirements))
                    requirements.append({
                        "tag": tag,
                        "description": item_text,
                        "acceptance_criteria": [],
                        "source_document": source_name,
                        "source_line": line_number,
                        "section": current_section,
                    })

            if tag_pattern.search(stripped) and not list_match:
                tags = tag_pattern.findall(stripped)
                for tag in tags:
                    requirements.append({
                        "tag": tag,
                        "description": stripped,
                        "acceptance_criteria": [],
                        "source_document": source_name,
                        "source_line": line_number,
                        "section": current_section,
                    })

        if not requirements:
            requirements = self._fallback_extract(content, source_name)

        return requirements

    def _is_requirement_like(self, text: str, heading: str) -> bool:
        indicators = [
            "must", "shall", "should", "required", "need to",
            "verify", "validate", "ensure", "support", "handle",
            "acceptance criteria", "user story", "edge case",
        ]
        text_lower = text.lower()
        heading_lower = heading.lower()
        return any(
            ind in text_lower or ind in heading_lower for ind in indicators
        )

    def _generate_tag(self, section: str, index: int) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")[:20]
        return f"@req-{slug}-{index + 1:02d}"

    def _fallback_extract(self, content: str, source_name: str) -> list[dict]:
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 40]
        return [
            {
                "tag": f"@req-auto-{i + 1:03d}",
                "description": p[:200],
                "acceptance_criteria": [],
                "source_document": source_name,
                "source_line": 0,
                "section": "Auto-extracted",
            }
            for i, p in enumerate(paragraphs[:50])
        ]
