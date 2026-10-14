"""IndexTTS 2.5 一键调试：同一段参考音频 + 同一句话，用几组不同参数各生成一遍，生成对比页面。

用法（由“一键调试.bat”调用，工作目录必须是 index-tts 代码目录）：
    uv run --no-sync python tune.py [参考音频路径]
"""
import html
import os
import socket
import sys
import time

# 与 webui.py 的默认值保持一致
BASE_GEN = dict(do_sample=True, top_p=0.8, top_k=30, temperature=0.8, length_penalty=0.0,
                num_beams=3, repetition_penalty=10.0, max_mel_tokens=1500)
EMO_NAMES = ["喜", "怒", "哀", "惧", "厌恶", "低落", "惊喜", "平静"]

# (文件名, 说明, 在网页里怎么设置, 参数改动)
VARIANTS = [
    ("01_默认", "官方默认参数", "什么都不用改",
     {}),
    ("02_默认再来一次", "参数和 01 完全一样，用来听每次生成的随机差异", "什么都不用改，多点几次生成",
     {}),
    ("03_更稳定", "temperature 0.6：更少乱读、重复，语气更平", "高级生成参数设置 → temperature 调到 0.6",
     {"temperature": 0.6}),
    ("04_更生动", "temperature 1.0：语调起伏更大，偶尔会不稳", "高级生成参数设置 → temperature 调到 1.0",
     {"temperature": 1.0}),
    ("05_稍快", "时长系数 0.9：语速快一点", "时长系数 调到 0.9",
     {"duration_factor": 0.9}),
    ("06_稍慢", "时长系数 1.1：语速慢一点", "时长系数 调到 1.1",
     {"duration_factor": 1.1}),
    ("07_平静", "情感向量：平静 0.6", "情感控制方式选“使用情感向量控制”，平静 拉到 0.6",
     {"emo": {"平静": 0.6}}),
    ("08_开心", "情感向量：喜 0.5", "情感控制方式选“使用情感向量控制”，喜 拉到 0.5",
     {"emo": {"喜": 0.5}}),
]


def ask_reference_audio():
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    while True:
        path = path.strip().strip('"').strip()
        if path and os.path.isfile(path):
            return os.path.abspath(path)
        if path:
            print(f"找不到文件：{path}")
        path = input("请把参考音频文件拖进这个窗口，然后按回车：")


def ask_text():
    default = "大家好，这是一段测试语音。今天天气不错，我们一起出去走走吧？"
    print()
    print("请输入要念的文字（直接按回车使用默认测试句）：")
    text = input("> ").strip()
    return text or default


def webui_running():
    try:
        with socket.create_connection(("127.0.0.1", 7860), timeout=1):
            return True
    except OSError:
        return False


def build_tts():
    import torch
    from indextts.infer_v2_5 import IndexTTS2

    use_bf16 = False
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        # 和 webui.py 一样：显存小于 10 GB 时用半精度
        use_bf16 = vram_gb < 10.0 and torch.cuda.is_bf16_supported()
    else:
        print("[警告] 没有检测到 NVIDIA 显卡，将用 CPU 生成，会非常慢。")
    return IndexTTS2(cfg_path="checkpoints/config.yaml", model_dir="checkpoints",
                     use_bf16=use_bf16, use_qwen_emo=False)


def write_report(out_dir, ref_audio, text, results):
    rows = []
    for name, desc, howto, seconds, ok in results:
        if ok:
            player = f'<audio controls preload="none" src="{html.escape(name)}.wav"></audio>'
        else:
            player = '<span class="err">生成失败，见黑色窗口里的报错</span>'
        rows.append(
            f'<tr><td class="name">{html.escape(name)}</td>'
            f'<td>{player}</td>'
            f'<td>{html.escape(desc)}<div class="howto">网页里这样设：{html.escape(howto)}</div></td>'
            f'<td class="num">{seconds:.1f} 秒</td></tr>'
        )
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IndexTTS 调试对比</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; margin: 24px; color: #222; background: #fafafa; }}
  h1 {{ font-size: 22px; margin: 0 0 8px; }}
  .meta {{ color: #555; margin-bottom: 16px; line-height: 1.7; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  td, th {{ border: 1px solid #ddd; padding: 10px; vertical-align: middle; text-align: left; }}
  th {{ background: #f0f0f0; }}
  .name {{ font-weight: bold; white-space: nowrap; }}
  .howto {{ color: #0a6; font-size: 13px; margin-top: 4px; }}
  .num {{ white-space: nowrap; color: #777; }}
  .err {{ color: #c00; }}
  .tip {{ margin-top: 16px; padding: 12px; background: #fffbe6; border: 1px solid #f0e0a0; }}
</style></head><body>
<h1>IndexTTS 调试对比</h1>
<div class="meta">参考音频：{html.escape(ref_audio)}<br>文本：{html.escape(text)}<br>文件夹：{html.escape(out_dir)}</div>
<table><tr><th>版本</th><th>试听</th><th>改了什么</th><th>耗时</th></tr>
{''.join(rows)}
</table>
<div class="tip">挑出最好听的一个，按“网页里这样设”去 IndexTTS 网页里设置，再点“保存为预设”，以后直接用。<br>
01 和 02 参数相同，如果两者差别很大，说明多点几次生成、挑最好的，比调参数更有效。</div>
</body></html>"""
    path = os.path.join(out_dir, "对比.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return path


def main():
    print("=" * 50)
    print("  IndexTTS 2.5 一键调试")
    print("  同一句话用 8 种设置各生成一遍，方便对比")
    print("=" * 50)

    if webui_running():
        print()
        print("[注意] IndexTTS 网页版正在运行，两个同时开 8GB 显存不够。")
        print("       请先关掉“启动.bat”的黑色窗口，再按回车继续。")
        input()

    ref_audio = ask_reference_audio()
    text = ask_text()

    out_dir = os.path.abspath(os.path.join("outputs", time.strftime("调试_%Y%m%d_%H%M%S")))
    os.makedirs(out_dir, exist_ok=True)

    print()
    print("正在加载模型，需要一两分钟...")
    tts = build_tts()

    results = []
    for i, (name, desc, howto, change) in enumerate(VARIANTS, 1):
        print()
        print(f"[{i}/{len(VARIANTS)}] {name}：{desc}")
        gen = dict(BASE_GEN)
        gen.update({k: v for k, v in change.items() if k in BASE_GEN})
        emo_vector = None
        if "emo" in change:
            vec = [change["emo"].get(n, 0.0) for n in EMO_NAMES]
            emo_vector = tts.normalize_emo_vec(vec, apply_bias=True)
        start = time.perf_counter()
        ok = True
        try:
            tts.infer(
                spk_audio_prompt=ref_audio, text=text, lang="ZH",
                output_path=os.path.join(out_dir, f"{name}.wav"),
                emo_alpha=0.65, emo_vector=emo_vector,
                duration_factor=change.get("duration_factor", 1.0),
                **gen,
            )
        except Exception as e:  # 一组失败不影响其他组
            ok = False
            print(f"[错误] {name} 生成失败：{e!r}")
        results.append((name, desc, howto, time.perf_counter() - start, ok))

    report = write_report(out_dir, ref_audio, text, results)
    print()
    print("全部完成！对比页面：", report)
    if hasattr(os, "startfile"):
        os.startfile(report)


if __name__ == "__main__":
    main()
