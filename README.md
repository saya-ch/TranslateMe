# 帮我说出口 · TranslateMe

> 一个围绕孩子建立的私密沟通中枢。AI 可以分别听见孩子、家长、老师的真实想法，但不会自动泄露任何一方原话。

TRAE AI 创造力大赛初赛作品 · 社会服务赛道 · 社会公益 / 青少年身心健康方向。

## 项目简介

很多初高中学生遇到学习压力、同伴关系、亲子冲突时，不是不想求助，而是不知道怎么开口，也怕一开口就被评价。他们真实说出口的话可能只有："我很烦""我不想去学校""你们不懂我"。

**帮我说出口** 不是 AI 心理咨询师，也不是情绪陪聊机器人。它是一个以孩子为中心的沟通桥梁：AI 作为受托的中间人，分别听见三方想法，但只在用户明确授权后，把可分享的信息转成温和、低冲突、可理解的沟通内容。

## 核心闭环

### 孩子端
1. 私密倾诉（默认只有自己能看到）
2. 安全确认（命中高风险表达时，两路分支）
3. AI 帮孩子整理：我真正想表达什么 / 我怕什么 / 我希望大人怎么做
4. 选择分享范围：只让自己看 / 生成草稿自己发 / 发给家长 / 只发模糊提醒
5. 预览草稿（可编辑）→ 确认发送
6. 收件箱接收家长回应

### 家长端
1. 收件箱看到孩子的沟通请求（温和摘要，非原话）
2. 问 AI 怎么回应
3. AI 给通用沟通建议（含信息防火墙说明，不透露孩子未授权内容）
4. 回应草稿（可编辑）→ 确认发送给孩子

### 老师端
1. 记录观察（不直接变成对家长的告知）
2. AI 给谈话建议、观察点、转介建议
3. 选择只记录或之后走学校心理老师/家校沟通流程

## 信息防火墙

- 原话默认不共享
- 具体事实默认不共享
- 只共享用户明确允许的内容
- 未授权时只给对方通用沟通建议
- 分享前必须让用户确认
- 对方不能通过追问套出孩子隐私
- AI 不能说"孩子其实告诉我……"

详见 [docs/safety-boundary.md](docs/safety-boundary.md)。

## 安全确认

"高风险表达"不等于系统判定孩子有危险。命中后进入安全确认页，由用户自己选择：

- **我现在安全，只是想整理表达**：可继续整理流程
- **我不太安全 / 我身边马上有危险**：只显示支持资源（12355/12356 心理支持；110/120 立即人身危险）

不询问危险方式、地点、计划，不输出任何危险行为方法。

## 技术栈

- Vite + React + TypeScript
- 纯静态前端，无后端、无数据库、无登录、无外部 API
- 初赛阶段用本地规则和模板模拟受控 AI 转译
- 用模块级内存状态模拟三方收件箱，同一设备切换身份即可看到消息流

## 安装与运行

```bash
# 安装依赖
npm install

# 本地开发
npm run dev

# 类型检查
npm run lint

# 构建
npm run build

# 预览构建产物
npm run preview
```

## 打包为 HTML Zip

```bash
npm run build
cd dist
zip -r ../translateme-dist.zip .
```

`vite.config.ts` 已配置 `base: './'`，使用相对资源路径，保证打包后的 HTML Zip 可通过本地静态服务器或社区上传环境正常打开。

## 部署

`dist/` 可直接部署到 GitHub Pages / Vercel / Netlify。

## 演示提示

- 家长端收件箱提供"加载演示案例"按钮，方便评委快速查看效果
- 正式流程中，如果孩子没有确认发送，家长端显示"暂无沟通请求"
- 老师端为独立流程，不接收孩子消息（MVP 阶段）

## 隐私说明

- 应用内不主动收集姓名、学校、班级、手机号等身份信息
- 不上传、不保存用户输入；输入仅存于浏览器内存，离开页面或刷新即销毁
- 复制功能走浏览器原生 Clipboard API，不经过任何服务端
- 若部署到 GitHub Pages / Vercel / Netlify，托管平台可能产生基础访问日志，由平台方管理

## 仓库结构

```
TranslateMe/
├── src/
│   ├── App.tsx                       # 主界面 + 状态机（按身份分流）
│   ├── main.tsx                      # 入口
│   ├── styles.css                    # 完整视觉样式（移动优先）
│   ├── types.ts                      # 共享类型
│   ├── components/
│   │   ├── IdentitySelect.tsx        # 身份选择
│   │   ├── SafetyPage.tsx            # 安全确认页（两路分支）
│   │   ├── ChildInput.tsx            # 孩子端倾诉输入
│   │   ├── ChildClarifyPanel.tsx     # 孩子端澄清三区块
│   │   ├── ShareScopeSelect.tsx      # 孩子端分享范围
│   │   ├── DraftPreview.tsx          # 孩子端草稿预览
│   │   ├── ChildInbox.tsx            # 孩子端收件箱
│   │   ├── ParentInbox.tsx           # 家长端收件箱（含演示入口）
│   │   ├── ParentMessageView.tsx     # 家长端消息查看
│   │   ├── ParentAsk.tsx             # 家长端提问
│   │   ├── ParentGuidePanel.tsx      # 家长端 AI 建议
│   │   ├── TeacherInput.tsx          # 老师端观察记录
│   │   ├── TeacherGuidePanel.tsx     # 老师端谈话建议
│   │   ├── CopyButton.tsx            # 复制按钮
│   │   └── Footer.tsx                # 底部边界声明
│   ├── lib/
│   │   ├── safety.ts                 # 安全确认检测
│   │   ├── childBuilder.ts           # 孩子端澄清+草稿生成
│   │   ├── parentBuilder.ts          # 家长端通用建议+防火墙
│   │   ├── teacherBuilder.ts         # 老师端谈话建议
│   │   └── messageStore.ts           # 本地模拟收件箱
│   └── data/
│       └── examples.ts               # 三端示例输入
├── docs/
│   ├── project-brief.md              # 项目背景
│   ├── safety-boundary.md            # 安全边界
│   └── architecture.md               # 真实产品架构说明
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## 后续方向

初赛 Demo 用本地规则和模板模拟受控 AI 转译。后续可接入受安全规则约束的 LLM，但必须先做安全确认、输出非诊断审查、严格遵守信息防火墙、禁止长期陪聊和诊断标签。真实产品架构详见 [docs/architecture.md](docs/architecture.md)。
