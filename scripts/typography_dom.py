#!/usr/bin/env python3
"""Apply and verify DeCLaRe's semantic typography contract in built HTML."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from lxml import etree, html
except ImportError as exc:  # pragma: no cover - exercised by CI setup failure
    raise SystemExit(
        "typography_dom.py requires lxml; install requirements.txt first"
    ) from exc


ROLE_ATTRIBUTE = "data-type-role"
CONTRACT_ATTRIBUTE = "data-type-contract"
IGNORED_TEXT_ANCESTORS = frozenset(
    {"script", "style", "svg", "template", "noscript", "title"}
)


@dataclass
class Audit:
    files: int = 0
    changed_files: int = 0
    assigned_roles: int = 0
    stripped_inline_properties: int = 0
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fix or verify semantic typography roles in a generated website."
        )
    )
    parser.add_argument("mode", choices=("fix", "verify"))
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config"
        / "typography-contract.json",
    )
    return parser.parse_args()


def load_contract(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        contract = json.load(stream)

    required = {"version", "scope_xpath", "roles", "excluded_paths"}
    missing = sorted(required.difference(contract))
    if missing:
        raise SystemExit(f"Typography contract is missing: {', '.join(missing)}")
    return contract


def is_excluded(relative_path: Path, patterns: Iterable[str]) -> bool:
    posix_path = relative_path.as_posix()
    return any(fnmatch.fnmatch(posix_path, pattern) for pattern in patterns)


def html_files(site: Path, patterns: Iterable[str]) -> list[Path]:
    return [
        path
        for path in sorted(site.rglob("*.html"))
        if not is_excluded(path.relative_to(site), patterns)
    ]


def direct_text(element: etree._Element) -> str:
    parts = [element.text or ""]
    parts.extend(child.tail or "" for child in element)
    return " ".join(" ".join(parts).split())


def has_ignored_ancestor(element: etree._Element, scope: etree._Element) -> bool:
    current: etree._Element | None = element
    while current is not None and current is not scope:
        if isinstance(current.tag, str) and current.tag.lower() in IGNORED_TEXT_ANCESTORS:
            return True
        current = current.getparent()
    return False


def has_role_ancestor(
    element: etree._Element,
    scope: etree._Element,
    roles: dict[etree._Element, str],
) -> bool:
    current: etree._Element | None = element
    while current is not None:
        if current in roles:
            return True
        if current is scope:
            return False
        current = current.getparent()
    return False


def fallback_role(element: etree._Element, scope: etree._Element) -> str:
    current: etree._Element | None = element
    while current is not None and current is not scope:
        tag = current.tag.lower() if isinstance(current.tag, str) else ""
        if tag in {"button", "input", "select", "textarea"}:
            return "control"
        if tag == "a":
            return "control"
        current = current.getparent()
    return "body"


def expected_roles(
    document: etree._ElementTree, contract: dict
) -> tuple[
    list[etree._Element],
    dict[etree._Element, str],
    list[etree._Element],
]:
    scopes = document.xpath(contract["scope_xpath"])
    roles: dict[etree._Element, str] = {}
    fallback_elements: list[etree._Element] = []

    for scope in scopes:
        for rule in contract["roles"]:
            for element in scope.xpath(rule["xpath"]):
                if isinstance(element, etree._Element):
                    roles[element] = rule["name"]

        for element in scope.iter():
            if not isinstance(element.tag, str):
                continue
            if has_ignored_ancestor(element, scope) or not direct_text(element):
                continue
            if not has_role_ancestor(element, scope, roles):
                roles[element] = fallback_role(element, scope)
                fallback_elements.append(element)

    return scopes, roles, fallback_elements


def fallback_errors(
    relative_path: Path, elements: list[etree._Element]
) -> list[str]:
    errors: list[str] = []
    for element in elements:
        text = " ".join(element.text_content().split())[:72]
        class_name = element.get("class")
        selector_hint = f".{class_name.split()[0]}" if class_name else element.tag
        errors.append(
            f"{relative_path}: unclassified text at {selector_hint}: {text}"
        )
    return errors


def strip_inline_typography(
    element: etree._Element, forbidden: set[str]
) -> tuple[int, bool]:
    style = element.get("style")
    if not style:
        return 0, False

    kept: list[str] = []
    removed = 0
    for declaration in style.split(";"):
        declaration = declaration.strip()
        if not declaration:
            continue
        if ":" not in declaration:
            kept.append(declaration)
            continue
        property_name = declaration.split(":", 1)[0].strip().lower()
        if property_name in forbidden:
            removed += 1
        else:
            kept.append(declaration)

    if not removed:
        return 0, False
    if kept:
        element.set("style", "; ".join(kept))
    else:
        element.attrib.pop("style", None)
    return removed, True


def heading_errors(
    relative_path: Path, scopes: list[etree._Element]
) -> list[str]:
    errors: list[str] = []
    for scope in scopes:
        headings = scope.xpath(".//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6")
        h1_headings = [heading for heading in headings if heading.tag == "h1"]
        if len(h1_headings) != 1:
            errors.append(
                f"{relative_path}: expected exactly one h1, found {len(h1_headings)}"
            )
        if headings and headings[0].tag != "h1":
            text = " ".join(headings[0].text_content().split())[:72]
            errors.append(
                f"{relative_path}: first heading is {headings[0].tag}, not h1: {text}"
            )
        for heading in headings:
            if not " ".join(heading.text_content().split()):
                errors.append(f"{relative_path}: empty <{heading.tag}> heading")

        previous = 0
        for heading in headings:
            level = int(heading.tag[1])
            if previous and level > previous + 1:
                text = " ".join(heading.text_content().split())[:72]
                errors.append(
                    f"{relative_path}: heading jumps h{previous} -> h{level}: {text}"
                )
            previous = level
    return errors


def parse_document(path: Path) -> etree._ElementTree:
    parser = html.HTMLParser(encoding="utf-8", remove_comments=False)
    return html.parse(str(path), parser=parser)


def serialize_document(document: etree._ElementTree, path: Path) -> None:
    doctype = document.docinfo.doctype or "<!doctype html>"
    output = html.tostring(
        document.getroot(),
        encoding="unicode",
        method="html",
        doctype=doctype,
    )
    path.write_text(output + "\n", encoding="utf-8")


def fix_file(
    path: Path, relative_path: Path, contract: dict, audit: Audit
) -> None:
    document = parse_document(path)
    scopes, roles, fallback_elements = expected_roles(document, contract)
    forbidden = set(contract["inline_typography_properties"])
    changed = False

    for scope in scopes:
        for element in scope.xpath(f".//*[@{ROLE_ATTRIBUTE}] | self::*[@{ROLE_ATTRIBUTE}]"):
            element.attrib.pop(ROLE_ATTRIBUTE, None)
            changed = True

    for element, role in roles.items():
        if element.get(ROLE_ATTRIBUTE) != role:
            element.set(ROLE_ATTRIBUTE, role)
            changed = True
            audit.assigned_roles += 1

    for scope in scopes:
        scope.set(CONTRACT_ATTRIBUTE, contract["version"])
        for element in scope.iter():
            removed, element_changed = strip_inline_typography(element, forbidden)
            audit.stripped_inline_properties += removed
            changed = changed or element_changed

    if changed:
        serialize_document(document, path)
        audit.changed_files += 1

    audit.errors.extend(heading_errors(relative_path, scopes))
    if contract.get("reject_fallback"):
        audit.errors.extend(fallback_errors(relative_path, fallback_elements))


def verify_file(
    path: Path, relative_path: Path, contract: dict, audit: Audit
) -> None:
    document = parse_document(path)
    scopes, roles, fallback_elements = expected_roles(document, contract)
    valid_roles = {rule["name"] for rule in contract["roles"]}
    forbidden = set(contract["inline_typography_properties"])

    if not scopes:
        audit.errors.append(f"{relative_path}: no site-main typography scope")
        return

    for scope in scopes:
        if scope.get(CONTRACT_ATTRIBUTE) != contract["version"]:
            audit.errors.append(
                f"{relative_path}: contract marker is missing or stale"
            )
        for element in scope.iter():
            actual = element.get(ROLE_ATTRIBUTE)
            if actual and actual not in valid_roles:
                audit.errors.append(
                    f"{relative_path}: unknown typography role {actual!r}"
                )
            style = element.get("style") or ""
            for match in re.finditer(r"(?:^|;)\s*([\w-]+)\s*:", style):
                if match.group(1).lower() in forbidden:
                    audit.errors.append(
                        f"{relative_path}: inline typography on <{element.tag}>"
                    )

    for element, expected in roles.items():
        actual = element.get(ROLE_ATTRIBUTE)
        if actual != expected:
            text = " ".join(element.text_content().split())[:72]
            audit.errors.append(
                f"{relative_path}: <{element.tag}> expected {expected!r}, "
                f"found {actual!r}: {text}"
            )

    audit.errors.extend(heading_errors(relative_path, scopes))
    if contract.get("reject_fallback"):
        audit.errors.extend(fallback_errors(relative_path, fallback_elements))


def main() -> int:
    args = parse_args()
    site = args.site.resolve()
    contract = load_contract(args.contract.resolve())
    audit = Audit()

    if not site.is_dir():
        raise SystemExit(f"Site directory does not exist: {site}")

    files = html_files(site, contract["excluded_paths"])
    for path in files:
        relative_path = path.relative_to(site)
        audit.files += 1
        if args.mode == "fix":
            fix_file(path, relative_path, contract, audit)
        else:
            verify_file(path, relative_path, contract, audit)

    if audit.errors:
        for error in audit.errors:
            print(error, file=sys.stderr)
        print(
            f"Typography {args.mode} failed with {len(audit.errors)} issue(s).",
            file=sys.stderr,
        )
        return 1

    if args.mode == "fix":
        print(
            f"Typography fix: {audit.files} files, "
            f"{audit.changed_files} changed, "
            f"{audit.assigned_roles} roles assigned, "
            f"{audit.stripped_inline_properties} inline declarations removed."
        )
    else:
        print(f"Typography verify: {audit.files} files conform to the contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
