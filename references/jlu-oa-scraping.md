# 吉林大学 OA 校内通知抓取（实测 2026-09-21）

> 抓 oa.jlu.edu.cn / 做吉大每日通知推送前必读。含大量已踩过的坑，别从零试错。

## 一、URL 选型（最大的坑）

| URL | 实际内容 | 可用 |
|---|---|---|
| `PortalInformation!jldxList.action?bs=1` | 首页**置顶栏**，永远只有 4 条，分页被 HTML 注释掉 | ❌ |
| `PortalInformation!jldxList.action?channelId=179577` | 通知公告；未登录**也只渲染 4 条置顶** | ⚠️ 受限 |
| `PortalInformation!jldxList.action?channelId=179578` | 校内快讯 → **30 条实时** | ✅ |
| `channelId=179579` | 校园新闻 → 30 条实时 | ✅ |
| `channelId=179580` | 学术信息 → 30 条实时 | ✅ |
| `channelId=179581` | 院系动态 → 30 条实时 | ✅ |
| `https://oa.jlu.edu.cn/` 首页 | 各栏目混合，含实时条目 | ✅ |

**结论：要拿"最近 N 天全部"必须多栏目合并抓取**（5 个 channelId + 首页）。
实测 7 天 ≈ **115 条**；只抓 `?bs=1` 只有 **4 条**（旧脚本 `jlu_notices.py` 就是这么坏的，长期每天只报 0-1 条相关通知）。

## 二、HTML 结构

列表项在 `itemContainer` 内，每块形如：

```html
<DIV class="li rel"><I></I>
  <A class="font14" href="PortalInformation!getInformation.action?id=70547236&channelId=179577">
     关于吉林大学2023、2024、2025、2026级本科学生体质健康测试工作的通知</A>
  <A class="column" href="...&orgname=体育学院">体育学院</A>
  <SPAN class="time" style='color:gray'>2026-09-21</SPAN>
</DIV>
```

⚠️ **不要用 `</DIV>` 切块**（块内嵌套 DIV，会截断）。用 lookahead 切：

```python
BLOCK = re.compile(r'<DIV\s+class="li rel">(.*?)(?=<DIV\s+class="li rel">|$)', re.S | re.I)
TITLE = re.compile(r'getInformation\.action\?id=(\d+)[^"]*"[^>]*>(.*?)</A>', re.S | re.I)
DEPT  = re.compile(r'class="column"[^>]*>(.*?)</A>', re.S | re.I)
TIME  = re.compile(r'class="time"[^>]*>(.*?)</SPAN>', re.S | re.I)
```

## 三、时间格式两种（必须都解析）

- **绝对**：`2026-09-18`（通知公告栏）
- **相对**：`今天&nbsp;&nbsp; 13:56` / `昨天 09:12`（校内快讯 / 院系动态栏）

只认绝对格式 → 快讯栏 30 条全丢（日期为 None 被过滤掉）。

## 四、详情页解析

- `<title>` **是空的** → 标题兜底取正文首行（4 < len < 90 时采用）
- 日期兜底：正文匹配 `(\d{4})年(\d{2})月(\d{2})日`
- 正文容器：`class` 含 content / article / detail / TRS_Editor 的 div
- 附件在正文末尾的 `<a>` 链接里
- ⚠️ 纯新闻稿正文可能极短（< 200 字），批量抓时跳过即可，不是 bug

## 五、已建脚本

| 脚本 | 用法 |
|---|---|
| `D:\Hermes文件库\每日科技日报\oa_weekly.py [天数] [--section]` | 多栏目合并抓取 → 按日期分组汇总 md（存 `吉林大学相关文件\校内通知\`）<br>`--section` 额外输出 `jlu_section.txt/html` 供流水线用 |
| `D:\Hermes文件库\每日科技日报\oa_detail.py <id...> \| --from <汇总md>` | 抓详情正文 → `校内通知\详情\*.md` |

⚠️ **脚本有两个输出目录**：`OUT`（汇总存档）/ `OUT_SECTION`（jlu_section.*）。
**`jlu_section.*` 必须落在 `每日科技日报\`**，否则 `daily_pipeline.ps1` 读不到（曾把两者混用，结果产物写进了 `校内通知\`）。

## 六、流水线接入

`daily_pipeline.ps1` 第 3 步：

```powershell
# 旧（坏）：& $py -u "$out\jlu_notices.py"          # ?bs=1 只有 4 条
# 新：多栏目合并，近 2 日新通知
& $py -u "$out\oa_weekly.py" 2 --section *>> $log
```

定时任务 `Hermes每日科技日报`（每天 18:30，LastTaskResult=0 为成功）指向 `daily_pipeline.ps1` —— **改脚本无需动任务**。

## 七、微信推送脚本 push_wechat.py 三个坑（已修）

任务 `Hermes每日科技日报推送`（18:35）曾 `LastTaskResult=1`，且**每天推空消息**。
症状：`✓ 已生成文字版摘要 (106 字符, 0 板块)`。

### 坑1：读错 HTML 源 → 丢吉大通知
原 `find_latest_html()` **优先读** `~/.hermes/cron/output/tech_daily_latest.html`，但该副本由**已废弃的** `deliver_report.ps1`（只 touch 时间戳）维护，**不含**流水线前置的「吉大校内通知」。
✅ 修复：优先读 `D:\Hermes文件库\每日科技日报\<today>\科技日报_<today>.html`（主产物），cron 副本降为最后兜底。

### 坑2：提取正则失配 → 0 板块
日报 v2 的 HTML **没有** `class="section-title"`（旧版才有）。真实层级：

```
板块 = <h2>今日头版 <span class="count">FEATURED</span></h2>      ← 12 个
子块 = <div class="sub-sec-title">每日最新论文（arXiv 实时）</div>   ← 11 个
条目 = <h3><a>标题</a></h3> / semi-card / band-card / cam-brand+cam-model
```

⚠️ 用 `sub-sec-title` 切**会把子块误当板块**，且漏掉头版/财经等无子块的板块。
✅ 正确：**以 `<h2>` 切板块，`sub-sec-title` 归入该板块的 subs**。

### 坑3：吉大通知块不在 `<h2>` 体系内
它由 `daily_pipeline` 以裸 div 前置：

```html
<div style="...">📢 吉大校内通知（09-19）</div>
<div style="..."><a href="...">· 标题</a></div>
```

✅ 单独提取，并插到板块列表**最前面**：

```python
jlu_hdr = re.search(r'吉大校内通知（([^）]+)）', html)
if jlu_hdr:
    seg = html[jlu_hdr.end():]
    nxt = re.search(r'<h2|<div[^>]*class="sub-sec-title"', seg)
    if nxt: seg = seg[:nxt.start()]
    cards = [strip_tags(t) for t in re.findall(r'<a[^>]*>·\s*([^<]+)</a>', seg)]
    sections.insert(0, {"icon": "📢", "name": f"吉大校内通知（{jlu_hdr.group(1)}）",
                        "cards": cards, "subs": [], "cams": []})
```

### 修复后实测
- 板块 **0 → 13**（吉大通知排第一）
- 摘要 **106 → 1,775 字符**
- 自检：`assert jlu and jlu[0]["cards"] and len(secs) >= 10`

## 八、验证脚本（不发消息，只校验提取）

```python
import sys; sys.path.insert(0, r"D:\Hermes文件库\每日科技日报")
import push_wechat as P
p, src = P.find_latest_html(); html = open(p, encoding="utf-8").read()
secs = P.extract_sections(html)
jlu = [s for s in secs if "吉大" in s["name"]]
assert jlu and jlu[0]["cards"] and len(secs) >= 10
print("OK", len(secs), "板块")
```

⚠️ 用 `Set-Content` / `Out-File -Encoding UTF8` 写 .py 会带 **BOM** → `SyntaxError: invalid non-printable character U+FEFF`。用 `write_file` 工具，或写入后用 `[System.IO.File]::WriteAllText($p, $txt, [System.Text.UTF8Encoding]::new($false))` 去 BOM。
