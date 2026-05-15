#!/usr/bin/env python3
"""
风水分析 (Feng Shui Analysis)
包含：命卦计算、八宅吉凶、玄空飞星、流年布局、五行配色
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============================================================
# 基础常量
# ============================================================

# 八卦与九宫数
GUA_NUMBER = {
    1: {"name": "坎", "trigram": "☵", "element": "水", "direction": "北", "group": "东四"},
    2: {"name": "坤", "trigram": "☷", "element": "土", "direction": "西南", "group": "西四"},
    3: {"name": "震", "trigram": "☳", "element": "木", "direction": "东", "group": "东四"},
    4: {"name": "巽", "trigram": "☴", "element": "木", "direction": "东南", "group": "东四"},
    5: {"name": "中", "trigram": "◎", "element": "土", "direction": "中宫", "group": "中"},
    6: {"name": "乾", "trigram": "☰", "element": "金", "direction": "西北", "group": "西四"},
    7: {"name": "兑", "trigram": "☱", "element": "金", "direction": "西", "group": "西四"},
    8: {"name": "艮", "trigram": "☶", "element": "土", "direction": "东北", "group": "西四"},
    9: {"name": "离", "trigram": "☲", "element": "火", "direction": "南", "group": "东四"},
}

# 九星（玄空飞星）
NINE_STARS = {
    1: {"name": "一白贪狼", "element": "水", "nature": "吉", "meaning": "桃花、人缘、智慧"},
    2: {"name": "二黑巨门", "element": "土", "nature": "凶", "meaning": "病符、是非、阻碍"},
    3: {"name": "三碧禄存", "element": "木", "nature": "凶", "meaning": "口舌、争斗、官非"},
    4: {"name": "四绿文曲", "element": "木", "nature": "吉", "meaning": "文昌、学业、桃花"},
    5: {"name": "五黄廉贞", "element": "土", "nature": "大凶", "meaning": "灾祸、疾病、破财"},
    6: {"name": "六白武曲", "element": "金", "nature": "吉", "meaning": "官运、偏财、权势"},
    7: {"name": "七赤破军", "element": "金", "nature": "凶", "meaning": "盗贼、破财、口舌"},
    8: {"name": "八白左辅", "element": "土", "nature": "大吉", "meaning": "正财、置业、旺丁"},
    9: {"name": "九紫右弼", "element": "火", "nature": "吉", "meaning": "喜事、姻缘、添丁"},
}

# 八宅吉凶方位（以命卦为伏位）
# 按大游年歌诀：生五延六祸天绝
BAZHAI_PATTERN = {
    # 坎1 (北)
    1: {
        "生气": 4, "延年": 9, "天医": 3, "伏位": 1,
        "祸害": 7, "六煞": 6, "五鬼": 8, "绝命": 2,
    },
    # 坤2 (西南)
    2: {
        "生气": 8, "延年": 6, "天医": 7, "伏位": 2,
        "祸害": 3, "六煞": 9, "五鬼": 4, "绝命": 1,
    },
    # 震3 (东)
    3: {
        "生气": 9, "延年": 4, "天医": 1, "伏位": 3,
        "祸害": 2, "六煞": 8, "五鬼": 6, "绝命": 7,
    },
    # 巽4 (东南)
    4: {
        "生气": 1, "延年": 3, "天医": 9, "伏位": 4,
        "祸害": 6, "六煞": 7, "五鬼": 2, "绝命": 8,
    },
    # 乾6 (西北)
    6: {
        "生气": 7, "延年": 2, "天医": 8, "伏位": 6,
        "祸害": 4, "六煞": 1, "五鬼": 3, "绝命": 9,
    },
    # 兑7 (西)
    7: {
        "生气": 6, "延年": 8, "天医": 2, "伏位": 7,
        "祸害": 1, "六煞": 4, "五鬼": 9, "绝命": 3,
    },
    # 艮8 (东北)
    8: {
        "生气": 2, "延年": 7, "天医": 6, "伏位": 8,
        "祸害": 9, "六煞": 3, "五鬼": 1, "绝命": 4,
    },
    # 离9 (南)
    9: {
        "生气": 3, "延年": 1, "天医": 4, "伏位": 9,
        "祸害": 8, "六煞": 2, "五鬼": 7, "绝命": 6,
    },
}

# 吉凶方位含义
DIRECTION_MEANING = {
    "生气": {"level": "上吉", "element": "木", "color": "绿", 
             "meaning": "旺财旺丁，事业发达，生机勃勃", "use": "大门、卧室、书房"},
    "延年": {"level": "上吉", "element": "金", "color": "白",
             "meaning": "延年益寿，感情和睦，人际关系好", "use": "卧室、客厅"},
    "天医": {"level": "中吉", "element": "土", "color": "黄",
             "meaning": "健康祛病，贵人相助，财运平稳", "use": "卧室、厨房"},
    "伏位": {"level": "小吉", "element": "木", "color": "青",
             "meaning": "平稳安顺，无大起落，适合静修", "use": "书房、休息区"},
    "祸害": {"level": "次凶", "element": "土", "color": "棕",
             "meaning": "口舌是非，小病小灾，破耗钱财", "avoid": "大门、卧室"},
    "六煞": {"level": "次凶", "element": "水", "color": "黑",
             "meaning": "桃花劫，人际关系复杂，情绪波动", "avoid": "卧室、办公"},
    "五鬼": {"level": "大凶", "element": "火", "color": "红",
             "meaning": "意外灾祸，官非口舌，严重破财", "avoid": "大门、卧室、厨房"},
    "绝命": {"level": "大凶", "element": "金", "color": "白",
             "meaning": "破财伤身，家庭不和，事业受阻", "avoid": "所有重要区域"},
}

# 方位对应
DIRECTIONS = {
    "北": 1, "西南": 2, "东": 3, "东南": 4,
    "西北": 6, "西": 7, "东北": 8, "南": 9,
}

DIR_NUMBER = {v: k for k, v in DIRECTIONS.items()}

# 2025年流年飞星（乙巳年）
# 以每年立春后更新
FLYING_STAR_2025 = {
    # 方位: 飞星数字
    "中宫": 2,  # 二黑入中
    "北": 7,     # 七赤
    "西南": 4,   # 四绿
    "东": 9,     # 九紫
    "东南": 5,   # 五黄
    "西北": 6,   # 六白
    "西": 1,     # 一白
    "东北": 8,   # 八白
    "南": 3,     # 三碧
}

# 2026年流年飞星（丙午年）
FLYING_STAR_2026 = {
    "中宫": 1,  # 一白入中
    "北": 8,     # 八白
    "西南": 6,   # 六白
    "东": 5,     # 五黄
    "东南": 3,   # 三碧
    "西北": 7,   # 七赤
    "西": 9,     # 九紫
    "东北": 2,   # 二黑
    "南": 4,     # 四绿
}

# 风水化解方法
CURES = {
    2: {"item": "铜葫芦/六帝钱", "note": "二黑病符星宜用金泄土气"},
    3: {"item": "红色饰品", "note": "三碧宜用火泄木气，忌绿色"},
    5: {"item": "铜铃/金属风铃", "note": "五黄大煞宜用金泄土气，切忌动土"},
    7: {"item": "蓝色/黑色水晶", "note": "七赤退气星宜用水泄金气"},
}

ENHANCE = {
    1: {"item": "水培植物/鱼缸", "note": "一白桃花星宜用水催旺"},
    4: {"item": "文昌塔/毛笔/绿植", "note": "四绿文昌星宜用木催旺"},
    6: {"item": "黄水晶/聚宝盆", "note": "六白偏财星宜用土生金"},
    8: {"item": "红地毯/紫水晶洞", "note": "八白正财星宜用火生土"},
    9: {"item": "红灯笼/红地毯/绿植", "note": "九紫喜星宜用木生火"},
}

# 五行行业
WUXING_CAREER = {
    "金": "金融、法律、公务员、工程师、珠宝、汽车",
    "木": "教育、出版、医疗、设计、园艺、文化",
    "水": "贸易、物流、旅游、传媒、IT、航海",
    "火": "餐饮、演艺、美容、能源、互联网、营销",
    "土": "房地产、建筑、农业、矿业、陶瓷、仓储",
}

# 五行生克
WUXING_GENERATE = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
WUXING_RESTRICT = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}


# ============================================================
# 命卦计算
# ============================================================

def calc_mingua(year: int, gender: str) -> Dict:
    """
    计算命卦（八宅风水基础）
    
    公式：
    男命：(100 - 年份后两位) % 9，若余0则为9
    女命：(年份后两位 - 4) % 9，若余0则为9
    2000年后公式不同
    """
    is_male = gender in ("男", "male", "m")
    last_two = year % 100
    
    if year >= 2000:
        if is_male:
            num = (100 - last_two) % 9
        else:
            num = (last_two + 6) % 9
    else:
        if is_male:
            num = (100 - last_two) % 9
        else:
            num = (last_two - 4) % 9
    
    if num == 0:
        num = 9
    if num == 5:
        # 中宫5，男寄坤2，女寄艮8
        num = 2 if is_male else 8
    
    return {
        "出生年": year,
        "性别": "男" if is_male else "女",
        "命卦数": num,
        "命卦": GUA_NUMBER[num]["name"],
        "卦象": GUA_NUMBER[num]["trigram"],
        "五行": GUA_NUMBER[num]["element"],
        "方位": GUA_NUMBER[num]["direction"],
        "东西命": GUA_NUMBER[num]["group"],
    }


# ============================================================
# 八宅吉凶方位
# ============================================================

def get_bazhai_directions(mingua_num: int) -> Dict:
    """获取命卦对应的八宅吉凶方位"""
    pattern = BAZHAI_PATTERN[mingua_num]
    
    result = {
        "吉方": {},
        "凶方": {},
        "命卦": GUA_NUMBER[mingua_num],
    }
    
    for meaning, gua_num in pattern.items():
        gua_info = GUA_NUMBER[gua_num]
        dir_info = DIRECTION_MEANING[meaning]
        
        entry = {
            "方位": gua_info["direction"],
            "卦名": gua_info["name"],
            "卦象": gua_info["trigram"],
            "五行": gua_info["element"],
            "吉凶等级": dir_info["level"],
            "含义": dir_info["meaning"],
            "建议": dir_info.get("use", "") or dir_info.get("avoid", ""),
            "颜色": dir_info["color"],
        }
        
        if "吉" in dir_info["level"]:
            result["吉方"][meaning] = entry
        else:
            result["凶方"][meaning] = entry
    
    # 按吉凶程度排序
    # 吉方：生气 > 延年 > 天医 > 伏位
    # 凶方：绝命 > 五鬼 > 六煞 > 祸害
    
    return result


def get_best_directions(mingua_num: int) -> List[Dict]:
    """获取最佳方位推荐"""
    bazhai = get_bazhai_directions(mingua_num)
    recommendations = []
    
    # 生气方：大门、主卧、书房
    if "生气" in bazhai["吉方"]:
        shengqi = bazhai["吉方"]["生气"]
        recommendations.append({
            "用途": "大门 / 公司入口",
            "最佳方位": shengqi["方位"],
            "效果": "纳生气，旺事业财运",
            "颜色建议": shengqi["颜色"],
        })
    
    # 延年方：卧室
    if "延年" in bazhai["吉方"]:
        yannian = bazhai["吉方"]["延年"]
        recommendations.append({
            "用途": "主卧室",
            "最佳方位": yannian["方位"],
            "效果": "利感情和睦，身体健康",
            "颜色建议": yannian["颜色"],
        })
    
    # 天医方：厨房/餐厅
    if "天医" in bazhai["吉方"]:
        tianyi = bazhai["吉方"]["天医"]
        recommendations.append({
            "用途": "厨房 / 餐厅",
            "最佳方位": tianyi["方位"],
            "效果": "利健康，聚财气",
            "颜色建议": tianyi["颜色"],
        })
    
    # 伏位方：书房
    if "伏位" in bazhai["吉方"]:
        fuwei = bazhai["吉方"]["伏位"]
        recommendations.append({
            "用途": "书房 / 办公室",
            "最佳方位": fuwei["方位"],
            "效果": "平稳安定，利学习和思考",
            "颜色建议": fuwei["颜色"],
        })
    
    return recommendations


# ============================================================
# 流年飞星分析
# ============================================================

def get_annual_stars(year: int = None) -> Dict:
    """获取流年飞星布局"""
    if year is None:
        year = datetime.now().year
    
    if year == 2025:
        stars = FLYING_STAR_2025
    elif year == 2026:
        stars = FLYING_STAR_2026
    else:
        # 简化计算：按年份推算入中星
        # (11 - year末位) % 9 + 1 作为入中星近似
        last_digit = year % 10
        center_star = (11 - last_digit) % 9
        if center_star == 0:
            center_star = 9
        # 简化：返回基础布局
        stars = {"中宫": center_star}
    
    result = {
        "年份": year,
        "飞星布局": {},
        "建议": {},
        "化解": {},
    }
    
    for direction, star_num in stars.items():
        star_info = NINE_STARS[star_num]
        
        result["飞星布局"][direction] = {
            "飞星": star_info["name"],
            "数字": star_num,
            "五行": star_info["element"],
            "属性": star_info["nature"],
            "含义": star_info["meaning"],
        }
        
        # 吉星催旺
        if star_info["nature"] in ("吉", "大吉"):
            enhance = ENHANCE.get(star_num, {})
            if enhance:
                result["建议"][direction] = {
                    "星": star_info["name"],
                    "催旺方法": enhance.get("item", ""),
                    "说明": enhance.get("note", ""),
                }
        
        # 凶星化解
        if star_info["nature"] in ("凶", "大凶"):
            cure = CURES.get(star_num, {})
            if cure:
                result["化解"][direction] = {
                    "星": star_info["name"],
                    "化解方法": cure.get("item", ""),
                    "说明": cure.get("note", ""),
                }
    
    return result


# ============================================================
# 综合风水建议
# ============================================================

def comprehensive_fengshui(year: int, gender: str, 
                           house_direction: str = None) -> Dict:
    """
    综合风水分析
    """
    mingua = calc_mingua(year, gender)
    bazhai = get_bazhai_directions(mingua["命卦数"])
    best = get_best_directions(mingua["命卦数"])
    annual = get_annual_stars()
    
    return {
        "命卦": mingua,
        "八宅吉凶": bazhai,
        "最佳方位推荐": best,
        f"{annual['年份']}年流年飞星": annual,
        "五行行业建议": WUXING_CAREER.get(mingua["五行"], ""),
    }


# ============================================================
# 格式化输出
# ============================================================

def print_mingua(mingua: Dict):
    """打印命卦"""
    print("=" * 60)
    print("  🏠 命卦分析")
    print("=" * 60)
    print(f"  出生年：{mingua['出生年']}　性别：{mingua['性别']}")
    print(f"  命　卦：{mingua['命卦']}{mingua['卦象']}（{mingua['东西命']}命）")
    print(f"  五　行：{mingua['五行']}")
    print(f"  本命方：{mingua['方位']}")
    print(f"  适合行业：{WUXING_CAREER.get(mingua['五行'], '')}")


def print_bazhai(bazhai: Dict):
    """打印八宅吉凶"""
    print()
    print("  🟢 吉方：")
    for name, info in bazhai["吉方"].items():
        mark = {"上吉": "⭐⭐⭐", "中吉": "⭐⭐", "小吉": "⭐"}
        print(f"    {name}位 → {info['方位']}（{info['卦名']}{info['卦象']}）{mark.get(info['吉凶等级'], '')}")
        print(f"            {info['含义']}")
        print(f"            💡 适合：{info['建议']}　🎨 色：{info['颜色']}")
    
    print()
    print("  🔴 凶方：")
    for name, info in bazhai["凶方"].items():
        mark = {"大凶": "💀💀", "次凶": "⚠️"}
        print(f"    {name}位 → {info['方位']}（{info['卦名']}{info['卦象']}）{mark.get(info['吉凶等级'], '')}")
        print(f"            {info['含义']}")
        print(f"            🚫 避免：{info['建议']}")


def print_best(best: List[Dict]):
    """打印最佳方位"""
    print()
    print("  📐 家居/办公室布局建议：")
    for rec in best:
        print(f"    {rec['用途']} → {rec['最佳方位']}（{rec['效果']}）")
        print(f"    🎨 配色建议：{rec['颜色建议']}")


def print_annual(annual: Dict):
    """打印流年飞星"""
    print()
    print(f"  🌟 {annual['年份']}年流年飞星布局：")
    
    # 九宫格显示
    grid = {
        "东南": "", "南": "", "西南": "",
        "东": "", "中宫": "", "西": "",
        "东北": "", "北": "", "西北": "",
    }
    
    for direction, info in annual["飞星布局"].items():
        if direction in grid:
            emoji = {"吉": "🟢", "大吉": "🌟", "凶": "🔴", "大凶": "💀"}
            e = emoji.get(info["属性"], "⚪")
            grid[direction] = f"{e}{info['数字']}"
    
    print(f"  ┌────────┬────────┬────────┐")
    print(f"  │ 东南 {grid['东南']:<4}│ 南  {grid['南']:<4}│ 西南 {grid['西南']:<4}│")
    print(f"  ├────────┼────────┼────────┤")
    print(f"  │ 东  {grid['东']:<4}│ 中  {grid['中宫']:<4}│ 西  {grid['西']:<4}│")
    print(f"  ├────────┼────────┼────────┤")
    print(f"  │ 东北 {grid['东北']:<4}│ 北  {grid['北']:<4}│ 西北 {grid['西北']:<4}│")
    print(f"  └────────┴────────┴────────┘")
    
    if annual.get("建议"):
        print()
        print("  ✅ 催旺建议：")
        for dir_name, advice in annual["建议"].items():
            print(f"    {dir_name}（{advice['星']}）：{advice['催旺方法']} — {advice['说明']}")
    
    if annual.get("化解"):
        print()
        print("  🛡️ 化解建议：")
        for dir_name, cure in annual["化解"].items():
            print(f"    {dir_name}（{cure['星']}）：{cure['化解方法']} — {cure['说明']}")


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("风水分析工具（阳宅风水）")
        print()
        print("用法:")
        print("  python fengshui.py mingua 1990 男        — 计算命卦")
        print("  python fengshui.py bazhai 1990 男        — 八宅吉凶方位")
        print("  python fengshui.py annual [年份]          — 流年飞星布局")
        print("  python fengshui.py full 1990 男           — 综合风水分析")
        print()
        print("示例:")
        print("  python fengshui.py full 1995 女")
        print("  python fengshui.py annual 2026")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "mingua":
        year = int(sys.argv[2])
        gender = sys.argv[3] if len(sys.argv) > 3 else "男"
        result = calc_mingua(year, gender)
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_mingua(result)
    
    elif cmd == "bazhai":
        year = int(sys.argv[2])
        gender = sys.argv[3] if len(sys.argv) > 3 else "男"
        mingua = calc_mingua(year, gender)
        result = get_bazhai_directions(mingua["命卦数"])
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_mingua(mingua)
            print_bazhai(result)
    
    elif cmd == "annual":
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        result = get_annual_stars(year)
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_annual(result)
    
    elif cmd == "full":
        year = int(sys.argv[2])
        gender = sys.argv[3] if len(sys.argv) > 3 else "男"
        house_dir = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = comprehensive_fengshui(year, gender, house_dir)
        
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_mingua(result["命卦"])
            print_bazhai(result["八宅吉凶"])
            print_best(result["最佳方位推荐"])
            annual_key = [k for k in result.keys() if "年流年飞星" in k][0]
            print_annual(result[annual_key])
            print()
            print("=" * 60)
            print("  ⚠️ 风水分析仅供参考，科学布局才是根本！")
            print("=" * 60)
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()