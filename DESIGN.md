---
name: 杭州酒店入住率分析
description: 浅色科研图表与可操作的数据分析看板
colors:
  teal: "#287d8e"
  mint: "#79b9bb"
  coral: "#f1b09a"
  cluster-blue: "#8ca9ce"
  ink: "#253f4b"
  muted: "#526e79"
  line: "#dce6e9"
  canvas: "#f5f8f8"
  surface: "#ffffff"
  control-border: "#b3c8cf"
  primary-hover: "#226c7b"
  control-hover: "#e5f1f1"
  table-head: "#edf4f4"
  grid-line: "#e8eff1"
  notice-bg: "#fff3ec"
  notice-ink: "#714a35"
typography:
  display:
    fontFamily: "Microsoft YaHei, Noto Sans SC, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.3
  title:
    fontFamily: "Microsoft YaHei, Noto Sans SC, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.6
  body:
    fontFamily: "Microsoft YaHei, Noto Sans SC, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Microsoft YaHei, Noto Sans SC, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
  metric:
    fontFamily: "Microsoft YaHei, Noto Sans SC, sans-serif"
    fontSize: "30px"
    fontWeight: 650
    lineHeight: 1.35
rounded:
  control: "6px"
  panel: "12px"
spacing:
  compact: "8px"
  inline: "16px"
  panel-gap: "20px"
  section: "22px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "8px 11px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.surface}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 11px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 11px"
  chart-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "20px 18px 8px"
---

# Design System: 杭州酒店入住率分析

## Overview

**Creative North Star: "清晰的科研分析台"**

大屏采用任务操作界面，以用户提供科研图表的浅色画布、青蓝主色、薄荷绿辅助与珊瑚强调色为依据。视觉目标是让教师和学生能读清趋势、比较区域，并核对每个筛选结果的口径。

延续原方向种子：主要趋势图占首屏左侧，区域比较在右侧，过滤器置于标题下方，表格在末尾。图表不加装饰渐变和发光。印刷分析图以同一主色保持一致，教材复现图另保留深蓝底与浅蓝标记。本文记录已实现系统，颜色和尺寸以前置令牌为准。

**Key Characteristics:**
- 浅色画布与白色图表面板。
- 青蓝主数据、薄荷辅助序列、珊瑚选中强调。
- 清楚的单位与预测原点；来源和完整方法说明集中于正文、README及数据文档。
- 桌面双列、窄屏单列的连续分析阅读。

## Colors

以低饱和青绿色连接图表与操作，以冷白中性色保证正文和网格退居辅助层。

### Primary

- **湖水青蓝**（`teal`）：主按钮、移动平均、月度柱图、排名柱条及预测中心线。
- **深湖水悬停**（`primary-hover`）：主按钮悬停，保持白字层级。

### Secondary

- **薄荷青绿**（`mint`）：真实日度曲线、周内柱图与半透明预测区间。

### Tertiary

- **柔珊瑚**（`coral`）：所选区县在排名图中的强调，同时属于固定聚类类别色。
- **柔雾蓝**（`cluster-blue`）：固定聚类所需的补充类别色。

### Neutral

- **深青墨 / 灰青文字**（`ink` / `muted`）：标题与正文、来源及统计说明。
- **冷白画布 / 纯白面板**（`canvas` / `surface`）：页面底层与图表内容层。
- **浅灰分隔 / 控件灰青边框 / 图表网格线**（`line` / `control-border` / `grid-line`）：区分结构、可操作控件和坐标参照。
- **浅青表头 / 浅青悬停**（`table-head` / `control-hover`）：表格与次按钮的状态反馈。
- **浅暖提示底 / 暖褐提示字**（`notice-bg` / `notice-ink`）：无有效观测的可读提示。

**The Selected Accent Rule.** 珊瑚色只承担选中强调与固定类别含义；图表必须同时用标签、线宽或点尺寸表明状态。

## Typography

**Display Font / Body Font:** Microsoft YaHei，回退 Noto Sans SC、sans-serif。中文无衬线保持课程分析界面的一致性，数字采用等宽数字排列。

### Hierarchy

- **Display**：页面唯一主标题，使用 `display`；窄屏缩至（25px）。
- **Title**：图表与明细标题，使用 `title`。
- **Body**：操作控件与一般文字，使用 `body`。
- **Label**：来源、筛选标签、口径与脚注，使用 `label`；表格正文（13px）。
- **Metric**：四项关键指标，使用 `metric`，单位跟随数值，日度波动明确写为 pp。

**The Units Stay Visible Rule.** 入住率使用百分数；标准差使用百分点。图表轴、指标和提示文字不得省略会改变理解的单位。

## Layout

内容居中，最大宽度（1520px），桌面内边距（32px 34px 28px）。标题与观察日期范围左右排列，过滤器在其下，以水平细线分区。四项指标横排，用分隔线组织而非重复卡片。

图表采用（1.5:1）双列网格，间距（20px），每行左侧更宽；主要趋势与区县排名放首行，其后为月度、周内、水平与波动、预测，末尾明细表跨全宽。标准图表高度（290px），紧凑图（260px）；标题位于绘图区之外，仅预测图保留历史原点。

视口宽度不大于（850px）时改为单列，页面横向内边距（16px），关键指标改为两列，快捷按钮允许换行。明细表在自身容器横向滚动，最大高度（340px），表头吸顶。散点绘图区小于（440px）时，优先显示当前区县标签，并用重叠避让保护可读性。

## Elevation & Depth

系统以冷白背景、白色面板、浅边框建立层次，没有结构阴影或装饰光晕。半透明色带仅用于表达预测区间，不能作为背景装饰。没有全屏装饰入场动画；图表更新沿用（450ms）的短过渡。

## Shapes

控件为轻圆角（`rounded.control`），图表面板为温和圆角（`rounded.panel`）。按钮、日期输入与选择框保持至少（40px）高度。面板与控件通过细边框保持边界，不使用胶囊按钮、倾斜边角或装饰纹理。

## Components

- **筛选行**：起止日期、范围选择、年度快捷键、全部样本与更新分析。主操作为青蓝实底，其他操作为白底描边；鼠标悬停有浅色反馈，键盘焦点为薄荷色（3px）外轮廓，偏移（2px）。
- **关键指标**：标签、显著数值、统计说明三层；保持全市官方口径和区县口径的可辨识性，明确有效及缺失天数。
- **趋势面板**：真实日度用薄荷细线，移动平均用青蓝粗线；保留横向缩放与图例。
- **比较图**：排名和月度以青蓝柱条表达；周内使用薄荷。排名柱条和散点可点击选区县，日期筛选更新图表与明细。
- **聚类散点**：类别颜色沿用2024—2025年的固定聚类；所选区县加大点尺寸，不能随日期筛选重新赋予颜色语义。
- **预测图**：中心线配半透明薄荷区间，图例置于绘图区上方。历史预测原点固定为2025-12-31，区间图例可见，历史筛选不重估预测。
- **观测表格**：浅青吸顶表头、细横分隔线、数值右对齐；显示最近45条，导出入口位于标题右侧。
- **无结果提示**：在筛选行之后显示暖色提示文字，明确让用户调整起止日期。

**The Chart Family Rule.** 教材复现10图逐一保持原作深蓝背景及各自红蓝、黄色、多色与渐变标记；6张研究分析图采用白底，交互看板沿用浅底青绿体系，保持各自任务内一致。

## Do's and Don'ts

### Do:
- 沿用浅色科研配色，并保持图表标题、单位和口径说明可见。
- 通过线宽、标签、位置或点尺寸补充颜色表达。
- 保留日期与区县筛选、年度快捷键和导出入口的清楚层级。
- 将预测原点和区间说明放在预测图标题下方。
- 教材10图保留深蓝模板结构；6张分析图延续青绿主色。

### Don't:
- 不要给图表添加装饰渐变、发光、立体柱体或多余阴影。
- 不要把区县均值写成全市官方口径，也不要把历史预测写成实时预测。
- 不要因新增组件改用另一套饱和配色或无关展示字体。
- 不要用大量珊瑚色代替选中状态的稀缺强调。

2026-11-02按用户参考论文精简：移除大屏来源段落和重复方法说明，来源保留在论文正文与README；不改变筛选、区县联动、明细导出和固定预测原点。
