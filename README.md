---
name: fortune-telling
description: Use when the user asks for fortune-telling, 算命, 八字, 周易, 易经, 六爻, 占卜, 手相, 面相, 风水, 阳宅, 飞星, divination, or wants a Ba Zi / I Ching / palm reading / Feng Shui analysis.
---

# 算命占卜 (Fortune Telling & Divination)

综合算命技能：八字命理、周易占卜、手相分析、阳宅风水。

## 快速参考

| 需求 | 命令 |
|------|------|
| 八字排盘 | `python3 scripts/bazi.py 1990-05-20 08 男` |
| 六爻铜钱卦 | `python3 scripts/iching.py coin` |
| 梅花易数(数字) | `python3 scripts/iching.py meihua 123 456 789` |
| 梅花易数(时间) | `python3 scripts/iching.py meihua time` |
| 查卦辞 | `python3 scripts/iching.py hex 1` |
| 手相分析 | `python3 scripts/palmistry.py analyze --hand=火 --life=长而深` |
| 命卦计算 | `python3 scripts/fengshui.py mingua 1990 男` |
| 八宅吉凶 | `python3 scripts/fengshui.py bazhai 1990 男` |
| 流年飞星 | `python3 scripts/fengshui.py annual 2026` |
| 综合风水 | `python3 scripts/fengshui.py full 1990 男` |
| JSON输出 | 任意命令加 `--json` |

## 八字排盘 (Ba Zi)

**用途：** 根据出生日期时间排四柱八字，分析五行旺衰、日主强弱、十神关系。

**必需参数：** 日期(YYYY-MM-DD)、小时(0-23)、性别(男/女)

```bash
python3 scripts/bazi.py 1990-05-20 08 男
```

输出包含：
- 四柱八字（年柱、月柱、日柱、时柱）
- 天干地支、阴阳五行
- 日主分析
- 十神关系（正官、七杀、正印、偏印、食神、伤官、正财、偏财、比肩、劫财）
- 纳音五行
- 五行分布统计
- 地支藏干
- 基础解读

**注意事项：**
- 月柱按节气分界（非公历月份），立春为寅月之始
- 时柱按时辰计算（23-1子时, 1-3丑时...）
- 大运为简化计算，精确排大运需节气准确日期

## 周易占卜 (I Ching)

### 六爻铜钱卦
随机掷六次铜钱，从初爻到上爻，得本卦和变卦：

```bash
python3 scripts/iching.py coin
```

有变爻（老阴/老阳）→ 生成变卦并给出综合解读
无变爻 → 仅参考本卦卦辞

### 梅花易数
数字起卦法，取三数定上下卦和动爻：

```bash
python3 scripts/iching.py meihua 12 34 56
```

时间起卦法（用当前时间）：

```bash
python3 scripts/iching.py meihua time
```

### 查看64卦

```bash
python3 scripts/iching.py list     # 列出全部64卦
python3 scripts/iching.py hex 1    # 查看第1卦「乾为天」
```

## 手相分析 (Palmistry) ⚠️ 专业标准强制

**用户明确要求专业级分析，禁止娱乐型泛泛解读。** 详见 `references/professional-palmistry.md`。

### 🔴 左右手判断（最高优先级！）

视觉模型对左右手判断**多次系统性翻车**（前置摄像头镜像导致）。**强制流程：**

1. vision_analyze 采集数据时问拇指位置
2. **出报告前必须向用户确认**：「视觉判为X手，实际上是左手还是右手？」
3. 只有确认后才做 先天/后天 框架
4. ❌ 禁止未经确认就出报告（用户原话：「赛博神算子左右都不分！」）

### 专业标准九步流程

1. **数据采集** — vision_analyze 获取精确客观数据（不问含义，只问"是什么"）
2. **五指分论** — 古典五指对应（拇指=意志/土、食指=权力/木/巽宫、中指=自我/火/离宫、无名指=审美/金、小指=口才/水/兑宫）。必做食指vs无名指长度对比
3. **三主纹精断** — 地纹(生命线)、人纹(智慧线)、天纹(感情线)，按年龄段分段解读
4. **玉柱纹(命运线)+太阳线(成功线)** — 事业核心，按出发位置/深浅变化/终点断
5. **八宫掌丘定位** — 用★评级(★平坦 ★★中等 ★★★饱满)
6. **明堂分析** — 掌心痣、特殊标记
7. **综合雷达图** — 0-10分量化事业心/执行力/创造力/领导力/社交力/表达力/抗压力/审美感
8. **事业路径精准推荐** — ✅排名推荐 + ❌明确排除，具体到岗位
9. **流年推运** — 玉柱纹分段对应年龄节点

### 关键 pitfalls

- 🔴 **禁止盲信视觉模型左右手判断**（前置摄像头自拍镜像导致系统性错误），必须先向用户确认
- ❌ 禁用俗称（"命运线""掌心"），必须用古典术语（"玉柱纹""明堂""巽宫"）
- ❌ 禁止泛泛说"适合创意工作"，必须精确到岗位级别
- ❌ 禁止只说掌丘"饱满"，必须★量化
- ❌ 禁止跳过五指分论和食指vs无名指对比
- ❌ 禁止缩水报告——九步流程缺一不可
- 🔴 **禁止盲信 vision_analyze 的左右手判断** — 视觉模型在判断左右手时不可靠，已实测连续两次将左手判为右手（"拇指在左侧=右手"的逻辑在照片镜像、角度偏差下频繁出错）。**必须先问用户确认左右手**，再开始分析。左手=先天命格，右手=后天造化，判错手=判错命。

### 查看知识库

```bash
python3 scripts/palmistry.py types    # 五行手型列表
python3 scripts/palmistry.py lines    # 主线特征解读
python3 scripts/palmistry.py mounts   # 七大掌丘说明
```

### 综合分析（脚本辅助）

```bash
python3 scripts/palmistry.py analyze \
  --hand=火 \
  --life=长而深 \
  --wisdom=长而下垂 \
  --emotion=弯曲上翘 \
  --fate=清晰深长 \
  --mounts=金星丘,太阳丘
```

脚本提供知识库输出，但**专业级解读必须AI主导**，结合 vision_analyze 实测数据和古典手相学体系

## 风水分析 (Feng Shui)

阳宅风水四大模块：命卦、八宅、玄空飞星、流年布局。

### 命卦计算

```bash
python3 scripts/fengshui.py mingua 1990 男
```

根据出生年份和性别计算命卦（东四命/西四命），输出命卦数、五行、本命方位、适合行业。

### 八宅吉凶方位

```bash
python3 scripts/fengshui.py bazhai 1990 男
```

以命卦为伏位，排八宅大游年：
- 🟢 **四吉方**：生气(上吉)、延年(上吉)、天医(中吉)、伏位(小吉)
- 🔴 **四凶方**：绝命(大凶)、五鬼(大凶)、六煞(次凶)、祸害(次凶)

每个方位输出：卦名卦象、五行、含义、适合/避免用途、配色建议。

### 流年飞星

```bash
python3 scripts/fengshui.py annual        # 当前年份
python3 scripts/fengshui.py annual 2026   # 指定年份
```

九宫飞星布局（九宫格显示），包含：
- 九星名称和属性（吉/凶/大吉/大凶）
- ✅ 吉星催旺建议（物品+原理）
- 🛡️ 凶星化解建议（物品+原理）

已内置2025、2026年精确飞星数据。

### 综合风水分析

```bash
python3 scripts/fengshui.py full 1990 男
```

一键输出：命卦 + 八宅吉凶 + 最佳方位推荐 + 流年飞星 + 五行行业建议。

## 解读原则

1. **八字以日主为核心**，看五行配合和十神格局，需结合大运流年
2. **周易重卦象变爻**，本卦为现状、变卦为趋势，爻位对应具体事体
3. **手相必须专业级** — 古典术语（玉柱纹/明堂/巽宫）+ 九步标准流程 + 实测数据 + 量化评分 + 雷达图。详见 `references/professional-palmistry.md`
4. **所有解读仅供娱乐参考**，不构成人生建议

## 常见组合用法

### 用户问"帮我算算八字"
→ `python3 scripts/bazi.py <生日> <时辰> <性别>` + AI深度解读日主旺衰和格局

### 用户问"帮我占一卦"
→ `python3 scripts/iching.py coin` + 解读本卦变卦关系

### 用户问"看看我的手相"或"看事业/感情"
→ **必须走专业九步流程**：先 vision_analyze 采集数据 → 五指论 → 三主纹 → 玉柱纹+太阳线 → 八宫 → 明堂 → 雷达图 → 精准推荐 → 流年推运

### 用户问"看寿命/能活多久"
→ **寿命专项分析**：聚焦地纹（生命线），逐项采集（起点/清晰度/断裂/岛纹/锁链纹/干扰线/终点/分叉/姐妹线），按年龄段分段精断（少年/青年/中年/中晚年/晚年），给出寿元预估区间和关键预警节点。不需要走全套九步流程，但必须地纹逐段精断。

### 用户问"今天运势如何"
→ `python3 scripts/iching.py meihua time`（梅花易数时间起卦）

### 用户问"帮我看看风水"或"怎么布局"
→ `python3 scripts/fengshui.py full <出生年> <性别>` + 结合流年飞星给出具体催旺和化解建议