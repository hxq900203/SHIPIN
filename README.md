# SHIPIN 影视配置

自动抓取饭太硬的 TVBox 配置，解码成明文 JSON，合并你自己的片源，并生成 `.md5` 校验文件。
GitHub Actions 每 6 小时自动更新一次。

## 订阅地址（仓库公开后可用）

| 文件 | 地址 |
|---|---|
| 配置 | `https://raw.githubusercontent.com/hxq900203/SHIPIN/claude/trusting-fermat-sosbmf/dist/tv.json` |
| MD5 | `https://raw.githubusercontent.com/hxq900203/SHIPIN/claude/trusting-fermat-sosbmf/dist/tv.json.md5`（同内容：`dist/tv.md5`） |

国内访问 raw.githubusercontent.com 不稳定时，可以在前面加镜像加速，例如
`https://ghfast.top/https://raw.githubusercontent.com/...`。

## iOS：MiraPlay / HawkPlayer 等（去掉 4K 版）

订阅地址：`https://raw.githubusercontent.com/hxq900203/SHIPIN/claude/trusting-fermat-sosbmf/dist/cat-lite/index.js.md5`

来源是群里的 Cat 接口 `https://9280.kstore.vip/cat/index.js.md5`，脚本 `scripts/cat_lite.py`
下载后先核对 md5，再把名字里带 “4K” 的站点去掉。想去掉别的站，改 `cat-lite.json`：

- `hide_name_patterns`：站名匹配（正则，不分大小写），默认 `["4K"]`
- `hide_keys`：按站点 key 精确去掉，比如 `["guazi"]`

上游源码结构变了导致找不到补丁位置时，脚本会报错退出，不会生成坏文件。

## 第一次使用

1. 仓库已公开，默认分支就是 `claude/trusting-fermat-sosbmf`，Actions 每 6 小时在这个分支上自动更新。
2. 想立即更新：打开仓库的 **Actions** 页面 → 「更新配置」→ **Run workflow**。
3. 把上面的地址填到 TVBox / 影视仓 / MiraPlay 等应用的“配置地址”里。

## 文件说明

- `sources.json`：上游地址，按顺序尝试，前一个失败就用下一个。
- `custom.json`：你自己的片源（`sites` / `parses` / `lives`），会排在最前面；`key` 与上游重复的会跳过。
- `scripts/build.py`：抓取、解码（明文 / base64 / 图片里藏 base64）、相对路径转绝对路径、输出 JSON 和 MD5。
- `dist/`：生成结果，不要手动改。

## 注意

片源来自第三方，请仅用于个人学习研究。上游改了加密方式时脚本会报错，Actions 会显示失败。
