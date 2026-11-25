屿间导航 V1.1.1 — 静态图标部署包
本包包含192个默认网站清单，但当前网络环境无法下载真实图片，icons目录初始为空。

方案 A：GitHub Actions 自动下载
1. 将本包解压，在现有 GitHub 仓库根目录上传 index.html、icon-manifest.json、download_icons.py 及 .github/workflows/download-icons.yml（注意隐藏目录）。
2. 仓库 Actions 页面选择 Download default website icons，点击 Run workflow。若写入被禁止，在 Settings > Actions > General 中检查工作流写权限及分支保护。
3. 工作流将图片写入 icons/ 并提交下载报告。检查报告中 failed 与 review 项，人工核对真实品牌图标；第三方可能返回通用图标。
4. 如果通过 GitHub Pages 或其他静态服务发布，确保 index.html 与 icons/ 同目录。若只是上传 GitHub 而实际网站托管在别处，需同步 icons/ 到实际站点。

方案 B：电脑上下载
安装 Python 3 后，在解压目录执行：python -m pip install Pillow
然后执行：python download_icons.py
将生成的 icons/ 与 index.html 上传到实际站点。脚本可重复运行补齐缺失文件。

静态图标采用完整域名.png，优先级：自定义图标 > 默认网站静态图标 > 原有缓存与动态来源 > 原有彩色备用图标。
下载阶段可使用 Google 作为最后来源，网页运行时不会自动请求 Google 图标。
保留 V1.1 原有代码与后端；未在真实站点浏览器进行回归测试。
