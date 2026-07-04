from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests


@dataclass(frozen=True)
class SourceCandidate:
    name: str
    url_or_path: str
    source_type: str


@dataclass(frozen=True)
class ResolvedSource:
    name: str
    url_or_path: str
    source_type: str
    local_path: str
    warning: str = ""


def download_source(candidate: SourceCandidate, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(candidate.url_or_path).name or f"{candidate.name}.download"
    target_path = target_dir / filename
    response = requests.get(candidate.url_or_path, timeout=60)
    response.raise_for_status()
    target_path.write_bytes(response.content)
    return target_path


def resolve_source(
    official: SourceCandidate,
    fallback: SourceCandidate,
    cache_dir: Path,
    download_func: Callable[[SourceCandidate, Path], Path] = download_source,
) -> ResolvedSource:
    try:
        local_path = download_func(official, cache_dir)
        return ResolvedSource(official.name, official.url_or_path, official.source_type, str(local_path))
    except Exception as exc:
        fallback_path = Path(fallback.url_or_path)
        if not fallback_path.exists():
            raise FileNotFoundError(f"Official source failed and fallback is missing: {fallback_path}") from exc
        return ResolvedSource(
            fallback.name,
            fallback.url_or_path,
            fallback.source_type,
            str(fallback_path),
            warning=f"official source failed: {exc}",
        )
