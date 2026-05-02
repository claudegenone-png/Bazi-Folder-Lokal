# Yiteng (倚天) V2.6 — Consolidated Output Schema

**Software**: 倚天 [星僑] 四柱論命附加紫微斗數 V2.6
**Author**: 陳恩國 (台內著字 第72685號)
**Programmer**: 陳慶鴻
**UI**: DOS-mode 80×25 text, cyan border on dark blue, Chinese reading right-to-left for tabular pillar columns.
**Sources**: 4 reverse-engineered subjects (Michelle 1995-07-22, Tommy 1960-05-08, 胡莉莉 1964-05-03, 林文進 1998-02-27).

---

## 0. Global UI Chrome (every page)

| Element | Value |
|---|---|
| Title bar | `【星僑】 四 柱 論 命 附 加 紫 微 斗 數 V2.6 【星僑】` |
| Top menu | `A:輸入生日  B:專家命盤  C:詳細解說  D:流年判斷  E:自動列印  F:參數設定` (active letter highlighted red) |
| Bottom hot-key | `[P]:列表  [Esc]:結束  [↓]:下一行  [↑]:上一行  [PgUp]:上一頁  [PgDn]:下一頁` |
| IME / corner | `【英數】【半形】` left, `倚天` watermark right |
| Person banner | `姓名：{NAME} [{性別}] 農曆民國 {Y} 年 {M} 月 {D} 日 {H} 時 {min} 分` |
| Section heading | `─── 【 X 】 ───` yellow text + cyan dashes |
| Bullets | `◎` yellow (paragraph), `※` (definitions), `○` (sub-keys), `●` (卦格 marker) |
| Star-name bracket | `【name】` red |

Chart-only footers:
- 12-palace board: `[P]:印表 [space] 或 [ESC]:結束`
- Palace-zoom view: `[P]:印表  ←→:移動宮位  [space]:回主畫面`
- 流年表 (10-yr grid): `[P]:列表 [Esc]:結束 [←]:上一頁 [↵]:下一頁`

Color encoding (consistent across all 4 subjects):
- Yellow/gold: section banners, ◎ bullets, palace ribbons
- Cyan: borders, labels (天干/地支/小限), grid frames
- Red: 神煞 in 【】, current-palace highlight (命宮/父母/etc), active menu key, palace name when matching cursor
- White: body text, star main-names
- Green: body narrative on some pages, year line `◎ 西元 …`
- Magenta/pink: ages and 大運 numbers
- 廟旺得利平不陷 markers (brightness): printed beside main-star name

---

## 1. INPUT FIELDS (page A: 輸入生日)

| Field | Format | Notes |
|---|---|---|
| 姓名 | string | rendered both in cover and footer banner |
| 性別 | 男/女 → 男陽 / 陰女 (Yang/Yin per stem of birth-year) | Michelle = 陰女 (乙=Yin), Tommy = 陽男 (庚=Yang), 胡 = 陽女 (甲=Yang), 林 = 男陽 (戊=Yang) |
| 西元 | YYYY | |
| 國曆民國 | 民國 N 年 M 月 D 日 H 時 (mm 分) | N = 西元 − 1911 |
| 農曆民國 | 民國 N 年 M 月 D 日 H 時 mm 分 (干支年 e.g. 甲辰) | computed via lunar conversion |
| 星期 | 日/一/…/六 | Saturday → 星期六, Sunday → 星期日, Tuesday → 星期二, Friday → 星期五 |
| 屬X | 鼠/牛/虎/兔/龍/蛇/馬/羊/猴/雞/狗/豬 | derived from 農曆 year-branch |

---

## 2. BAZI MASTER PAGE (B 專家命盤 → 四柱)

Header: `男/女 陰/陽 【星僑】 命 論 柱 四 【星僑】 屬X`

### 2.1 Four Pillars Block (vertical, columns read R→L: 時 / 日 / 月 / 年; subject-display sometimes adds a leftmost 命宮 column making 5 columns)

Row | Content | Examples
---|---|---
Header label (十神 of stem vs 日主) | 偏官/正財/命主/正財/七殺 etc. Day stem column is `命主` | Tommy: 偏官/命主/正財/偏財; Michelle: 七殺/命主/正印/劫財 (per pillar layout 辛甲癸乙); 林: 七殺/命主/劫財/正財; 胡: 比肩/命主/偏財/比肩
天干 | 1 char | e.g. Tommy 庚辛丙己
地支 | 1 char | e.g. Tommy 子巳亥丑
藏干 | up to 3 chars per branch (本氣 + 中氣 + 餘氣) | 子→癸; 寅→戊丙甲; 巳→庚戊丙; 午→丁己; 未→乙己丁; etc.
副星 (藏干 ten-gods vs day-master) | up to 3 ten-god labels stacked, two-char each | each hidden stem mapped via 五合/十神 to day-master

Optional 命宮 column to LEFT of 年柱: shows 命宮 stem-branch (BaZi 命宮 干支, NOT Zi Wei palace), with same 十神/藏干 stack. Computed: 命宮 = (寅 + 月支 + 時支) mod 12 method (standard 子平 命宮 公式).

### 2.2 日主旺度 panel (centre-right)
- `+X.XXX` (positive supportive sum)
- `−Y.YYY` (negative depleting sum)
- Label `日主旺度`

Observed values:

Subject | + | − | Net
---|---|---|---
Michelle (甲寅 day) | (not extracted, +/− present) | | 
Tommy (辛巳 day) | +2.238 | −6.440 | −4.202 (very weak 辛)
胡莉莉 (戊辰 day) | +6.186 | −2.518 | +3.668 (strong 戊)
林文進 (乙巳 day) | +3.876 | −5.060 | −1.184 (slightly weak 乙)

### 2.3 卦格 / 用事 row (between gauge and 大運)
Format: `●{派格} {祿/刃/etc}` then `{某}用事` then label `卦格`.

Observed:
- Michelle: (not visible in extract — likely `劫財用事` since 甲 day with 月令未 餘氣劫財 乙)
- Tommy: `●運巽祿` / `偏財用事` (辛 day, 甲 in 巳 餘氣 → 正財; 月支亥 中氣甲=正財, +生時 庚子 偏財; choosing 偏財 as 用事 because 月支亥本氣壬=傷官… actually per software it picks the 旺氣 stem in 月令 hidden stems against 日干: gives 偏財)
- 胡莉莉: `○偏乾財` / `偏財用事` (戊 day, 月支寅 本氣甲 → 七殺/木; but printed as 偏財用事 — note schema records it literally, deeper rule in formula doc)
- 林文進: `●羊刃坤刃` / `劫財用事` (乙 day, 月支寅 餘氣甲=劫財; 寅 also cluster with 卯 type — 羊刃 marker)

### 2.4 五行 旺相死囚休 panel
Five labels `旺 / 相 / 死 / 囚 / 休` paired with the 5 elements in order of seasonal status.

Hu's example: `囚 木 / 休 火 / 旺 土 / 相 金 / 死 水` (戊 day, 月支寅 春 → traditional 春木旺火相土死金囚水休; but Yiteng prints from 日主 perspective — actually it's seasonal element vs 月令 not vs 日主).

林's example: `旺 木火 / 相 土金 / 死 水` (春令: 木旺火相 — different layout: pairs of elements per status).

Schema: dict `{element → status}` where status ∈ {旺,相,休,囚,死}. Determined purely by 月令 (month branch).

### 2.5 喜用神 / 用神 / 喜神 / 閒神 / 仇神 / 忌神
5-row block, each row labels 1–2 elements (out of 木火土金水).

Subject | 喜用神 | 用神 | 喜神 | 閒神 | 仇神 | 忌神
---|---|---|---|---|---|---
Michelle | — | — | — | — | — | — (not in extract; default per 甲寅 weak in 未月 火土旺 → likely 用水 喜木)
Tommy | 土木 | 土木 | (merged) | 火 | 金 | 水
胡莉莉 | 火土 | 火土 | (merged) | 金 | 水 | 木
林文進 | 火 | 火 | 木 | 水 | 土 | 金

(Yiteng sometimes collapses 喜用神 = 用神 + 喜神 into one row.)

### 2.6 大運 ladder (10-year cycles)
- Top label: `每逢 {X或Y}年 {節氣} 後 {N} 天交大運` (起運 timing rule — see Formula doc §E)
- Row of ages: e.g. `3 13 23 33 43 53 63 73 83 93` (start age = 起運歲)
- Row of 干支: 10 stem-branches following 月柱 forward (陽男陰女) or backward (陰男陽女)
- Row of 十神 (大運 stem vs day-master)
- Row of 副星 (大運 branch hidden stems → 十神, stacked)

Observed start-ages: Tommy 9 → cycle starts at 10 (壬午); 胡 11 → 11丁卯; 林 3 → 3乙卯; Michelle 27 → 丙戌 (the cycle current age 27-36; start age likely also 27).

### 2.7 先天體質 / 先天體神 panel (10-organ scores)
10 rows fixed mapping to the 10 天干 → organ in Chinese medicine:

Stem | Organ | 五行 | Yin/Yang
---|---|---|---
甲 | 膽 | 木 | 陽
乙 | 肝 | 木 | 陰
丙 | 小腸 | 火 | 陽
丁 | 心 | 火 | 陰
戊 | 胃 | 土 | 陽
己 | 脾 | 土 | 陰
庚 | 大腸 | 金 | 陽
辛 | 肺 | 金 | 陰
壬 | 膀胱 | 水 | 陽
癸 | 腎 | 水 | 陰

Each organ shows integer score. Range observed: 0–8.

Subject | 甲 | 乙 | 丙 | 丁 | 戊 | 己 | 庚 | 辛 | 壬 | 癸
---|---|---|---|---|---|---|---|---|---|---
Tommy | 1 | 0 | 2 | 0 | 1 | 2 | 1 | 1 | 1 | 1
胡 | 4 | 1 | 2 | 0 | 4 | 0 | 0 | 1 | 0 | 3
林 | 3 | 4 | 7 | 6 | 5 | 0 | 2 | 1 | 6 | 8

(Michelle scores not visible in extract.)

### 2.8 神煞 panel (BaZi-side 神煞, may overlap with cross-pillar markers)
Listed with `將星 / 劫煞 / 亡神 / 天乙貴人 / 元辰大耗 / 孤辰 / 從掃` etc., each followed by descriptive sentence.

### 2.9 命宮 干支 (BaZi 命宮)
Single 2-char label, e.g. 胡 = 丙子. Computed = 14 − (月支 + 時支) mod 12 (standard formula).

---

## 3. BAZI NARRATIVE PAGES (C 詳細解說 group)

Triggered automatically; one page per topic. Order observed: 神煞 → 全局總論 → 性情 → 財富 → 陽宅 → 事業 → 婚配 → (Zi Wei narratives) → 古書云.

### 3.1 神煞 — Per-神煞 paragraph triggers

Each 神煞 lookup keyed by NAME, fixed text. Triggers when subject possesses that 神煞 from cross-pillar test (年支/日支 vs other pillars).

Examples observed:
- 將星 (Tommy)
- 劫煞 (Michelle, Tommy, 林)
- 亡神 (Tommy)
- 天乙貴人 (Michelle, Tommy)
- 孤辰 (Michelle, 林)
- 從掃 (Michelle, 胡)
- 元辰大耗 (Tommy)

Text is pre-canned per 神煞 name. Script merely lists those that triggered.

### 3.2 全局總論 — Pattern-triggered relationship outcomes

Fixed slot-based sentences about: 配偶 / 兒子 / 母親 / 父親 / 兄弟 / 姊妹 / 領導力 / 健康忠告 / 性格收尾.

Triggered by 十神 strength of: 正官/七殺 (子女 for 女, 工作 for 男), 正印/偏印 (母), 正財/偏財 (妻 for 男), etc., crossed with whether they are 用神 or 忌神.

Examples:
- "配偶的操作能力強，但有內向的個性。" (Michelle, 胡 same — both 甲 day-master; trigger: 配星 strong but 性 quiet)
- "配偶較不重感情, 較會花錢。" (Tommy — 辛 day, 配偶=正財乙/巳藏 weak)
- "兒子的名氣會比較好、又乖。" (Michelle), "兒子聰明, 比較外向。" (Tommy), "兒子比較不聽話。" (林), "兒子的操作能力強，較固執。" (胡)
- "較不擅於思考。" (Michelle, 胡 — 印星弱)
- "有始無終，虎頭蛇尾，做事有頭無尾。" (Michelle, Tommy — 七殺/食傷 imbalance)
- "離鄉背井，會搬離出生地較遠的地方居住。" (胡, 林 — 驛馬星 in 命宮/年柱)
- "易患胸疾..." (Tommy — 五行 缺/過多 specific)

### 3.3 性情 — 4-paragraph block. Each paragraph keyed to one of the strongest 十神 in chart.

Mapping inferred:
- ◎1: 食神 / 傷官 dominant theme (creativity / expression)
- ◎2: 財星 dominant (wealth attitude)
- ◎3: 官殺 dominant (authority/discipline)
- ◎4: 印 / 比劫 dominant (self / nurture)

Observed: Michelle and 胡 share 4 nearly-identical paragraphs because both are 甲/戊 with similar 十神 distribution; Tommy & 林 different sets.

### 3.4 財富 — fixed 4-line schema:
1. `偏財源{豐厚/不豐厚}, 有錢{存得住/存不住}, 要買不動產才保得住。`
2. `與偏財關係{密切/疏遠}, {容易/不易}得到。`
3. `正財源{豐厚/不豐厚}, ...`
4. `與正財關係{密切/疏遠}, {容易/不易}得到。`
5. `※ 正財: ...   偏財: ...` (definition footer, always)

Each variable has 2 states → 16 combinations encoded by:
- 豐厚/不豐厚 → strength of 財星 in 五行 sum
- 容易/不易 → 財星 是否被 比劫剋
- 密切/疏遠 → 財星 出干 vs 藏支

### 3.5 陽宅 — keyed by 日主 element → 卦. 8卦 lookup:
- 甲乙木 → 震/巽
- 丙丁火 → 離
- 戊己土 → 坤/艮 / 乾(Hu)
- 庚辛金 → 兌/乾
- 壬癸水 → 坎 (Michelle 甲 → printed 坎)

Each 卦 has fixed paragraph: 宅向 / 神位 / 門路 / 爐灶 / 房間 / 床位 / 坑廁 directions.

Observed: Michelle 坎卦; Tommy 巽卦; 胡 乾卦; 林 (likely 艮卦 — text shows 艮 directions).

### 3.6 事業 — 2 ◎ paragraphs. First = 喜用神 element industries; second = 忌神/閒神 element industries (or 仇神 alternative).

Industries-by-element table inferable from samples (火 → 工廠/光學/美容/化妝品; 木 → 文具/出版/木材/教育; 土 → 建築/房地產/古董; 水 → 流動攤販/航海/冷凍; 金 → 金融/機械; — Michelle 火+土 paragraphs; Tommy 木+土 paragraphs; 胡 火+土; 林 火+水).

### 3.7 婚配 — 2-line forbidden + 2-line preferred:
- `忌：配相{X}、{Y}、…`
- (consequence sentence, fixed pool)
- `宜：配相{A}、{B}大吉相{C}吉以相半其他次吉。`
- (prosperity sentence, fixed pool)

Forbidden 屬 = 沖/害/刑 of 年支. Preferred = 三合/六合.

Year-branch | 沖 (forbidden core) | 三合 (preferred core)
---|---|---
亥(Michelle) | 巳 (蛇) | 卯未 (兔羊)
子(Tommy) | 午 (馬) | 申辰 (猴龍)
辰(胡) | 戌 (狗) | 申子 (猴鼠)
寅(林) | 申 (猴) | 午戌 (馬狗)

Matches observed: Michelle 忌蛇猴豬, 宜羊兔虎; Tommy 忌羊馬兔雞, 宜龍猴牛; 胡 忌牛兔狗龍, 宜鼠猴雞; 林 忌蛇猴, 宜馬狗豬.

### 3.8 古書云 — 4–5 classical citations keyed strictly by 日主天干:

日主 | sources
---|---
甲 | 三命通會 詩(甲乙貴乎木...), 滴天髓(甲木參天...), 月令詩 (specific to 月支), 木天干作首排...
乙 | 三命通會, 青龍狀形詩, 滴天髓(乙木雖柔...), 月令詩, 木根紫種...
丙 | 三命通會, 朱雀乘風詩, 滴天髓(丙火猛烈...), 月令詩, 火明明一太陽...
丁 | parallel structure
戊 | 三命通會 詩(戊己貴乎...), 滴天髓(戊土固重), 月令詩
己 | parallel
庚 | parallel
辛 | parallel
壬 | parallel
癸 | parallel

Plus 月令-specific 詩 chosen by 月支 (12 options per 日主 × 12 months = canned text table).

Michelle (甲日 未月) and 胡 (甲日 寅月) and 林 (乙日 寅月) all show 三命通會 + 滴天髓 + 月令詩 + 五言.

---

## 4. ZI WEI MASTER 12-PALACE BOARD

Layout: 4×4 grid; outer 12 cells = palaces (clockwise from 命宮); inner 2×2 = central info cartouche.

### 4.1 Central cartouche fields
- Top banner: `★☆★ 紫微論命 ★☆★` flanked by `屬X`
- `{陰陽}{男/女}` and `姓名: {NAME}`
- `西元 {Y} 年   星期{D}`
- `國曆民國 {N} 年 {M} 月 {D} 日 {H} 時生`
- `農曆{干支} {N} 年 {M} 月 {D} 日 {H} 時生`
- `時日月年` row → 4 stems on next row (R→L), 4 branches on row after
- `○命主：{star}    ○命宮：{branch}` — 命主 derived from 命宮 branch (子→貪狼, 丑亥→巨門, 寅戌→祿存, 卯酉→文曲, 辰申→廉貞, 巳未→武曲, 午→破軍)
- `○身主：{star}    ○身宮：{branch}` — 身主 derived from 年支 (子午→火星, 丑未→天相, 寅申→天梁, 卯酉→天同, 辰戌→文昌, 巳亥→天機)
- `○五行：{木三/火六/土五/金四/水二}局`
- `○子年斗君：{branch}`
- 四化 (本命四化, by 年干): `○{star}：化祿  ○{star}：化權`  / `○{star}：化科  ○{star}：化忌`
- Footer: `作者：陳恩國   合内庵字第 72685 號`

四化 by 年干 (lookup table):
- 甲: 廉祿 破權 武科 太陽忌
- 乙: 天機祿 天梁權 紫微科 太陰忌  ← Michelle (乙亥年)
- 丙: 同祿 機權 昌科 廉忌
- 丁: 陰祿 同權 機科 巨忌
- 戊: 貪祿 陰權 弼科 機忌
- 己: 武祿 貪權 梁科 曲忌
- 庚: 陽祿 武權 陰科 同忌  ← Tommy (庚子年): 太陽祿 武曲權 太陰科 天同忌 ✓
- 辛: 巨祿 陽權 曲科 昌忌
- 壬: 梁祿 紫權 左科 武忌
- 癸: 破祿 巨權 陰科 貪忌

Subject confirmations:
- Michelle 乙年 → 機祿 梁權 紫科 陰忌 ✓
- 胡 甲辰年 → 廉祿 破權 武科 陽忌 ✓
- Tommy 庚子年 → 陽祿 武權 陰科 同忌 ✓
- 林 戊寅年 → would be 貪祿 陰權 弼科 機忌 (not in extract)

### 4.2 Per-palace cell schema

Each cell shows up to 5 horizontal text lines + 1 footer row:

```
{主星 with 廟旺得利平閒陷} {副星-row1}
{副星-row2}                {小限 1-yr triggers row}
{副星-row3}                
{副星-row4}                
{12長生} {博士12神} {太歲12神}{流年將前12神}{歲前12神} 【{宮名}】 {大限-trio} {墓宿等}
{大限 age band  {干支}}     {小限 number}
```

- 主星: up to 2 of the 14 主星 (紫微/天機/太陽/武曲/天同/廉貞/天府/太陰/貪狼/巨門/天相/天梁/七殺/破軍) + brightness `廟/旺/得/利/平/閒/陷/不`
- 副星: lesser stars across 6 categories (六吉: 文昌文曲左輔右弼天魁天鉞; 六煞: 擎羊陀羅火星鈴星地空地劫; 四化 markers: 祿權科忌 small label; 雜曜: 紅鸞天喜天馬天姚天哭天虛 etc.)
- 神煞: 將前12神 (將星攀鞍歲驛息神華蓋劫煞災煞天煞指背咸池月煞亡神) starting from 三合 of 年支; 歲前12神 (太歲晦氣喪門貫索官符小耗大耗龍德白虎天德弔客病符) starting from 年支
- 大限: 6+10*(N) age band (e.g. 6-15, 16-25, …) — clockwise from 命宮 for 陽男陰女, counter for else
- 小限: per-year wheel (5 numbers shown means ages a, a+12, a+24, ...). Starting palace from 年支 (寅午戌→辰; 申子辰→戌; 巳酉丑→未; 亥卯未→丑)
- 干支 of palace: based on 年干 + 月支 via 五虎遁 lookup
- Highlight: red text on dark for current cursor palace and for `命宮 / 父母 / 福德 / 田宅 / 官祿 / 夫妻 / 兄弟 / 子女 / 財帛 / 疾厄 / 遷移 / 僕役` when matching that palace name

### 4.3 12-palace name sequence (clockwise from 命宮)
命宮 → 兄弟 → 夫妻 → 子女 → 財帛 → 疾厄 → 遷移 → 僕役 → 官祿 → 田宅 → 福德 → 父母

### 4.4 Subject confirmations

Subject | 命宮 | 身宮 | 命主 | 身主 | 五行局 | 子年斗君
---|---|---|---|---|---|---
Michelle | 子(戊子) | 寅 | 貪狼 | 天機 | 火六局 | 寅
Tommy | 午(壬午) | 辰 | 破軍 | 火星 | 木三局 | 申
胡莉莉 | 辰(丙子-printed; per chart 命宮辰) | 辰 | 廉貞 | 文昌 | 木三局 | 戌
林文進 | (not in extract; computed from 卯月 巳時 → 命宮 酉)

### 4.5 Zoom view (PgDn from chart)
Same chart cropped to 4 palaces around cursor + central cartouche, with extra labels: `本宮 / 對宮 / 左宮 / 右宮` (current / opposite / triangle-trine palaces).

---

## 5. ZI WEI PALACE NARRATIVES (12 + 宿命)

Pages: 命宮 → 兄弟 → 夫妻 → 子女 → 財帛 → 疾厄 → 遷移 → 僕役 → 官祿 → 田宅 → 福德 → 父母 → 宿命

Each palace narrative composed of 1–4 paragraphs, indexed by:
1. **Primary trigger**: dominant 主星 in that palace (e.g. 命宮 has 天機 → "像流水般永無休止..." (Michelle)).
2. **Co-occurrence modifiers**: paragraphs starting with `與{Star}同宮者...` or `如有{Star}同宮...` appended when secondary stars present.
3. **Branch modifier**: `位於{branch}之宮內者...` paragraphs added when palace falls in specific branches.
4. **Brightness modifier**: 廟旺 → fortunate variant; 陷不 → cautionary variant.
5. **Gender modifier**: separate `女性...` paragraph when applicable.
6. **凶星/吉星 conditional**: `如有凶星阻礙...` branches.

Observed pattern: 命宮 narrative is longest (4–8 lines); 兄弟/夫妻/子女 etc. shorter; 宿命 is 2–3 lines summary referencing 命宮 + 福德/身宮 strength.

### Paragraph triggers extracted (cross-subject)
- `像流水般永無休止...` → 命宮 with 天機 (Michelle 命主貪狼 but 命宮 actually has 天機 by chart layout; trigger = 天機 in 命宮)
- `就像盛夏豔陽的陽光一般...` → 命宮 with 太陽 (Tommy: 命宮 午, 但實 chart 主星 破軍; the 命宮 narrative paragraph maps via secondary trigger or by 身主 — needs more samples)
- `禮尚往來, 儀禮周到的友情` → 兄弟宮 with specific star
- `愛情運一帆風順` → 夫妻宮 with 太陽/太陰 廟旺 (胡)
- `集福德於身, 是慷慨又瀟灑的人` → 福德宮 with 紫微 (Michelle)
- `能將天賦的能力發揮得淋漓盡致` → 宿命 standard intro when 命宮+身宮 same trine

(Full mapping requires 14主星 × 12palaces × brightness = ~500 canned paragraphs database; partial inference only.)

### 宿命 page
Always 2–3 paragraphs. First always summarises 命宮 strength. Always mentions 命宮/職業宮/移動宮/福德宮 cross-checking. Pure deterministic from 命宮+身宮+福德 strengths.

---

## 6. 大運 DETAIL TABLE (D 流年判斷 → 流年易鑑表)

One sheet per 10-year 大運. Layout:

| Column right→left | Header (current 大運) | year a | a+1 | a+2 | … | a+9 |
|---|---|---|---|---|---|---|
| Top label | `每逢 {X或Y}年 {節氣} 後 {N} 天交大運` | | | | | |
| 十神 (vs 日主) | 大運 ten-god | year ten-god (top) | … | | | |
| 年齡 | range a–(a+9) | a | a+1 | … | | |
| 干支 | 大運 干支 | year 干支 | … | | | |
| 副星 (藏干 ten-gods, stacked 2-char per sub-stem) | … | … | … | | | |
| 十二長生 (stem 長生十二宮) | 養/胎/絕/墓/死/病/衰/帝旺/臨官/冠帶/沐浴/長生 | per-year | | | | |
| 神煞 row 1 (年柱-derived) | 寡宿/華蓋/羊刃/驛馬/桃花/天乙/孤辰/將星/金輿/元辰/紅鸞/文昌/天亡乙神/劫煞/干祿 | | | | | |
| 神煞 row 2 (歲前12神) | 太歲/晦氣/喪門/貫索/官符/小耗/大耗/龍德/白虎/天德/弔客/病符 / + 太陰/太陽/福德/歲破/死符/天狗 | | | | | |

Examples:
- Tommy 60–69: 大運 丁亥 (劫財), 起運 `每逢 己或甲年 白露 後 12 天交大運`
- Tommy 70–79: 大運 戊子 (食神, actually 正官 vs 辛 — schema printed 食神; possibly typo in extract)
- 胡 51–60: 大運 癸亥 (正印), 起運 `每逢甲或己年 穀雨 後 3 天交大運`
- 胡 61–70: 大運 壬戌 (偏印)
- 林 23–32: 大運 丁巳 (食神), 起運 `每逢 庚或乙年 小滿 後 2 天交大運`
- 林 33–42: 大運 戊午 (正財)
- Michelle 27–36: 大運 丙戌 (食神), 起運 `辛亥 或 丙年 雨水 後 2 天交大運`

---

## 7. 流年 ANNUAL NARRATIVES (D 流年判斷 per-year)

Pages: one per 流年 (5 years observed per subject 2026–2030/31).

Header: `─── 【 流 年 】 ───`
First line: `◎ 西元 {Y} 年  民國 {N} 年  歲次{干支}  {age} 歲`

Body composed of:
1. **Effort/return line** — 4 templates:
   - "今年用腦所想出來的事物，表面上能與金錢成對比。"
   - "今年所付出的勞力，表面上與金錢能成對比。"
   - "今年所付出的勞力與腦力，表面上看起來能與金錢成對比。"
   - "今年所付出的代價，表面上與金錢能成對比。"
   - "今年的壓力會比較大..."
   - "今年所付出的勞力與腦力，表面上不能與金錢成對比。"
2. **Outcome line** — pool: 達到理想 / 實質上不能達到 / 得到貴人 / 得到一切機緣 / 注意身體 etc.
3. **Optional secondary lines** — 大環境/事業/心情/夫妻 status flags
4. **將前神煞 verse** — `{name}：{4-line 5-char poem}` (canned for 12 將前): 太歲/晦氣/喪門/貫索/官符/小耗/大耗/龍德/白虎/天德/弔客/病符 + 龍德/歲破/死符/福德/天狗/太陽/太陰
5. **歲前神煞 verse** — `{name}：流年{name}星{...}` extended verse with 忌月/防注意 line
6. **Personality summary** — 1 paragraph keyed to 流年 干支 (60 templates)

Trigger logic for items 4–5: standard 太歲/將前12神 wheel based on (年支 of 流年) starting position; 歲前12神 likewise.

---

## 8. JSON SKELETON

```json
{
  "input": {
    "name": "string",
    "name_hanzi": "string",
    "gender": "男|女",
    "yin_yang": "陰|陽",
    "solar": {"year": 1995, "month": 7, "day": 22, "hour": 14, "minute": 0, "weekday": "六"},
    "minguo": {"year": 84, "month": 7, "day": 22, "hour": 14, "minute": 0},
    "lunar": {"ganzhi_year": "乙亥", "year": 84, "month": 6, "day": 25, "hour": 14, "minute": 48, "leap": false},
    "zodiac": "豬"
  },

  "bazi": {
    "pillars": {
      "year":  {"stem": "乙", "branch": "亥", "hidden": ["壬","甲"], "ten_god_stem": "劫財", "ten_gods_hidden": ["偏印","比肩"]},
      "month": {"stem": "癸", "branch": "未", "hidden": ["己","乙","丁"], "ten_god_stem": "正印", "ten_gods_hidden": ["正財","劫財","傷官"]},
      "day":   {"stem": "甲", "branch": "寅", "hidden": ["甲","丙","戊"], "ten_god_stem": "命主", "ten_gods_hidden": ["比肩","食神","偏財"]},
      "hour":  {"stem": "辛", "branch": "未", "hidden": ["己","乙","丁"], "ten_god_stem": "正官", "ten_gods_hidden": ["正財","劫財","傷官"]}
    },
    "ming_gong": {"stem": "戊", "branch": "子"},
    "rizhu_strength": {"plus": 2.238, "minus": -6.440, "net": -4.202, "category": "弱"},
    "wuxing_season": {"木":"囚","火":"休","土":"旺","金":"相","水":"死"},
    "yong_shen": {"喜用神":["土","木"], "用神":["土","木"], "喜神":[], "閒神":["火"], "仇神":["金"], "忌神":["水"]},
    "gua_ge": {"label": "偏財用事", "marker": "●運巽祿"},
    "tijian": {"甲膽":1,"乙肝":0,"丙小腸":2,"丁心":0,"戊胃":1,"己脾":2,"庚大腸":1,"辛肺":1,"壬膀胱":1,"癸腎":1},
    "shen_sha": ["將星","劫煞","亡神","天乙貴人","元辰大耗"],
    "da_yun": {
      "start_age": 9,
      "transition_rule": "每逢己或甲年白露後12天交大運",
      "cycles": [
        {"age": 10, "ganzhi": "壬午", "ten_god_stem": "正官", "hidden_ten_gods": ["..."]},
        {"age": 20, "ganzhi": "癸未", "ten_god_stem": "偏印", "hidden_ten_gods": ["..."]}
      ]
    }
  },

  "bazi_narratives": {
    "shen_sha": [{"name": "劫煞", "text": "聰明敏捷..."}],
    "quan_ju": ["配偶...", "兒子..."],
    "xing_qing": ["◎...", "◎...", "◎...", "◎..."],
    "cai_fu": {"pian_cai_source": "不豐厚", "pian_cai_relation": "疏遠", "pian_cai_get": "容易",
               "zheng_cai_source": "不豐厚", "zheng_cai_relation": "密切", "zheng_cai_get": "容易"},
    "yang_zhai": {"gua": "坎卦", "directions": {"宅":"...","神位":"...","門路":"...","爐灶":"...","房間":"...","床位":"...","坑廁":"..."}},
    "shi_ye": ["paragraph1", "paragraph2"],
    "hun_pei": {"forbidden_zodiac": ["蛇","猴","豬"], "forbidden_text": "...",
                "preferred_zodiac": ["羊","兔","虎"], "preferred_text": "..."},
    "gu_shu_yun": ["三命通會註：...", "詩曰：...", "滴天髓云：...", "詩云：...", "..."]
  },

  "ziwei": {
    "ming_gong_branch": "子",
    "shen_gong_branch": "寅",
    "ming_zhu": "貪狼",
    "shen_zhu": "天機",
    "wuxing_ju": "火六局",
    "zinian_doujun": "寅",
    "sihua_birth": {"祿": "天機", "權": "天梁", "科": "紫微", "忌": "太陰"},
    "palaces": {
      "命宮": {
        "branch": "子", "ganzhi": "戊子",
        "main_stars": [{"name": "天機", "brightness": "廟"}],
        "minor_stars": ["天魁","祿存"],
        "sihua_local": [],
        "shen_sha": ["大耗","咸池","晦氣"],
        "da_xian": "6-15",
        "xiao_xian": [2, 14, 26, 38, 50],
        "twelve_changsheng": "胎",
        "shi_er_shen": ["伏兵","咸池"]
      }
    }
  },

  "ziwei_narratives": {
    "命宮": "...",
    "兄弟": "...",
    "夫妻": "...",
    "子女": "...",
    "財帛": "...",
    "疾厄": "...",
    "遷移": "...",
    "僕役": "...",
    "官祿": "...",
    "田宅": "...",
    "福德": "...",
    "父母": "...",
    "宿命": "..."
  },

  "da_yun_tables": [
    {
      "age_range": [27,36],
      "ganzhi": "丙戌",
      "ten_god_stem": "食神",
      "hidden_ten_gods": ["傷官","正財","偏財"],
      "twelve_changsheng": "養",
      "shen_sha": ["寡宿","華蓋","病符"],
      "transition_rule": "辛亥或丙年雨水後2天交大運",
      "annual": [
        {"age": 27, "year": 2021, "ganzhi": "辛丑", "ten_god_stem": "正官",
         "hidden_ten_gods": ["正印","偏財"], "twelve_changsheng": "冠帶",
         "shen_sha_1": ["天乙"], "shen_sha_2": ["喪門"]}
      ]
    }
  ],

  "liu_nian_narratives": [
    {
      "year": 2026, "minguo": 115, "ganzhi": "丙午", "age": 32,
      "effort_line": "今年用腦所想出來的事物...",
      "outcome_lines": ["能用思考想出一切事物..."],
      "shen_sha_1": {"name": "龍德", "verse": "龍德入命來..."},
      "shen_sha_2": {"name": "天掃", "verse": "流年天掃星逢運..."},
      "personality_summary": "生性較為急躁..."
    }
  ]
}
```
