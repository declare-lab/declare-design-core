#!/usr/bin/env python3
"""Audit and remove style declarations that belong to the shared core."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from lxml import etree, html


TYPOGRAPHY_PROPERTIES = {
    "font",
    "font-family",
    "font-size",
    "font-style",
    "font-variation-settings",
    "font-weight",
    "letter-spacing",
    "line-height",
    "text-transform",
}
DECLARATION = re.compile(r"^(\s*)([-\w]+)\s*:\s*([^;]+);(.*)$")
LITERAL_TYPE = re.compile(
    r"(?:font-size\s*:\s*[-.\d]+(?:px|rem)|font-weight\s*:\s*\d{3})"
)
LITERAL_COLOR = re.compile(
    r"(?<![-\w])(?:#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\))"
)
STYLE_ATTRIBUTE = re.compile(r"\bstyle\s*=\s*([\"'])(.*?)\1", re.DOTALL)
DYNAMIC_STYLE_WRITE = re.compile(
    r"\.style(?:\.|\[)|"
    r"(?:setAttribute|removeAttribute)\(\s*[\"']style[\"']"
)


@dataclass
class Finding:
    file: str
    line: int
    property: str
    value: str


@dataclass
class Report:
    mode: str
    site_root: str
    style_files: int = 0
    style_lines: int = 0
    typography_declarations: int = 0
    typography_by_property: Counter = field(default_factory=Counter)
    typography_findings: list[Finding] = field(default_factory=list)
    literal_typography_lines: int = 0
    literal_color_lines: int = 0
    important_lines: int = 0
    built_html_files: int = 0
    source_content_files: int = 0
    source_inline_style_attributes: int = 0
    source_custom_property_only_styles: int = 0
    source_inline_style_violations: int = 0
    source_dynamic_style_writes: int = 0
    inline_style_attributes: int = 0
    custom_property_only_styles: int = 0
    inline_style_violations: int = 0
    embedded_style_blocks: int = 0
    changed_files: int = 0
    removed_declarations: int = 0

    @property
    def passed(self) -> bool:
        return (
            self.typography_declarations == 0
            and self.literal_typography_lines == 0
            and self.literal_color_lines == 0
            and self.important_lines == 0
            and self.source_inline_style_violations == 0
            and self.source_dynamic_style_writes == 0
            and self.inline_style_violations == 0
            and self.embedded_style_blocks == 0
        )

    def serializable(self) -> dict:
        data = asdict(self)
        data["typography_by_property"] = dict(self.typography_by_property)
        data["passed"] = self.passed
        return data


def style_paths(site_root: Path) -> list[Path]:
    paths = [site_root / "assets/css/style.scss"]
    paths.extend(sorted((site_root / "_sass").glob("*.scss")))
    return [path for path in paths if path.is_file()]


def declaration_for(line: str, in_comment: bool) -> tuple[str, str] | None:
    if in_comment:
        return None
    match = DECLARATION.match(line)
    if not match:
        return None
    return match.group(2).lower(), match.group(3).strip()


def scan_or_fix_styles(site_root: Path, report: Report, fix: bool) -> None:
    for path in style_paths(site_root):
        report.style_files += 1
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        output: list[str] = []
        changed = False
        in_comment = False

        for number, line in enumerate(lines, 1):
            report.style_lines += 1
            was_in_comment = in_comment
            if "/*" in line and "*/" not in line.split("/*", 1)[1]:
                in_comment = True

            declaration = declaration_for(line, was_in_comment)
            if declaration and declaration[0] in TYPOGRAPHY_PROPERTIES:
                prop, value = declaration
                report.typography_declarations += 1
                report.typography_by_property[prop] += 1
                report.typography_findings.append(
                    Finding(
                        file=str(path.relative_to(site_root)),
                        line=number,
                        property=prop,
                        value=value,
                    )
                )
                if fix:
                    report.removed_declarations += 1
                    changed = True
                    if "*/" in line:
                        in_comment = False
                    continue

            if not was_in_comment and LITERAL_TYPE.search(line):
                report.literal_typography_lines += 1
            if not was_in_comment and LITERAL_COLOR.search(line):
                report.literal_color_lines += 1
            if not was_in_comment and "!important" in line:
                report.important_lines += 1

            output.append(line)
            if "*/" in line:
                in_comment = False

        if fix and changed:
            path.write_text("".join(output), encoding="utf-8")
            report.changed_files += 1


def excluded(relative_path: Path, patterns: list[str]) -> bool:
    value = relative_path.as_posix()
    return any(fnmatch.fnmatch(value, pattern) for pattern in patterns)


def source_content_paths(site_root: Path) -> list[Path]:
    paths: list[Path] = []
    for name in ("index.md", "index.html"):
        path = site_root / name
        if path.is_file():
            paths.append(path)
    for directory in ("_pages", "_posts"):
        root = site_root / directory
        if root.is_dir():
            paths.extend(sorted(root.rglob("*.md")))
            paths.extend(sorted(root.rglob("*.html")))
    return paths


def scan_source_content(site_root: Path, report: Report) -> None:
    for path in source_content_paths(site_root):
        report.source_content_files += 1
        content = path.read_text(encoding="utf-8")

        for match in STYLE_ATTRIBUTE.finditer(content):
            report.source_inline_style_attributes += 1
            declarations = [
                part.strip()
                for part in match.group(2).split(";")
                if part.strip()
            ]
            if declarations and all(part.startswith("--") for part in declarations):
                report.source_custom_property_only_styles += 1
            else:
                report.source_inline_style_violations += 1

        report.source_dynamic_style_writes += len(
            DYNAMIC_STYLE_WRITE.findall(content)
        )


def audit_built_site(site_root: Path, built_site: Path, report: Report) -> None:
    contract_path = (
        site_root / "assets/declare-core/config/typography-contract.json"
    )
    patterns: list[str] = []
    if contract_path.is_file():
        patterns = json.loads(contract_path.read_text())["excluded_paths"]

    for path in sorted(built_site.rglob("*.html")):
        relative = path.relative_to(built_site)
        if excluded(relative, patterns):
            continue
        try:
            document = html.fromstring(path.read_text(encoding="utf-8"))
        except (ValueError, etree.ParserError):
            continue

        scopes = document.xpath(
            "//main[contains(concat(' ', normalize-space(@class), ' '),"
            " ' site-main ')]"
        )
        if not scopes:
            continue
        report.built_html_files += 1

        for element in document.xpath("//*[@style]"):
            report.inline_style_attributes += 1
            declarations = [
                part.strip()
                for part in (element.get("style") or "").split(";")
                if part.strip()
            ]
            if declarations and all(part.startswith("--") for part in declarations):
                report.custom_property_only_styles += 1
            else:
                report.inline_style_violations += 1

        report.embedded_style_blocks += len(
            document.xpath("//style[normalize-space(text())]")
        )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("mode", choices=("audit", "fix"))
    result.add_argument("--site-root", type=Path, required=True)
    result.add_argument("--built-site", type=Path)
    result.add_argument("--json", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    site_root = args.site_root.resolve()
    report = Report(mode=args.mode, site_root=str(site_root))
    scan_source_content(site_root, report)
    scan_or_fix_styles(site_root, report, fix=args.mode == "fix")

    if args.mode == "fix":
        verification = Report(mode="audit", site_root=str(site_root))
        scan_or_fix_styles(site_root, verification, fix=False)
        report.typography_declarations = verification.typography_declarations
        report.typography_by_property = verification.typography_by_property
        report.typography_findings = verification.typography_findings
        report.literal_typography_lines = verification.literal_typography_lines

    if args.built_site:
        audit_built_site(site_root, args.built_site.resolve(), report)

    if args.json:
        print(json.dumps(report.serializable(), indent=2, sort_keys=True))
    else:
        print(
            f"Style ownership {args.mode}: {report.style_files} files, "
            f"{report.typography_declarations} local typography declarations, "
            f"{report.literal_color_lines} literal color lines, "
            f"{report.important_lines} !important lines, "
            f"{report.source_inline_style_violations} source inline-style "
            f"violations, {report.source_dynamic_style_writes} dynamic style "
            f"writes, "
            f"{report.inline_style_violations} inline-style violations, "
            f"{report.embedded_style_blocks} embedded style blocks."
        )
        if args.mode == "fix":
            print(
                f"Removed {report.removed_declarations} declarations from "
                f"{report.changed_files} files."
            )
        for finding in report.typography_findings[:20]:
            print(
                f"{finding.file}:{finding.line}: "
                f"{finding.property}: {finding.value}"
            )

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
