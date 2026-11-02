# -*- coding: utf-8 -*-
"""中国高校/学会官网抓取通用模板（Windows + Python 3.x）
已验证场景：吉林大学学院官网（webplus）、中国大学生方程式官网（静态站）

三条铁律（踩过的坑，别删）：
  1. UR 必须手工 quote —— urllib 不自动编码中文/空格 URL
  2. 输出用 ascii 安全写法 —— Windows 终端 GBK，print 中文文件名会崩
  3. 让 Python 自己写文件 —— PowerShell `>` 会把 UTF-8 转 UTF-16 毁中文

用法：把本文件当参考，按站点改 URL/正则即可。下载前先抓清单存 JSON，别混在一步（必超时）。
"""
import urllib.request, urllib.parse, re, os, json, time
from concurrent.futures import ThreadPoolExecutor

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


# ---------- 铁律 1：URL 编码 ----------
def enc(u, referer=None):
    """把含中文/空格的 URL 转成合法 ASCII URL。本模块所有请求都要走它。"""
    p = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((
        p.scheme, p.netloc,
        urllib.parse.quote(p.path, safe="/%"),
        urllib.parse.quote(p.query, safe="=&%"),
        "",
    ))


def get(u, referer=None, timeout=30, binary=False):
    h = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"}
    if referer:
        h["Referer"] = referer          # webplus download.jsp 必须带 Referer
    data = urllib.request.urlopen(
        urllib.request.Request(enc(u), headers=h), timeout=timeout).read()
    return data if binary else data.decode("utf-8", "ignore")


def txt(html):
    """HTML → 纯文本（去 script/style/nav，块级标签转换行）。"""
    h = re.sub(r"(?is)<(script|style|nav|header|footer|form)[^>]*>.*?</\1>", " ", html)
    h = re.sub(r"(?is)<br\s*/?>|</(p|div|li|h[1-6]|td|tr)>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    for a, b in [("&nbsp;", " "), ("&amp;", "&"), ("&ldquo;", '"'),
                 ("&rdquo;", '"'), ("&quot;", '"'), ("&#39;", "'")]:
        h = h.replace(a, b)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", h)).strip()


# ---------- 铁律 2：安全打印 ----------
def say(s):
    print(str(s).encode("ascii", "replace").decode())


# ---------- 附件下载 + 校验 ----------
def magic_ok(p):
    """铁律校验：确认不是 403 错误页。PDF=%P / ZIP(=docx/xlsx/7z/rar)=PK"""
    return open(p, "rb").read(2) in (b"%P", b"PK")


def download(url, dest_dir, referer=None):
    fn = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    fn = re.sub(r'[<>:"/\\|?*]', "_", fn)          # Windows 非法字符
    path = os.path.join(dest_dir, fn)
    if os.path.exists(path) and os.path.getsize(path) > 2048:
        return f"SKIP {len(fn)}ch ({os.path.getsize(path)//1024}KB)"
    try:
        data = get(url, referer=referer, timeout=240, binary=True)
        open(path, "wb").write(data)
        return f"OK   {fn[:40]} ({len(data)//1024}KB)"
    except Exception as e:
        return f"FAIL {fn[:40]}: {type(e).__name__} {e}"


def download_all(items, dest_dir, workers=5):
    """items: [(url, referer|None), ...] 或 [url, ...]"""
    os.makedirs(dest_dir, exist_ok=True)
    norm = [(i, None) if isinstance(i, str) else i for i in items]
    out = []
    with ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(download, u, dest_dir, r) for u, r in norm]
        for f in futs:
            line = f.result()
            out.append(line)
            say(line)
    files = [f for f in os.listdir(dest_dir)
             if os.path.getsize(os.path.join(dest_dir, f)) > 2048]
    bad = [f for f in files if not magic_ok(os.path.join(dest_dir, f))]
    say(f"\ngot {len(files)} files, magic-bad {len(bad)}")
    assert not bad, f"存在非 PDF/ZIP 文件（疑似错误页）: {bad}"
    return out


# ---------- 两步法：抓清单 → 存 JSON ----------
def scrape_list(list_urls, item_re, file_re, out_json, referer=None, delay=0.4):
    """list_urls: 列表页 URL 列表；item_re: 抽详情页链接；file_re: 抽附件链接"""
    docs, seen = [], set()
    for lu in list_urls:
        try:
            h = get(lu, referer=referer)
        except Exception as e:
            say(f"list ERR {lu[:60]} {e}")
            continue
        for m in re.finditer(item_re, h):
            item = m.group(1)
            if not item.startswith("http"):
                item = urllib.parse.urljoin(lu, item)
            if item in seen:
                continue
            seen.add(item)
            fm = None
            try:
                dh = get(item, referer=referer)
                fres = re.findall(file_re, dh, re.I)
                if fres:
                    f0 = fres[0]
                    fm = f0 if f0.startswith("http") else ("http:" + f0 if f0.startswith("//") else urllib.parse.urljoin(item, f0))
            except Exception as e:
                say(f"detail ERR {item[:60]} {e}")
            docs.append({"page": item, "file": fm})
        time.sleep(delay)
    json.dump(docs, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    say(f"items {len(docs)}, with-file {sum(1 for d in docs if d['file'])}")
    return docs


# ---------- 自检 ----------
def demo():
    """最小可运行校验：三个坑的修复逻辑必须成立。"""
    # 铁律1：含中文+空格的 URL 必须能编码成功
    u = "http://img.sae-china.org/web/2026/04/2026中国大学生 方程式规则.pdf"
    e = enc(u)
    assert " " not in e and re.match(r"^https?://[\x00-\x7f]+$", e), e
    # 铁律2：中文安全打印不抛异常
    say("自检：中文 测试 ✓")
    # 文本清洗
    t = txt("<p>轴距</p><script>var x=1</script><p>≥1525mm</p>")
    assert "轴距" in t and "1525" in t and "var x" not in t, t
    print("demo OK")


if __name__ == "__main__":
    demo()
    print(__doc__)
