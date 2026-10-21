# JIYAX · 无际涯

品牌首页，沿用已确认的黑白灰设计，包含 AI、VPS、加密三个入口、中英文切换与精选内容轮播。三个专题子站尚未上线，当前入口显示栏目预告；加密栏目规划域名为 `crypto.jiyax.com`。

源码仓库：`git@github.com:tktkl/jiyax.com.git`，默认分支 `main`。构建仅依赖 Python 3；生成文件、截图、备份和本地凭据不纳入版本控制。目前未配置 GitHub Actions，部署按下文通过 SSH 发布。

顶部导航始终显示 `AI / VPS / CRYPTO`。中文模式的正文、栏目标签、卡片、轮播及栏目预告使用中文；三个栏目标签分别为「AI 订阅」「VPS 基建」「加密货币」。英文模式显示相应英文内容，品牌名、产品名和域名保持原文。

页脚联系方式：Telegram `https://t.me/jiyax_com`、X `https://x.com/jiyax_com`，配有内嵌 SVG 图标。后续增加邮箱、WhatsApp 等入口时，在 `.jx-socials` 中沿用 `.jx-social-link` 结构，使用实际地址与对应图标；不创建空入口。

## 文件与构建

- `src/home.html`：已确认的设计源文件。
- `src/site.css`：全屏首屏、单套顶部导航与手机布局的覆盖样式。
- `src/language.js`：语言选择规则，按 URL、手动偏好、浏览器首选语言依次判断。
- `build.py`：移除预览宿主依赖，抽出带内容指纹的图片、样式与脚本，生成站点和 SEO 元信息。
- `dist/`：可直接部署的静态文件，不依赖 Node 服务、数据库或第三方脚本。
- `deploy/*.conf`：每个域名独立的 Nginx 配置。

```sh
python3 build.py
python3 package.py
```

`deploy/site.tar.gz` 仅包含站点文件，不携带 macOS 隐藏元数据。

## bero 部署

- 服务目录：`/srv/jiyax/`。
- 版本目录：`/srv/jiyax/releases/<UTC时间>/`，`current` 软链接指向当前版本。
- 当前网站：`https://jiyax.com/`；`https://www.jiyax.com/` 保留路径与参数跳转主域名。
- 语言入口：`?lang=zh` / `?lang=en`；未指定时优先读取手动选择，再根据浏览器首选语言判断：`zh` 系列为中文，其余为英文。只有手动切换会写入 `jiyax.language.preference`，忽略旧版自动保存的语言。
- 静态内容由宿主机 Nginx 提供，无需额外 Compose 容器或公网服务端口。
- Nginx：`/etc/nginx/sites-available/jiyax.com.conf`、`www.jiyax.com.conf`，同名链接启用。
- 证书：`/etc/letsencrypt/live/jiyax.com/`，覆盖两个域名；复用 Cloudflare DNS-01、现有续期调度与 Nginx deploy hook。
- 两个域名都需经过 Cloudflare，并由现有 Request Header Transform Rule 覆盖所有路径。沿用 `/etc/nginx/snippets/origin-auth-check.conf`；密钥唯一位置见 `/srv/nginx/README.md`，本文不记录。
- 独立日志：`/var/log/nginx/jiyax.com.*.log`、`/var/log/nginx/www.jiyax.com.*.log`。沿用系统 Nginx logrotate。
- HTML 每次重新验证缓存，带内容指纹的静态资源缓存一年。
- 包含 canonical、hreflang、Open Graph、X 分享卡、`robots.txt` 和 `sitemap.xml`。
- 首屏占满导航下方视口，主图按比例缩放并渐隐融入背景。手机使用同一套导航与两行顶部布局；导航、语言和主要交互控件触控高度至少 44px。

## 更新与回退

更新前读取 `/srv/AGENTS.md` 和本文，检查现有文件及链接，备份到 `/srv/backups/jiyax/<UTC时间>/`。构建后将 `dist/` 上传到新的版本目录，使用临时软链接配合 `mv -Tf` 原子替换 `current`。保留上一版本；跨版本仍可能被缓存 HTML 引用的内容指纹资源应同时保留。

仅内容更新不需要重载 Nginx。修改站点配置时先 `nginx -t`，通过后再 `systemctl reload nginx`；失败恢复备份配置与原链接。

回退内容：将 `current` 原子切回上一版本，再验证页面。首次部署的撤销：移除本次创建的两个 `sites-enabled/` 链接，执行配置检查并重载；保留站点数据、证书和备份。

验证范围：公网 HTTPS 首页、www 跳转、语言切换、入口返回、轮播、静态资源、无密钥与错误密钥的源站拒绝、正确密钥的源站访问。证书配置变更后只对该证书验证续期 dry-run 和 deploy hook。

## 首次上线记录

2026-10-21 部署；已验证公网首页 200、www 301、无效回源认证 403、中英文切换、栏目入口与返回、轮播和滚动。首页、图片、样式、脚本及 SEO 文件与发布文件内容一致。证书续期 dry-run 连同 Nginx deploy hook 已通过。备份目录为 `/srv/backups/jiyax/20261021T075844Z/`。

## 2026-10-21 首页更新

该次版本：`/srv/jiyax/releases/20261021T083105Z/`。上线全屏主视觉、单套顶部导航、加密栏目改名和浏览器语言自动选择。已检查 320px、390px 手机布局与宽屏效果，验证导航定位、语言切换及记忆、栏目返回和轮播；语言规则 10 个用例通过。公网 HTML、CSS、JS 与本地构建文件逐字节一致。

改前备份：`/srv/backups/jiyax/20261021T083105Z/`；内容回退目标：`/srv/jiyax/releases/20261021T075844Z/`。本次只更新静态内容及源文件，没有修改 Nginx、证书或 DNS。

## 2026-10-21 文案与联系入口更新

当前版本：`/srv/jiyax/releases/20261021T084708Z/`。顶部导航在两种语言下统一为 `AI / VPS / CRYPTO`；中文模式补齐首屏标语、栏目标签、装饰卡片、轮播、页脚和栏目预告。页脚新增带 SVG 图标的 Telegram 与 X 链接，联系方式采用可复用的链接样式，触控高度 44px。

已验证 52 个文案键均有中英文内容，脚本语法、桌面与 320px/390px 手机布局、语言切换及栏目预告；公网 HTML、CSS、JS 与构建文件逐字节一致。改前备份：`/srv/backups/jiyax/20261021T084708Z/`；内容回退目标：`/srv/jiyax/releases/20261021T083105Z/`。
