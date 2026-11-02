# PowerShell → Python 脚本调用的编码/转义坑（Windows 实战）

> 本机环境：Windows 11 + PowerShell 5.1。凡是「用 PS 驱动 Python 脚本」的任务
> （抓取、日报流水线、OCR、批处理）都会反复撞到下面这几条。
> 相关：技能 `windows-wsl2-script-exec`（WSL 侧），本文件补 PS 侧。

## 1. 不要用 here-string 内联写 Python

```powershell
# ❌ 会坏：@"..."@ 里的 \" / f-string 大括号被 PS 破坏
$pycode = @"
print(f\"  {s['icon']}\")
"@
$pycode | Out-File -FilePath script.py -Encoding UTF8
# 结果：SyntaxError: unexpected character after line continuation character
```

✅ **改用 `write_file` 工具直接写 .py 文件**，再跑。
（ladder：已经有 write_file，别再手搓 heredoc。）

## 2. `Out-File -Encoding UTF8` / `Set-Content` 会写 BOM

在 PS 5.1 里这两个 cmdlet 默认写 **UTF-8 with BOM**。Python 读带 BOM 的源码会：

```
SyntaxError: invalid non-printable character U+FEFF (line 1, column 1)
```

✅ 三种解法，任选：
- 用 `write_file` 工具（默认无 BOM）
- `[System.IO.File]::WriteAllText($p, $txt, [System.Text.UTF8Encoding]::new($false))`
- 已有 BOM 的文件：读出来 `TrimStart([char]0xFEFF)` 再写回

## 3. 必须设 `$env:PYTHONUTF8 = "1"`

`print()` 含中文/emoji 时，定时任务（无控制台）下 stdout 走 GBK → `UnicodeEncodeError` 直接崩。
PEP 540 的 UTF-8 模式一举解决。

## 4. 跑脚本用 Start-Process + 重定向到文件

```powershell
$env:PYTHONUTF8 = "1"
$p = Start-Process -FilePath $py -ArgumentList @("-u", "D:\...\script.py", "arg") `
     -NoNewWindow -Wait -PassThru `
     -RedirectStandardOutput "D:\...\_out.txt" -RedirectStandardError "D:\...\_err.txt"
Write-Output "退出码: $($p.ExitCode)"
Get-Content "D:\...\_out.txt" -Encoding UTF8   # 读回时必须显式 -Encoding UTF8
```

好处：`-u` 无缓冲便于定位卡死；stdout/stderr 分离；退出码可控。
⚠️ `Get-Content` 不加 `-Encoding UTF8` 会用 GBK 解 → 中文乱码。

## 5. 中文参数不要在 PS 里传

PS 传中文实参给 python3.14 会**吞字符**。
✅ 中文写进文件（清单/配置），或只传 ASCII（id、数字、路径英文段）。

## 6. 禁 `&` 前台调用（会被判为后台符）

前台跑脚本**不要用 `& $py ...`**（工具层会报 `uses '&' backgrounding`）。
用 `Start-Process`，或直接 `python.exe script.py`（无前导 `&`）。

## 7. 改含中文的脚本不要用 `Get-Content`/`Set-Content`

PS 5.1 的 `Get-Content` 按 **GBK** 解 UTF-8 文件 → 中文不可逆损毁。
✅ 编辑 `.py` / `.md` 一律用 `patch` / `write_file` 工具；
   必须用 PS 时走 `[System.IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)`。

## 8. 临时文件自检纪律

- 每轮生成的 `_xxx.py` / `_xxx_out.txt` 跑完**立刻清掉**，别在 `<工作目录>/` 根目录堆积
- 清理用 `Get-ChildItem <dir> -Filter "_xxx*" -File | Remove-Item -Force`（通配批量比逐个列举稳）
- 脚本内嵌 `assert` 自检（三行即可），失败即暴露，比事后读日志快

## 9. 定时任务返回值的读法

`Get-ScheduledTaskInfo` 的 `LastTaskResult`：
- `0` = 成功
- `1` = 脚本非零退出（**注意**：脚本自身 `return 0` 也可能因外层 PS 报错而变 1）
- 别只看这个值下结论 —— 要跑一遍看**实际产物**（文件大小/内容），因为"成功但产出空"完全可能
  （实例：任务返回 1 的同时，脚本每天推 106 字符的空摘要）
