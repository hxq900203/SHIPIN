#!/usr/bin/env python3
"""抓取上游 TVBox 配置（默认饭太硬），解码成明文 JSON，合并自定义片源，
输出 dist/tv.json 以及对应的 dist/tv.json.md5 / dist/tv.md5。"""
import base64
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SOURCES = ROOT / "sources.json"
CUSTOM = ROOT / "custom.json"
CAT_SITES = ROOT / "cat" / "sites.json"
UA = "okhttp/3.12.0"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.geturl()


def strip_comments(text):
    # 去掉整行的 // 注释（TVBox 配置里很常见），保留 URL 中的 //
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("//"))


def try_json(text):
    text = text.strip().lstrip("﻿")
    if not text.startswith("{"):
        return None
    try:
        return json.loads(strip_comments(text))
    except json.JSONDecodeError:
        # 去掉尾随逗号再试一次
        try:
            return json.loads(re.sub(r",\s*([}\]])", r"\1", strip_comments(text)))
        except json.JSONDecodeError:
            return None


def b64decode_loose(s):
    s = re.sub(r"\s+", "", s)
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s).decode("utf-8", "ignore")


def decode(raw):
    """支持：明文 JSON、整段 base64、图片尾部藏 base64（'**' 分隔，饭太硬常用）。"""
    text = raw.decode("utf-8", "ignore")
    cfg = try_json(text)
    if cfg is not None:
        return cfg
    m = re.search(rb"[A-Za-z0-9]{8}\*\*([A-Za-z0-9+/=\s]+)$", raw)
    if m:
        cfg = try_json(b64decode_loose(m.group(1).decode()))
        if cfg is not None:
            return cfg
    try:
        cfg = try_json(b64decode_loose(text))
        if cfg is not None:
            return cfg
    except Exception:
        pass
    raise ValueError("无法识别的配置格式（可能是新的加密方式）")


def absolutize(value, base):
    """把 ./xxx 这类相对路径改成绝对地址，否则放到别处托管后会失效。"""
    if isinstance(value, str):
        if value.startswith("./") or value.startswith("../"):
            path, sep, rest = value.partition(";")
            return urljoin(base, path) + sep + rest
        return value
    if isinstance(value, list):
        return [absolutize(v, base) for v in value]
    if isinstance(value, dict):
        return {k: absolutize(v, base) for k, v in value.items()}
    return value


def merge_custom(cfg):
    if not CUSTOM.exists():
        return cfg
    custom = json.loads(CUSTOM.read_text(encoding="utf-8"))
    for key in ("sites", "parses", "lives"):
        extra = custom.get(key) or []
        if not extra:
            continue
        existing = {item.get("key") or item.get("name") for item in cfg.get(key, [])}
        new = [i for i in extra if (i.get("key") or i.get("name")) not in existing]
        cfg[key] = new + cfg.get(key, [])  # 自定义的排在最前面
    return cfg


def cms_sites(cfg):
    """挑出 iOS 能用的苹果CMS JSON 接口（type 1），jar / JS 爬虫跳过。"""
    out, seen = [], set()
    for s in cfg.get("sites", []):
        api = str(s.get("api", ""))
        if s.get("type") != 1 or not api.startswith("http"):
            continue
        key = re.sub(r"\W", "_", str(s.get("key") or s.get("name")), flags=re.ASCII) or f"s{len(out)}"
        while key in seen:
            key += "_"
        seen.add(key)
        out.append({"key": key, "name": s.get("name") or key, "api": api})
    return out


def main():
    urls = json.loads(SOURCES.read_text(encoding="utf-8"))["upstream"]
    cfg, errors = None, []
    for url in urls:
        try:
            raw, final_url = fetch(url)
            cfg = absolutize(decode(raw), final_url)
            print(f"OK  {url}  sites={len(cfg.get('sites', []))}")
            break
        except Exception as e:  # 换下一个备用地址
            errors.append(f"{url}: {e}")
            print(f"ERR {url}: {e}", file=sys.stderr)
    if cfg is None:
        sys.exit("所有上游地址都失败：\n" + "\n".join(errors))

    cfg = merge_custom(cfg)
    DIST.mkdir(exist_ok=True)
    data = json.dumps(cfg, ensure_ascii=False, indent=2).encode("utf-8")
    digest = hashlib.md5(data).hexdigest()
    (DIST / "tv.json").write_bytes(data)
    (DIST / "tv.json.md5").write_text(digest)
    (DIST / "tv.md5").write_text(digest)
    print(f"md5={digest}")

    sites = cms_sites(cfg)
    CAT_SITES.write_text(json.dumps(sites, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"cat 可用站点 {len(sites)} 个")


if __name__ == "__main__":
    main()
