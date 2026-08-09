import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from git import Repo


class GitHubIndexer:
    def __init__(self, token: str = ""):
        self.token = token

    def clone_and_index(self, repo_url: str, branch: str = "main") -> dict:
        clone_url = repo_url
        if self.token and "github.com" in repo_url:
            clone_url = repo_url.replace(
                "https://", f"https://{self.token}@"
            ).replace("github.com", "github.com")

        tmp_dir = tempfile.mkdtemp(prefix="hendrickson_repo_")
        try:
            repo = Repo.clone_from(clone_url, tmp_dir, branch=branch)
            commit_hash = repo.head.commit.hexsha

            files = self._index_files(tmp_dir)
            entities = self._extract_code_entities(files, tmp_dir)

            return {
                "repository": repo_url,
                "branch": branch,
                "commit_hash": commit_hash,
                "affected_files": files,
                "entities": entities,
            }
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def analyze_diff(self, repo_url: str, base_branch: str, target_branch: str) -> dict:
        clone_url = repo_url
        if self.token and "github.com" in repo_url:
            clone_url = repo_url.replace(
                "https://", f"https://{self.token}@"
            ).replace("github.com", "github.com")

        tmp_dir = tempfile.mkdtemp(prefix="hendrickson_diff_")
        try:
            repo = Repo.clone_from(clone_url, tmp_dir)
            diff_index = repo.commit(base_branch).diff(repo.commit(target_branch))
            changed_files = [d.b_path or d.a_path for d in diff_index]

            return {
                "base_branch": base_branch,
                "target_branch": target_branch,
                "changed_files": changed_files,
                "diff_summary": str(diff_index)[:5000],
            }
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _index_files(self, root_dir: str) -> list[str]:
        extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rs", ".rb"}
        files = []
        for path in Path(root_dir).rglob("*"):
            if path.suffix in extensions and path.is_file():
                rel_path = str(path.relative_to(root_dir))
                if "node_modules" not in rel_path and ".git" not in rel_path:
                    files.append(rel_path)
        return files

    def _extract_code_entities(self, files: list[str], root_dir: str) -> list[dict]:
        entities = []
        for file_path in files:
            full_path = Path(root_dir) / file_path
            try:
                content = full_path.read_text(encoding="utf-8")
                ext = Path(file_path).suffix
                parsed = self._parse_file_entities(content, file_path, ext)
                entities.extend(parsed)
            except Exception:
                continue
        return entities

    def _parse_file_entities(self, content: str, file_path: str, ext: str) -> list[dict]:
        entities = []
        lines = content.split("\n")

        if ext == ".py":
            entities = self._parse_python_entities(lines, file_path)
        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            entities = self._parse_ts_entities(lines, file_path)
        elif ext == ".go":
            entities = self._parse_go_entities(lines, file_path)

        return entities

    def _parse_python_entities(self, lines: list[str], file_path: str) -> list[dict]:
        import re
        entities = []
        func_pattern = re.compile(r"^\s*(async\s+)?def\s+(\w+)\s*\(")
        class_pattern = re.compile(r"^\s*class\s+(\w+)")
        import_pattern = re.compile(r"^\s*(from\s+(\S+)\s+)?import\s+(.+)")

        for i, line in enumerate(lines):
            func_match = func_pattern.match(line)
            if func_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "function",
                    "name": func_match.group(2),
                    "signature": line.strip(),
                    "line": i + 1,
                })

            class_match = class_pattern.match(line)
            if class_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "class",
                    "name": class_match.group(1),
                    "signature": line.strip(),
                    "line": i + 1,
                })

        return entities

    def _parse_ts_entities(self, lines: list[str], file_path: str) -> list[dict]:
        import re
        entities = []
        func_pattern = re.compile(
            r"^\s*(export\s+)?(async\s+)?function\s+(\w+)\s*[\(<]"
        )
        arrow_pattern = re.compile(
            r"^\s*(export\s+)?(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\([^)]*\)\s*=>"
        )
        class_pattern = re.compile(r"^\s*(export\s+)?class\s+(\w+)")

        for i, line in enumerate(lines):
            func_match = func_pattern.match(line)
            if func_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "function",
                    "name": func_match.group(3),
                    "signature": line.strip(),
                    "line": i + 1,
                })

            arrow_match = arrow_pattern.match(line)
            if arrow_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "function",
                    "name": arrow_match.group(3),
                    "signature": line.strip(),
                    "line": i + 1,
                })

            class_match = class_pattern.match(line)
            if class_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "class",
                    "name": class_match.group(2),
                    "signature": line.strip(),
                    "line": i + 1,
                })

        return entities

    def _parse_go_entities(self, lines: list[str], file_path: str) -> list[dict]:
        import re
        entities = []
        func_pattern = re.compile(r"^\s*func\s+(\([^)]*\)\s+)?(\w+)\s*\(")
        type_pattern = re.compile(r"^\s*type\s+(\w+)\s+struct")

        for i, line in enumerate(lines):
            func_match = func_pattern.match(line)
            if func_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "function",
                    "name": func_match.group(2),
                    "signature": line.strip(),
                    "line": i + 1,
                })

            type_match = type_pattern.match(line)
            if type_match:
                entities.append({
                    "file_path": file_path,
                    "entity_type": "struct",
                    "name": type_match.group(1),
                    "signature": line.strip(),
                    "line": i + 1,
                })

        return entities
