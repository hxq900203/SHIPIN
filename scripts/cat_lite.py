#!/usr/bin/env python3
"""下载群里的 Cat 源（MiraPlay 用），去掉指定站点后输出到 dist/cat-lite/。

过滤方式：在源码加载站点列表的地方（`n=await X(t);e.spiders=n`）插入一个 filter，
被去掉的站点既不注册接口，也不会出现在片源列表里。规则写在 cat-lite.json。
"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "cat-lite"
CONF = json.loads((ROOT / "cat-lite.json").read_text(encoding="utf-8"))
UA = "okhttp/3.12.0"
FILES = ["index.js", "index.config.js"]


def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as e:
            if i == tries - 1:
                raise
            print(f"重试 {url}: {e}", file=sys.stderr)
            time.sleep(2 ** (i + 1))


def md5(data):
    return hashlib.md5(data).hexdigest()


def patch(js):
    names = json.dumps(CONF.get("hide_name_patterns", []), ensure_ascii=False)
    keys = json.dumps(CONF.get("hide_keys", []))
    hide = (
        f"(s=>!({names}.some(p=>new RegExp(p,'i').test(s?.meta?.name||''))"
        f"||{keys}.includes(s?.meta?.key)))"
    )
    pattern = re.compile(r",(\w+)=await (\w+)\((\w+)\);(\w+)\.spiders=\1,")
    found = pattern.findall(js)
    if len(found) != 1:
        sys.exit(f"找不到唯一的补丁位置（匹配到 {len(found)} 处），上游源码结构可能变了")
    return pattern.sub(
        lambda m: f",{m[1]}=(await {m[2]}({m[3]})).filter({hide});{m[4]}.spiders={m[1]},", js
    )


def main():
    base = CONF["upstream"]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        data = fetch(base + name)
        expect = fetch(base + name + ".md5").decode().strip().lower()
        if md5(data) != expect:
            sys.exit(f"{name} 下载不完整：md5 {md5(data)} != {expect}")
        if name == "index.js":
            data = patch(data.decode("utf-8")).encode("utf-8")
        (OUT / name).write_bytes(data)
        (OUT / (name + ".md5")).write_text(md5(data))
        print(f"{name}: {len(data)} 字节, md5={md5(data)}")


if __name__ == "__main__":
    main()
