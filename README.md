# Antarctic 南极冰 官网

> AI，本来就该是冷的。

一个虚构品牌的恶搞官网：Antarctic Ice（南极冰）是一家“专注于极低温安全与可靠拉力的 AI 公司”，提供 Cold Floe / Cold Sleet / Cold Hail-ku 三款冰、Colding Plan（不是 Coding Plan）低温生活订阅，以及真的是背带的 Harness。

本网站为恶搞创作，不代表任何真实公司或产品。所有价格不可购买，所有表单都不会发送任何数据。

## 目录结构

```
index.html, *.html, models/, research/   构建产物（GitHub Pages 直接托管这些文件）
assets/css/site.css                      全站共享样式
assets/js/site.js                        全站共享脚本（导航、淡入、筛选、假表单、复制按钮）
assets/img/                              图片
src/pages/                               页面源文件（只含正文部分）
tools/build.py                           构建脚本：套上公告条 + 导航 + 页脚，并检查断链
```

## 修改页面

1. 编辑 `src/pages/` 下对应的文件（站内链接写成 `{{root}}xxx.html`）。
2. 运行构建：

   ```bash
   python3 tools/build.py
   ```

3. 提交 `src/` 和生成的 HTML，推送后 GitHub Pages 会自动更新。

如果仓库名不是 `antarctic-ice`，构建时设置 `BASE_PATH`，让 404 页面的链接指向正确路径：

```bash
BASE_PATH=/你的仓库名/ python3 tools/build.py
```

保持冷静。系好 Harness。
