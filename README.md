# 中国高校网站抓取实战

> 在国内网络环境下抓高校/机关网站（教务处、研究生院、学院主页）的实战经验：中文 URL 与空格必须手工 quote、PowerShell 的 `>` 会把中文写坏、here-string 会毁 Python 脚本、下载后要校验文件魔数、Bing 中文检索失效时改用站内检索与 RSS。

**版本** 1.0.0 ｜ **技能名** `china-university-web-research`

## 什么时候用

- 要抓某高校的通知公告、新闻列表、历年分数线
- 目标站点是老旧 ASP/PHP，编码 GBK/GB2312，直接 requests 得到乱码
- 搜索结果和实际页面不一致，怀疑被做了地区定向

## 核心做法

1. **URL 先 quote**：中文和空格一律 `urllib.parse.quote` 后再请求，不要指望 requests 自动处理。
2. **不要用 shell 重定向存中文**：PowerShell `>` 默认 UTF-16/GBK 写出，中文全毁；用 Python 写文件。
3. **不要用 here-string 拼 Python 脚本**：会被 shell 提前展开，脚本语法全错；用 write_file 落盘再执行。
4. **下载后校验魔数**：先读前 4 字节判断是 PDF/HTML/zip 还是错误页，再交给解析器。
5. **列表页分页**：优先找 `list.htm?page=N` 这类整数参数，比解析"下一页"链接稳。
6. **编码兜底**：`resp.content.decode('utf-8', 'ignore')` 失败时依次试 `gbk` / `gb18030`。

## 安装

把本目录整个复制到你的 agent 技能目录（如 `~/.agent/skills/` 或所用工具的 skills 目录）：

```bash
git clone https://github.com/WilliamWang6586/china-university-web-research.git
cp -r china-university-web-research "<你的技能目录>/"
```

放进去后，agent 读到 `SKILL.md` 即可按其中的触发条件调用。

## 文件

- `SKILL.md` — 完整方法与判据
- `references/` — 各站点抓取记录与踩坑

## 说明

