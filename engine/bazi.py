#!/usr/bin/env python3
"""
八字排盘 (Ba Zi / Four Pillars of Destiny) Calculator
支持：四柱八字、五行、十神、纳音、大运、流年
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# ============================================================
# 常量定义
# ============================================================

# 十天干
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二地支
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十二生肖
SHENG_XIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 五行对应天干
GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
}

# 五行对应地支
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"
}

# 地支藏干
ZHI_CANG_GAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# 天干阴阳
GAN_YINYANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴", "戊": "阳",
    "己": "阴", "庚": "阳", "辛": "阴", "壬": "阳", "癸": "阴"
}

# 地支阴阳
ZHI_YINYANG = {
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴", "辰": "阳", "巳": "阴",
    "午": "阳", "未": "阴", "申": "阳", "酉": "阴", "戌": "阳", "亥": "阴"
}

# 十神关系（日干 vs 其他天干）
# 同我，阴阳相同=比肩，阴阳不同=劫财
# 我生，阴阳相同=食神，阴阳不同=伤官
# 我克，阴阳相同=偏财，阴阳不同=正财
# 克我，阴阳相同=偏官(七杀)，阴阳不同=正官
# 生我，阴阳相同=偏印(枭神)，阴阳不同=正印
def get_shishen(rigan: str, other_gan: str) -> str:
    """计算十神"""
    wuxing_ri = GAN_WUXING[rigan]
    wuxing_ot = GAN_WUXING[other_gan]
    yy_ri = GAN_YINYANG[rigan]
    yy_ot = GAN_YINYANG[other_gan]
    same_yy = yy_ri == yy_ot
    
    if wuxing_ri == wuxing_ot:
        return "比肩" if same_yy else "劫财"
    
    # 生克关系
    sheng_ke = {
        ("木", "火"): "sheng", ("火", "土"): "sheng", ("土", "金"): "sheng",
        ("金", "水"): "sheng", ("水", "木"): "sheng",
        ("木", "土"): "ke", ("土", "水"): "ke", ("水", "火"): "ke",
        ("火", "金"): "ke", ("金", "木"): "ke",
    }
    
    relation = sheng_ke.get((wuxing_ri, wuxing_ot))
    if relation == "sheng":
        return "食神" if same_yy else "伤官"  # 我生
    elif sheng_ke.get((wuxing_ot, wuxing_ri)) == "sheng":
        return "偏印" if same_yy else "正印"  # 生我
    elif relation == "ke":
        return "偏财" if same_yy else "正财"  # 我克
    else:
        return "七杀" if same_yy else "正官"  # 克我

# 纳音五行
NAYIN = [
    ("海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火"),
    ("涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土"),
    ("霹雳火", "松柏木", "流年水", "沙中金", "山下火", "平地木"),
    ("壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金"),
    ("桑柘木", "柘榴木", "大海水", "石榴木", "大海水", None),
]

def get_nayin(gan_idx: int, zhi_idx: int) -> str:
    """获取纳音"""
    idx = (gan_idx // 2) * 6 + zhi_idx // 2
    row = idx // 6
    col = idx % 6
    return NAYIN[row][col]

# 二十四节气近似日期（用于月柱计算）
# 每月两个节气，第二个为"中气"，决定月份
JIEQI_MONTH = [
    # (month_start_day, month_end_day, chinese_month_name, zhi_index)
    # 农历月从立春开始：寅月(正月) = 立春→惊蛰
    (2, 4),   # 立春 ~2.4 → 寅月
    (3, 6),   # 惊蛰 ~3.6 → 卯月
    (4, 5),   # 清明 ~4.5 → 辰月
    (5, 6),   # 立夏 ~5.6 → 巳月
    (6, 6),   # 芒种 ~6.6 → 午月
    (7, 7),   # 小暑 ~7.7 → 未月
    (8, 8),   # 立秋 ~8.8 → 申月
    (9, 8),   # 白露 ~9.8 → 酉月
    (10, 8),  # 寒露 ~10.8 → 戌月
    (11, 8),  # 立冬 ~11.8 → 亥月
    (12, 7),  # 大雪 ~12.7 → 子月
    (1, 6),   # 小寒 ~1.6 → 丑月
]

# 节气精确日期（更准确的节气日期表，用于月柱计算）
# 格式：(month, day_range_start, day_range_end)
JIEQI_PRECISE = [
    (2, 3, 5),   # 立春 2.3-2.5
    (3, 5, 7),   # 惊蛰 3.5-3.7
    (4, 4, 6),   # 清明 4.4-4.6
    (5, 5, 7),   # 立夏 5.5-5.7
    (6, 5, 7),   # 芒种 6.5-6.7
    (7, 6, 8),   # 小暑 7.6-7.8
    (8, 7, 9),   # 立秋 8.7-8.9
    (9, 7, 9),   # 白露 9.7-9.9
    (10, 7, 9),  # 寒露 10.7-10.9
    (11, 7, 9),  # 立冬 11.7-11.9
    (12, 6, 8),  # 大雪 12.6-12.8
    (1, 5, 7),   # 小寒 1.5-1.7
]


# ============================================================
# 核心计算函数
# ============================================================

def calc_year_gz(year: int) -> Tuple[int, int]:
    """
    计算年干支索引
    以甲子年(4)为基准：1984年是甲子年
    """
    base = 1984
    offset = (year - base) % 60
    return offset % 10, offset % 12


def calc_month_gz(year: int, month: int, day: int, year_gan_idx: int) -> Tuple[int, int]:
    """
    计算月干支索引
    月支由节气决定，月干由年干推出（五虎遁）
    """
    # 确定月支（基于节气）
    date_val = month * 100 + day
    
    # 先判断节气所属的月份
    if date_val < 204 or date_val >= 106:  # 立春前 → 丑月（上一年十二月）
        if date_val >= 106 and date_val < 204:
            zhi_idx = 1  # 丑月
        elif date_val >= 204 and date_val < 306:
            zhi_idx = 2  # 寅月
        elif date_val >= 306 and date_val < 405:
            zhi_idx = 3  # 卯月
        elif date_val >= 405 and date_val < 506:
            zhi_idx = 4  # 辰月
        elif date_val >= 506 and date_val < 606:
            zhi_idx = 5  # 巳月
        elif date_val >= 606 and date_val < 707:
            zhi_idx = 6  # 午月
        elif date_val >= 707 and date_val < 808:
            zhi_idx = 7  # 未月
        elif date_val >= 808 and date_val < 908:
            zhi_idx = 8  # 申月
        elif date_val >= 908 and date_val < 1008:
            zhi_idx = 9  # 酉月
        elif date_val >= 1008 and date_val < 1108:
            zhi_idx = 10  # 戌月
        elif date_val >= 1108 and date_val < 1207:
            zhi_idx = 11  # 亥月
        elif date_val >= 1207:
            zhi_idx = 0  # 子月
        else:
            zhi_idx = 1  # 丑月
    else:
        zhi_idx = 1  # 丑月
    
    # 五虎遁：甲己之年丙作首 → 年干为甲或己，正月(寅月)月干为丙
    # 年干: 甲己→丙寅, 乙庚→戊寅, 丙辛→庚寅, 丁壬→壬寅, 戊癸→甲寅
    wuhu_base = {
        0: 2,  # 甲 → 丙(2)
        1: 2,  # 己 → 丙(2) 
        2: 4,  # 乙 → 戊(4)
        3: 4,  # 庚 → 戊(4)
        4: 6,  # 丙 → 庚(6)
        5: 6,  # 辛 → 庚(6)
        6: 8,  # 丁 → 壬(8)
        7: 8,  # 壬 → 壬(8)
        8: 0,  # 戊 → 甲(0)
        9: 0,  # 癸 → 甲(0)
    }
    
    # 寅月(2)为正月，月干从寅月开始推
    # zhi_idx=2(寅月)时 offset=0, zhi_idx=0(子月)时 offset=10
    month_offset = (zhi_idx - 2) % 12
    gan_idx = (wuhu_base[year_gan_idx] + month_offset) % 10
    
    return gan_idx, zhi_idx


def calc_day_gz(date: datetime) -> Tuple[int, int]:
    """
    计算日干支索引
    已知 1900-01-01 为甲戌日（干=0, 支=10）
    """
    base_date = datetime(1900, 1, 1)
    base_gan = 0   # 甲
    base_zhi = 10  # 戌
    
    delta = (date.date() - base_date.date()).days
    gan_idx = (base_gan + delta) % 10
    zhi_idx = (base_zhi + delta) % 12
    
    return gan_idx, zhi_idx


def calc_hour_gz(hour: int, day_gan_idx: int) -> Tuple[int, int]:
    """
    计算时干支索引
    时支由小时决定，时干由日干推出（五鼠遁）
    """
    # 时支：23-1=子(0), 1-3=丑(1), 3-5=寅(2), ...
    zhi_idx = ((hour + 1) // 2) % 12
    
    # 五鼠遁：甲己还加甲 → 日干为甲或己，子时天干为甲
    wushu_base = {
        0: 0,  # 甲日 → 甲子
        1: 0,  # 己日 → 甲子
        2: 2,  # 乙日 → 丙子
        3: 2,  # 庚日 → 丙子
        4: 4,  # 丙日 → 戊子
        5: 4,  # 辛日 → 戊子
        6: 6,  # 丁日 → 庚子
        7: 6,  # 壬日 → 庚子
        8: 8,  # 戊日 → 壬子
        9: 8,  # 癸日 → 壬子
    }
    
    gan_idx = (wushu_base[day_gan_idx] + zhi_idx) % 10
    return gan_idx, zhi_idx


def calc_dayun(year_gan_idx: int, gender: str, year_gan_yinyang: str) -> List[Dict]:
    """
    计算大运
    阳男阴女顺排，阴男阳女逆排
    """
    is_male = gender in ("男", "male", "m")
    gan_yang = year_gan_yinyang == "阳"
    
    forward = (is_male and gan_yang) or (not is_male and not gan_yang)
    
    # 起运年龄（简化：按出生日期到下一个/上一个节气天数/3）
    # 这里简化处理
    qiyun_age = 1  # 默认1岁起运，实际需要精确计算
    
    # 月柱干支
    # 从月柱开始，顺排或逆排
    dayuns = []
    for i in range(8):  # 排8步大运
        age = qiyun_age + i * 10
        dayuns.append({
            "age": f"{age}-{age+9}岁",
            "description": f"第{i+1}步大运"
        })
    
    return dayuns


# ============================================================
# 输出格式化
# ============================================================

def format_bazi(birth_date: datetime, gender: str = "男") -> Dict:
    """计算完整八字命盘"""
    year = birth_date.year
    month = birth_date.month
    day = birth_date.day
    hour = birth_date.hour
    
    # 计算四柱
    yg, yz = calc_year_gz(year)
    mg, mz = calc_month_gz(year, month, day, yg)
    dg, dz = calc_day_gz(birth_date)
    hg, hz = calc_hour_gz(hour, dg)
    
    year_gan = TIAN_GAN[yg]
    year_zhi = DI_ZHI[yz]
    month_gan = TIAN_GAN[mg]
    month_zhi = DI_ZHI[mz]
    day_gan = TIAN_GAN[dg]
    day_zhi = DI_ZHI[dz]
    hour_gan = TIAN_GAN[hg]
    hour_zhi = DI_ZHI[hz]
    
    # 日主（日干）
    rizhu_gan = day_gan
    
    # 五行统计
    wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for g, z in [(year_gan, year_zhi), (month_gan, month_zhi), (day_gan, day_zhi), (hour_gan, hour_zhi)]:
        wuxing_count[GAN_WUXING[g]] += 1
        wuxing_count[ZHI_WUXING[z]] += 0.5  # 地支五行权重0.5
    
    rizhu_wuxing = GAN_WUXING[rizhu_gan]
    
    # 十神
    shishen_map = {}
    for pillar_name, gan in [("年干", year_gan), ("月干", month_gan), ("日干", day_gan), ("时干", hour_gan)]:
        shishen_map[pillar_name] = get_shishen(rizhu_gan, gan) if gan != rizhu_gan else "日主"
    
    # 纳音
    nayin_map = {
        "年柱": get_nayin(yg, yz),
        "月柱": get_nayin(mg, mz),
        "日柱": get_nayin(dg, dz),
        "时柱": get_nayin(hg, hz),
    }
    
    # 生肖
    shengxiao = SHENG_XIAO[yz]
    
    # 大运
    dayuns = calc_dayun(yg, gender, GAN_YINYANG[year_gan])
    
    return {
        "基本信息": {
            "出生时间": birth_date.strftime("%Y年%m月%d日 %H时"),
            "性别": gender,
            "生肖": shengxiao,
        },
        "四柱八字": {
            "年柱": f"{year_gan}{year_zhi}",
            "月柱": f"{month_gan}{month_zhi}",
            "日柱": f"{day_gan}{day_zhi}",
            "时柱": f"{hour_gan}{hour_zhi}",
        },
        "详细": {
            "年": {"天干": year_gan, "地支": year_zhi, "阴阳": GAN_YINYANG[year_gan], "五行": GAN_WUXING[year_gan]},
            "月": {"天干": month_gan, "地支": month_zhi, "阴阳": GAN_YINYANG[month_gan], "五行": GAN_WUXING[month_gan]},
            "日": {"天干": day_gan, "地支": day_zhi, "阴阳": GAN_YINYANG[day_gan], "五行": GAN_WUXING[day_gan]},
            "时": {"天干": hour_gan, "地支": hour_zhi, "阴阳": GAN_YINYANG[hour_gan], "五行": GAN_WUXING[hour_gan]},
        },
        "日主": {
            "天干": rizhu_gan,
            "五行": rizhu_wuxing,
            "阴阳": GAN_YINYANG[rizhu_gan],
        },
        "十神": shishen_map,
        "纳音": nayin_map,
        "五行分布": wuxing_count,
        "地支藏干": {
            "年": ZHI_CANG_GAN[year_zhi],
            "月": ZHI_CANG_GAN[month_zhi],
            "日": ZHI_CANG_GAN[day_zhi],
            "时": ZHI_CANG_GAN[hour_zhi],
        },
        "大运": dayuns,
    }


def print_bazi(bazi: Dict):
    """美化打印八字命盘"""
    info = bazi["基本信息"]
    pillars = bazi["四柱八字"]
    detail = bazi["详细"]
    rizhu = bazi["日主"]
    
    print("=" * 60)
    print(f"  📅 八字命盘 — {info['出生时间']}")
    print("=" * 60)
    print(f"  生肖：{info['生肖']}　性别：{info['性别']}")
    print()
    
    # 四柱排盘表
    print("  ┌────────┬────────┬────────┬────────┐")
    print(f"  │  年柱  │  月柱  │  日柱  │  时柱  │")
    print("  ├────────┼────────┼────────┼────────┤")
    print(f"  │ {pillars['年柱']:^5} │ {pillars['月柱']:^5} │ {pillars['日柱']:^5} │ {pillars['时柱']:^5} │")
    print("  ├────────┼────────┼────────┼────────┤")
    
    # 天干行
    yl = detail["年"]
    ml = detail["月"]
    dl = detail["日"]
    hl = detail["时"]
    print(f"  │{yl['天干']}({yl['五行']}{yl['阴阳']})│{ml['天干']}({ml['五行']}{ml['阴阳']})│{dl['天干']}({dl['五行']}{dl['阴阳']})│{hl['天干']}({hl['五行']}{hl['阴阳']})│")
    
    # 地支行
    print(f"  │{yl['地支']}({ZHI_WUXING[yl['地支']]}) │{ml['地支']}({ZHI_WUXING[ml['地支']]}) │{dl['地支']}({ZHI_WUXING[dl['地支']]}) │{hl['地支']}({ZHI_WUXING[hl['地支']]}) │")
    print("  └────────┴────────┴────────┴────────┘")
    print()
    
    print(f"  🌟 日主：{rizhu['天干']}（{rizhu['五行']}{rizhu['阴阳']}）")
    print(f"  📛 十神：{bazi['十神']}")
    print(f"  🎵 纳音：{bazi['纳音']}")
    print(f"  ⚖️  五行：{bazi['五行分布']}")
    print(f"  🏠 藏干：{bazi['地支藏干']}")
    print()
    
    # 基础解读
    wx_dist = bazi['五行分布']
    ri_wx = rizhu['五行']
    print(f"  📖 基础解读：")
    
    # 五行旺衰分析
    total = sum(wx_dist.values())
    for wx, cnt in sorted(wx_dist.items(), key=lambda x: x[1], reverse=True):
        pct = cnt / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        marker = " ← 日主" if wx == ri_wx else ""
        print(f"    {wx}: {bar} {pct:.1f}%{marker}")
    
    print("=" * 60)


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("用法: python bazi.py YYYY-MM-DD HH [男/女]")
        print("示例: python bazi.py 1990-05-20 08 男")
        sys.exit(1)
    
    date_str = sys.argv[1]
    hour = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    gender = sys.argv[3] if len(sys.argv) > 3 else "男"
    
    try:
        # 支持多种日期格式
        for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError("无法解析日期")
        
        birth = dt.replace(hour=hour)
    except Exception as e:
        print(f"日期解析错误: {e}")
        sys.exit(1)
    
    bazi = format_bazi(birth, gender)
    
    # 支持JSON输出
    if "--json" in sys.argv:
        import json
        print(json.dumps(bazi, ensure_ascii=False, indent=2))
    else:
        print_bazi(bazi)


if __name__ == "__main__":
    main()