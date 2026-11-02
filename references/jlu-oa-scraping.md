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

## 五、验证脚本（不发消息，只校验提取）

```python
import sys; sys.path.insert(0, r"<工作目录>/每日科技日报")
import push_wechat as P
p, src = P.find_latest_html(); html = open(p, encoding="utf-8").read()
secs = P.extract_sections(html)
jlu = [s for s in secs if "吉大" in s["name"]]
assert jlu and jlu[0]["cards"] and len(secs) >= 10
print("OK", len(secs), "板块")
```

⚠️ 用 `Set-Content` / `Out-File -Encoding UTF8` 写 .py 会带 **BOM** → `SyntaxError: invalid non-printable character U+FEFF`。用 `write_file` 工具，或写入后用 `[System.IO.File]::WriteAllText($p, $txt, [System.Text.UTF8Encoding]::new($false))` 去 BOM。
