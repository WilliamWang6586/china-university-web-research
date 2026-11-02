# 吉林大学各学院官网域名速查表（2026-08 实测验证）

来源：《各学院2026年本科生集中考核转专业工作细则链接.xlsx》（官方汇总，最可靠）+ 实测可达性验证。

## 已验证可达（socket 连接成功）

| 学院 | 域名 |
|------|------|
| 法学院 | https://law.jlu.edu.cn |
| 马克思主义学院 | http://marx.jlu.edu.cn |
| 数学学院 | https://math.jlu.edu.cn |
| 物理学院 | https://phy.jlu.edu.cn |
| 化学学院 | https://chem.jlu.edu.cn |
| 生命科学学院 | https://life.jlu.edu.cn |
| 机械与航空航天工程学院 | https://mae.jlu.edu.cn |
| 汽车工程学院 | http://auto.jlu.edu.cn |
| 材料科学与工程学院 | https://dmse.jlu.edu.cn |
| 生物与农业工程学院 | https://cbae.jlu.edu.cn |
| 电子科学与工程学院 | https://ee.jlu.edu.cn |
| 通信工程学院 | https://dce.jlu.edu.cn |
| 计算机科学与技术学院 | http://ccst.jlu.edu.cn |
| 软件学院 | https://csw.jlu.edu.cn |
| 仪器科学与电气工程学院 | http://ciee.jlu.edu.cn |
| 基础医学院 | https://medicine.jlu.edu.cn |
| 公共卫生学院 | https://sph.jlu.edu.cn |
| 口腔医学院 | http://jdkq.jlu.edu.cn |
| 动物医学学院 | https://dwyx.jlu.edu.cn |
| 人工智能学院 | https://sai.jlu.edu.cn |
| 哲学社会学院 | http://zsy.jlu.edu.cn |
| 文学院 | https://wxy.jlu.edu.cn |
| 考古学院 | https://kgxy.jlu.edu.cn |
| 外国语言文化学院 | https://sflc.jlu.edu.cn |
| 历史文化学院 | https://hac.jlu.edu.cn |
| 经济学院 | https://jjxy.jlu.edu.cn |
| 行政学院 | http://adm.jlu.edu.cn |
| 商学与管理学院 | https://sg.jlu.edu.cn |
| 东北亚学院 | https://nasa.jlu.edu.cn |
| 公共外交学院 | https://sipa.jlu.edu.cn |
| 交通学院 | https://jt.jlu.edu.cn |
| 地球科学学院 | http://geo.jlu.edu.cn |
| 地球探测科学与技术学院 | http://gest.jlu.edu.cn |
| 建设工程学院 | https://const.jlu.edu.cn |
| 新能源与环境学院 | https://cer.jlu.edu.cn |
| 药学院 | https://yxy.jlu.edu.cn |
| 护理学院 | https://hlxy.jlu.edu.cn |
| 植物科学学院 | https://zky.jlu.edu.cn |
| 动物科学学院 | https://dwkx.jlu.edu.cn |
| 食品科学与工程学院 | https://spxy.jlu.edu.cn |

## 吉大官网建站系统特征

- 建站系统：webplus（附件链接统一为 `/system/_content/download.jsp?urltype=news.DownloadAttachUrl&owner={ownerId}&wbfileid={fileId}`）
- 通知公告分页：`tzgg.htm` → `tzgg/N.htm`
- 通知详情页：`info/{栏目ID}/{文章ID}.htm`
- 下载附件需带 Referer 头

## 推免文件下载实测记录（2026-08）

- 汽车工程学院 2026届推免细则通知页：`info/1114/8210.htm`（通知列表第55页）
- 汽车工程学院 2025届推免细则通知页：`info/1114/7714.htm`（第44页）
- 附件3件套：工作实施细则 + 素质类项目加分标准 + 限定选修课公示
- 2026届推免细则 = 2025年9月发布；2025届 = 2024年9月发布
