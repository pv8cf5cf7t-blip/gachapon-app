#!/usr/bin/env python3
"""
手相分析 (Palmistry Analysis) 知识库
包含：五行手型、三大主线、掌丘、指纹等解读
"""

import sys
import json
from typing import Dict, List

# ============================================================
# 五行手型
# ============================================================

HAND_TYPES = {
    "金": {
        "name": "金形手",
        "characteristics": "手掌方正，手指尖细，皮肤白皙，指节不明显",
        "personality": "理性冷静，思维缜密，有正义感，做事果断。适合从事法律、管理、金融等需要逻辑思维的工作。",
        "strength": "判断力强，原则性强，处事公正",
        "weakness": "有时过于固执，缺乏灵活性，感情表达内敛",
        "career": "管理、法律、金融、公务员",
        "love": "重视承诺和责任，不轻易表达感情，但一旦认定就会非常忠诚",
    },
    "木": {
        "name": "木形手",
        "characteristics": "手掌修长，手指细直，关节略突出，皮肤偏青",
        "personality": "好学上进，有创造力，理想主义者。喜欢学习和探索新事物。适合学术、教育、艺术等需要创造力的工作。",
        "strength": "学习能力强，有创造力，心地善良",
        "weakness": "有时不切实际，容易焦虑，多愁善感",
        "career": "教育、科研、艺术、设计",
        "love": "浪漫主义者，渴望灵魂伴侣，重视精神交流",
    },
    "水": {
        "name": "水形手",
        "characteristics": "手掌圆润丰满，手指短而圆，皮肤柔滑有弹性",
        "personality": "灵活变通，适应力强，善于交际。如同水一样能适应各种环境。适合商业、外交、销售等需要灵活应对的工作。",
        "strength": "适应力强，人缘好，随机应变",
        "weakness": "有时缺乏主见，容易随波逐流，缺乏持久力",
        "career": "商业、销售、公关、外交",
        "love": "感情丰富，重视当下感受，享受恋爱过程",
    },
    "火": {
        "name": "火形手",
        "characteristics": "手掌尖长，手指细长，指尖尖细，皮肤偏红",
        "personality": "热情冲动，精力充沛，直觉敏锐。充满激情和创造力。适合创业、演艺、体育等需要热情和爆发力的工作。",
        "strength": "热情积极，行动力强，富有感染力",
        "weakness": "容易冲动，缺乏耐心，情绪起伏大",
        "career": "创业、演艺、体育、销售",
        "love": "激情四射，爱得热烈，但也容易来得快去得快",
    },
    "土": {
        "name": "土形手",
        "characteristics": "手掌厚实宽大，手指粗短结实，皮肤粗糙厚实",
        "personality": "稳重踏实，诚实可靠，忍耐力强。如同大地一般可靠。适合技术、农业、建筑等需要耐力和实干的工作。",
        "strength": "踏实可靠，耐力强，诚实守信",
        "weakness": "有时过于保守，缺乏变通，思维固化",
        "career": "工程、技术、农业、制造",
        "love": "务实可靠，不善花言巧语，但用行动表达爱意",
    },
}


# ============================================================
# 三大主线
# ============================================================

LINES = {
    "生命线": {
        "description": "从拇指和食指之间出发，环绕大鱼际向下延伸。反映生命力和健康状态。",
        "meanings": {
            "长而深": "生命力强，身体健康，精力充沛",
            "短而浅": "体质较弱，需注意健康，但并非短寿之兆",
            "清晰连续": "生活稳定，健康状况良好",
            "断裂": "人生可能有重大转折或健康危机",
            "链状": "体质敏感，容易疲劳",
            "双重生命线": "生命力极强，有贵人相助，是吉兆",
            "起点高（靠近食指）": "志向远大，事业心强",
            "弧线大（包围大鱼际广）": "精力充沛，活动范围广",
            "末端有分叉": "晚年生活丰富，可能远行",
        }
    },
    "智慧线": {
        "description": "从拇指和食指之间出发，横穿手掌中央。反映思维方式、智力和判断力。",
        "meanings": {
            "长而直（到掌边）": "思维清晰，逻辑能力强，理性冷静",
            "长而下垂（弯向月丘）": "想象力丰富，直觉敏锐，有艺术天赋",
            "短（在中指下结束）": "思维务实，注重眼前实际",
            "深而清晰": "判断力强，专注力好",
            "浅而模糊": "思维分散，容易犹豫不决",
            "与生命线分开发源": "独立自主，性格果断",
            "与生命线同源较长": "谨慎小心，考虑周全",
            "有岛纹": "某时期思维混乱或精神压力大",
        }
    },
    "感情线": {
        "description": "从小指下方出发，向食指和中指之间延伸。反映感情世界、人际关系和情绪状态。",
        "meanings": {
            "长而深（延伸到食指下）": "感情丰富深沉，重情重义",
            "短（只到中指下）": "感情表达直接，不善于浪漫",
            "平直": "理性恋爱，不易被感情冲昏头脑",
            "弯曲上翘": "浪漫多情，感情丰富",
            "链状": "情感细腻敏感，容易受伤",
            "有岛纹": "感情上可能经历波折或困扰",
            "双重感情线": "情感丰富，可能有复杂的感情经历",
            "末端分叉": "感情选择上的矛盾，或有多方面的爱",
        }
    },
    "命运线": {
        "description": "从手腕向上延伸至中指下方的竖线（非人人都有）。反映事业运和人生发展。",
        "meanings": {
            "清晰深长": "事业方向明确，人生有目标感",
            "从生命线出发": "靠自身努力开创事业",
            "从月丘出发": "得他人帮助或外部机遇成就事业",
            "从手腕正中出发": "早年就开始有明确的事业方向",
            "止于智慧线": "中年后可能事业方向改变",
            "止于感情线": "感情因素对事业影响较大",
            "多条命运线": "事业多元化，有多个发展方向",
            "没有命运线": "不受命运束缚，人生自由多变（并非坏事）",
        }
    },
}


# ============================================================
# 掌丘
# ============================================================

MOUNTS = {
    "金星丘": {
        "location": "拇指根部隆起处",
        "full": "充满爱心，热情有活力，生命力旺盛。异性缘佳，喜欢享受生活。",
        "flat": "性格冷淡，体力较弱，对生活缺乏热情。",
        "excessive": "占有欲强，贪图享乐，可能过于放纵。",
    },
    "木星丘": {
        "location": "食指根部隆起处",
        "full": "有领导才能，自信自尊，事业心强。有组织能力，适合管理岗位。",
        "flat": "缺乏自信，不愿担当，甘于平凡。",
        "excessive": "过于自负，独断专行，野心过大。",
    },
    "土星丘": {
        "location": "中指根部隆起处",
        "full": "稳重理智，有责任感，善于思考和规划。对哲学和深度思考有兴趣。",
        "flat": "缺乏责任感，行事轻浮，不善深度思考。",
        "excessive": "过于严肃刻板，容易抑郁，孤僻寡欢。",
    },
    "太阳丘": {
        "location": "无名指根部隆起处",
        "full": "有艺术天赋，乐观开朗，审美能力强。追求美好，有创造力。",
        "flat": "缺乏艺术细胞，过于务实，不懂享受生活之美。",
        "excessive": "虚荣心强，爱慕浮华，可能铺张浪费。",
    },
    "水星丘": {
        "location": "小指根部隆起处",
        "full": "善于沟通表达，商业头脑好，反应敏捷。适合经商和社交活跃的工作。",
        "flat": "不善言辞，社交能力弱，商业头脑欠缺。",
        "excessive": "过于圆滑，巧言令色，可能缺乏诚信。",
    },
    "月丘": {
        "location": "手掌外侧下部（小鱼际）",
        "full": "想象力丰富，直觉强，有浪漫情怀。可能有艺术或灵性方面的天赋。",
        "flat": "缺乏想象力，过于实际，不懂浪漫。",
        "excessive": "不切实际的幻想家，容易脱离现实。",
    },
    "火星丘": {
        "location": "生命线和智慧线之间的区域",
        "full": "勇敢果断，行动力强，遇事敢于应对。有冒险精神。",
        "flat": "胆小怕事，缺乏勇气，容易退缩。",
        "excessive": "好斗冲动，争强好胜，容易惹事。",
    },
}


# ============================================================
# 其他特征
# ============================================================

SPECIAL_MARKS = {
    "星纹": "突发的机遇或变化（位置决定吉凶）",
    "十字纹": "某个方面的考验或保护（位置决定含义）",
    "岛纹": "困扰、停滞或弱势时期",
    "方纹": "保护符号，化解灾难",
    "三角纹": "某种特殊才能或天赋",
    "格子纹": "困扰和障碍",
    "圆环纹": "约束和限制",
}


# ============================================================
# 综合解读
# ============================================================

def analyze_palm(hand_type: str = None, life_line: str = None, 
                 wisdom_line: str = None, emotion_line: str = None,
                 fate_line: str = None, prominent_mounts: List[str] = None) -> Dict:
    """综合分析手相"""
    
    result = {
        "手型分析": {},
        "主线解读": {},
        "掌丘分析": {},
        "综合建议": [],
    }
    
    # 手型
    if hand_type and hand_type in HAND_TYPES:
        ht = HAND_TYPES[hand_type]
        result["手型分析"] = {
            "类型": ht["name"],
            "特征": ht["characteristics"],
            "性格": ht["personality"],
            "优势": ht["strength"],
            "劣势": ht["weakness"],
            "适合职业": ht["career"],
            "感情特点": ht["love"],
        }
    
    # 主线
    for line_name, feature in [("生命线", life_line), ("智慧线", wisdom_line), 
                                 ("感情线", emotion_line), ("命运线", fate_line)]:
        if feature and feature in LINES[line_name]["meanings"]:
            result["主线解读"][line_name] = {
                "特征": feature,
                "解读": LINES[line_name]["meanings"][feature],
                "说明": LINES[line_name]["description"],
            }
    
    # 掌丘
    if prominent_mounts:
        for mount in prominent_mounts:
            if mount in MOUNTS:
                result["掌丘分析"][mount] = {
                    "位置": MOUNTS[mount]["location"],
                    "解读": MOUNTS[mount]["full"],
                }
    
    # 综合建议
    if hand_type == "火":
        result["综合建议"].append("💡 火形手热情有余，建议在做重大决定前多冷静思考，避免冲动。")
    elif hand_type == "土":
        result["综合建议"].append("💡 土形手稳重可靠，建议适当跳出舒适区，尝试新的可能。")
    elif hand_type == "木":
        result["综合建议"].append("💡 木形手好学善思，建议将想法付诸实践，避免纸上谈兵。")
    elif hand_type == "金":
        result["综合建议"].append("💡 金形手刚正果断，建议适当柔和处事，刚柔并济更佳。")
    elif hand_type == "水":
        result["综合建议"].append("💡 水形手机敏灵活，建议在一些事情上坚持到底，培养定力。")
    
    if wisdom_line and "短" in wisdom_line:
        result["综合建议"].append("💡 智慧线偏短，建议在做复杂决策时多咨询他人意见。")
    
    if emotion_line and "链状" in emotion_line:
        result["综合建议"].append("💡 感情线呈链状，情感细腻敏感，建议学会保护自己的内心。")
    
    return result


def print_palm_analysis(analysis: Dict):
    """美化打印手相分析"""
    print("=" * 60)
    print("  🖐️  手相综合分析")
    print("=" * 60)
    
    if analysis["手型分析"]:
        ht = analysis["手型分析"]
        print()
        print(f"  🔸 手型：{ht['类型']}")
        print(f"     特征：{ht['特征']}")
        print(f"     性格：{ht['性格']}")
        print(f"     优势：{ht['优势']}")
        print(f"     劣势：{ht['劣势']}")
        print(f"     职业：{ht['适合职业']}")
        print(f"     感情：{ht['感情特点']}")
    
    if analysis["主线解读"]:
        print()
        print("  📏 主线解读：")
        for line_name, info in analysis["主线解读"].items():
            print(f"     【{line_name}】{info['特征']}")
            print(f"     → {info['解读']}")
    
    if analysis["掌丘分析"]:
        print()
        print("  ⛰️  掌丘分析：")
        for mount, info in analysis["掌丘分析"].items():
            print(f"     【{mount}】{info['位置']}")
            print(f"     → {info['解读']}")
    
    if analysis["综合建议"]:
        print()
        print("  📋 综合建议：")
        for advice in analysis["综合建议"]:
            print(f"     {advice}")
    
    print()
    print("=" * 60)
    print("  ⚠️  手相仅供参考娱乐，人生掌握在自己手中！")
    print("=" * 60)


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("手相分析工具")
        print()
        print("用法:")
        print("  python palmistry.py types                    — 查看五行手型列表")
        print("  python palmistry.py lines                    — 查看三大主线说明")
        print("  python palmistry.py mounts                   — 查看掌丘说明")
        print("  python palmistry.py analyze [特征...]        — 综合分析")
        print()
        print("分析示例:")
        print("  python palmistry.py analyze --hand=火 --life=长而深 --wisdom=长而下垂 --emotion=长而深")
        print("  python palmistry.py analyze --hand=木 --mounts=木星丘,太阳丘")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "types":
        print("五行手型：")
        print("-" * 60)
        for wx, info in HAND_TYPES.items():
            print(f"\n  [{wx}] {info['name']}")
            print(f"   特征：{info['characteristics']}")
            print(f"   性格：{info['personality']}")
            print(f"   适合：{info['career']}")
    
    elif cmd == "lines":
        print("三大主线 + 命运线：")
        print("-" * 60)
        for name, info in LINES.items():
            print(f"\n  📏 {name}")
            print(f"   说明：{info['description']}")
            print(f"   特征解读：")
            for feat, meaning in info["meanings"].items():
                print(f"     · {feat}：{meaning}")
    
    elif cmd == "mounts":
        print("七大掌丘：")
        print("-" * 60)
        for name, info in MOUNTS.items():
            print(f"\n  ⛰️  {name}")
            print(f"   位置：{info['location']}")
            print(f"   饱满：{info['full']}")
    
    elif cmd == "analyze":
        hand_type = None
        life = None
        wisdom = None
        emotion = None
        fate = None
        mounts = []
        
        for arg in sys.argv[2:]:
            if arg.startswith("--hand="):
                hand_type = arg.split("=")[1]
            elif arg.startswith("--life="):
                life = arg.split("=")[1]
            elif arg.startswith("--wisdom="):
                wisdom = arg.split("=")[1]
            elif arg.startswith("--emotion="):
                emotion = arg.split("=")[1]
            elif arg.startswith("--fate="):
                fate = arg.split("=")[1]
            elif arg.startswith("--mounts="):
                mounts = arg.split("=")[1].split(",")
        
        analysis = analyze_palm(
            hand_type=hand_type,
            life_line=life,
            wisdom_line=wisdom,
            emotion_line=emotion,
            fate_line=fate,
            prominent_mounts=mounts if mounts else None,
        )
        
        if "--json" in sys.argv:
            print(json.dumps(analysis, ensure_ascii=False, indent=2))
        else:
            print_palm_analysis(analysis)
    
    else:
        # 可能是交互模式
        print("欢迎使用手相分析！请回答以下问题：")
        print()
        print("选择您的手型（输入序号）：")
        for i, (wx, info) in enumerate(HAND_TYPES.items(), 1):
            print(f"  {i}. {info['name']} — {info['characteristics']}")
        print()
        print("（更多交互功能请使用命令行参数）")
        print("提示: python palmistry.py analyze --hand=火 --life=长而深")


if __name__ == "__main__":
    main()