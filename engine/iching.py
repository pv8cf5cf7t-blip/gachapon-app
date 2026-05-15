#!/usr/bin/env python3
"""
周易占卜 (I Ching Divination) & 梅花易数
支持：六爻铜钱卦、梅花易数、64卦解读、变爻分析
"""

import sys
import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============================================================
# 八卦基础
# ============================================================

# 八卦 (Three-line trigrams)
# 乾三连，坤六断，震仰盂，艮覆碗，离中虚，坎中满，兑上缺，巽下断
BAGUA = {
    0: {"name": "乾", "symbol": "☰", "nature": "天", "direction": "西北", "element": "金", "body": "首", "family": "父"},
    1: {"name": "兑", "symbol": "☱", "nature": "泽", "direction": "西", "element": "金", "body": "口", "family": "少女"},
    2: {"name": "离", "symbol": "☲", "nature": "火", "direction": "南", "element": "火", "body": "目", "family": "中女"},
    3: {"name": "震", "symbol": "☳", "nature": "雷", "direction": "东", "element": "木", "body": "足", "family": "长男"},
    4: {"name": "巽", "symbol": "☴", "nature": "风", "direction": "东南", "element": "木", "body": "股", "family": "长女"},
    5: {"name": "坎", "symbol": "☵", "nature": "水", "direction": "北", "element": "水", "body": "耳", "family": "中男"},
    6: {"name": "艮", "symbol": "☶", "nature": "山", "direction": "东北", "element": "土", "body": "手", "family": "少男"},
    7: {"name": "坤", "symbol": "☷", "nature": "地", "direction": "西南", "element": "土", "body": "腹", "family": "母"},
}

# 八卦二进制编码（从下往上：初爻→上爻）
# 阳爻=1, 阴爻=0
TRIGRAM_BIN = {
    0b111: 0,  # 乾 ☰
    0b110: 1,  # 兑 ☱
    0b101: 2,  # 离 ☲
    0b100: 3,  # 震 ☳
    0b011: 4,  # 巽 ☴
    0b010: 5,  # 坎 ☵
    0b001: 6,  # 艮 ☶
    0b000: 7,  # 坤 ☷
}

# 六十四卦定义
HEXAGRAMS = {
    # 上经
    1:  {"name": "乾为天", "upper": 0, "lower": 0, "judgment": "元亨利贞", "element": "金金",
         "interpretation": "乾卦象征天，是纯阳之卦。代表创始、刚健、自强不息。得此卦者应积极进取，把握时机，但也要知道物极必反的道理。六爻皆阳，刚健中正，宜主动作为。"},
    2:  {"name": "坤为地", "upper": 7, "lower": 7, "judgment": "元亨，利牝马之贞", "element": "土土",
         "interpretation": "坤卦象征地，是纯阴之卦。代表柔顺、包容、厚德载物。得此卦者宜顺势而为，以柔克刚，不宜贸然出头。守正待时，厚积薄发。"},
    3:  {"name": "水雷屯", "upper": 5, "lower": 3, "judgment": "元亨利贞，勿用有攸往", "element": "水木",
         "interpretation": "屯卦象征初生之艰难。万物始生，充满困难但孕育希望。得此卦者正处创业初期或事业开端，虽困难重重但不可放弃，需耐心坚持。"},
    4:  {"name": "山水蒙", "upper": 6, "lower": 5, "judgment": "亨，匪我求童蒙，童蒙求我", "element": "土水",
         "interpretation": "蒙卦象征蒙昧、启蒙。代表需要学习和启发的时候。得此卦者宜虚心求教，不宜自以为是。教育启发之道在于受教者主动求问。"},
    5:  {"name": "水天需", "upper": 5, "lower": 0, "judgment": "有孚，光亨，贞吉，利涉大川", "element": "水金",
         "interpretation": "需卦象征等待。时机未到，需要耐心等候。得此卦者当前不宜急躁冒进，静待时机成熟。饮食宴乐，养精蓄锐。"},
    6:  {"name": "天水讼", "upper": 0, "lower": 5, "judgment": "有孚窒惕，中吉终凶", "element": "金水",
         "interpretation": "讼卦象征争讼、纠纷。代表矛盾冲突。得此卦者宜尽量避免争执，见好就收。诉讼之事中途或可化解，但纠缠到底必然两败俱伤。"},
    7:  {"name": "地水师", "upper": 7, "lower": 5, "judgment": "贞，丈人吉，无咎", "element": "土水",
         "interpretation": "师卦象征军队、战争。代表集体行动和组织纪律。得此卦者宜以正道统领众人，强调纪律和正义。师出有名，以正取胜。"},
    8:  {"name": "水地比", "upper": 5, "lower": 7, "judgment": "吉，原筮元永贞，无咎", "element": "水土",
         "interpretation": "比卦象征亲附、团结。代表人与人之间的亲近合作。得此卦者宜主动与人亲近，建立良好关系。众人拾柴火焰高，团结就是力量。"},
    9:  {"name": "风天小畜", "upper": 4, "lower": 0, "judgment": "亨，密云不雨，自我西郊", "element": "木金",
         "interpretation": "小畜卦象征小有积蓄。力量尚在积累中，阴云密布但未下雨。得此卦者事业有所积累但力量不足，暂时无法大展拳脚，需继续积蓄。"},
    10: {"name": "天泽履", "upper": 0, "lower": 1, "judgment": "履虎尾，不咥人，亨", "element": "金金",
         "interpretation": "履卦象征践行、履行。如履虎尾，险中求安。得此卦者当谨慎行事，行为端正，虽有风险也能化险为夷。礼行天下，以柔履刚。"},
    11: {"name": "地天泰", "upper": 7, "lower": 0, "judgment": "小往大来，吉亨", "element": "土金",
         "interpretation": "泰卦象征通达、安泰。天地交而万物通，上下交而其志同。得此卦者正处顺境，万事亨通。阴阳调和，否极泰来，是大吉之卦。"},
    12: {"name": "天地否", "upper": 0, "lower": 7, "judgment": "否之匪人，不利君子贞", "element": "金土",
         "interpretation": "否卦象征闭塞、不通。天地不交，万物不通。得此卦者正处逆境，小人道长君子道消。宜守正自保，韬光养晦，等待转机。否极泰来。"},
    13: {"name": "天火同人", "upper": 0, "lower": 2, "judgment": "同人于野，亨，利涉大川", "element": "金火",
         "interpretation": "同人卦象征大同、和同。代表志同道合的人走到一起。得此卦者宜与人合作，寻求志同道合的伙伴。以公正之心团结众人，可成大事。"},
    14: {"name": "火天大有", "upper": 2, "lower": 0, "judgment": "元亨", "element": "火金",
         "interpretation": "大有卦象征丰收、富有。所有甚大，无所不有。得此卦者事业有成，收获满满。但需戒骄戒躁，富而有德，方能长久。"},
    15: {"name": "地山谦", "upper": 7, "lower": 6, "judgment": "亨，君子有终", "element": "土土",
         "interpretation": "谦卦象征谦虚。地中有山，内高外低。得此卦者宜保持谦虚态度，不骄不躁。谦虚使人进步，君子始终能有好结果。是最吉之卦。"},
    16: {"name": "雷地豫", "upper": 3, "lower": 7, "judgment": "利建侯行师", "element": "木土",
         "interpretation": "豫卦象征喜悦、安乐。雷出地奋，万物欣悦。得此卦者宜顺势而为，享受当下的安乐。但也需防乐极生悲，居安思危。"},
    # 第17-32卦（精简版，保留关键卦）
    17: {"name": "泽雷随", "upper": 1, "lower": 3, "judgment": "元亨利贞，无咎", "element": "金木",
         "interpretation": "随卦象征随从、顺从。得此卦者宜随顺时势，灵活应变。天下随时，随时之义大矣哉。随遇而安但不可随波逐流，保持自我判断。"},
    18: {"name": "山风蛊", "upper": 6, "lower": 4, "judgment": "元亨，利涉大川", "element": "土木",
         "interpretation": "蛊卦象征腐败、整治。事物久而生弊需要革新。得此卦者须面对积弊，振作精神进行改革。先甲三日后甲三日，革故鼎新。"},
    19: {"name": "地泽临", "upper": 7, "lower": 1, "judgment": "元亨利贞，至于八月有凶", "element": "土金",
         "interpretation": "临卦象征临近、监督。以上临下，恩威并施。得此卦者当前运势正在上升，需善于管理和监督。但盛极必衰，八月之后需警惕。"},
    20: {"name": "风地观", "upper": 4, "lower": 7, "judgment": "盥而不荐，有孚颙若", "element": "木土",
         "interpretation": "观卦象征观察、观摩。风行地上，无所不观。得此卦者宜冷静观察，不宜贸然行动。先看清楚形势再做决断。观天之道，执天之行。"},
    21: {"name": "火雷噬嗑", "upper": 2, "lower": 3, "judgment": "亨，利用狱", "element": "火木",
         "interpretation": "噬嗑卦象征咬合、刑罚。口中有物，咬碎则合。得此卦者可能面临障碍需要强力突破。宜果断处理矛盾纠纷，快刀斩乱麻。"},
    22: {"name": "山火贲", "upper": 6, "lower": 2, "judgment": "亨，小利有攸往", "element": "土火",
         "interpretation": "贲卦象征装饰、文饰。山下有火，光彩照人。得此卦者宜注重外在形象包装，但也需防华而不实。形式服务于内容，不可本末倒置。"},
    23: {"name": "山地剥", "upper": 6, "lower": 7, "judgment": "不利有攸往", "element": "土土",
         "interpretation": "剥卦象征剥落、衰退。山附于地，根基不稳。得此卦者正处运势下降期，小人当道，宜隐忍守正。顺势而止，等待阳气的恢复。"},
    24: {"name": "地雷复", "upper": 7, "lower": 3, "judgment": "亨，出入无疾，朋来无咎", "element": "土木",
         "interpretation": "复卦象征回复、复兴。一阳复始，万象更新。得此卦者运势开始回升，生机重现。七日来复，天道循环。宜抓住重新开始的机会。"},
    25: {"name": "天雷无妄", "upper": 0, "lower": 3, "judgment": "元亨利贞，其匪正有眚", "element": "金木",
         "interpretation": "无妄卦象征不妄为、真实无虚。天下雷行，万物不敢妄为。得此卦者宜真诚实在，不存侥幸心理。妄行则有灾，守正自然亨通。"},
    26: {"name": "山天大畜", "upper": 6, "lower": 0, "judgment": "利贞，不家食吉", "element": "土金",
         "interpretation": "大畜卦象征大积蓄。天在山中，蓄力待发。得此卦者力量正在大量积累，宜学习充电。养贤蓄德，厚积薄发，终将大展宏图。"},
    27: {"name": "山雷颐", "upper": 6, "lower": 3, "judgment": "贞吉，观颐，自求口实", "element": "土木",
         "interpretation": "颐卦象征颐养、养生。山下有雷，万物得其养。得此卦者宜注重养生修养，自食其力。言语饮食皆需谨慎，养正则吉。"},
    28: {"name": "泽风大过", "upper": 1, "lower": 4, "judgment": "栋桡，利有攸往，亨", "element": "金木",
         "interpretation": "大过卦象征大过、过度。泽灭木，过犹不及。得此卦者可能面临重大转折或过度的情况。独立不惧，遁世无闷，需要超常规的应对。"},
    29: {"name": "坎为水", "upper": 5, "lower": 5, "judgment": "习坎，有孚维心亨", "element": "水水",
         "interpretation": "坎卦象征险陷、困难。水洊至，习坎。得此卦者正处险境，双重困难。但水流而不盈，行险而不失其信。宜保持信心，以柔克刚，终能出险。"},
    30: {"name": "离为火", "upper": 2, "lower": 2, "judgment": "利贞亨，畜牝牛吉", "element": "火火",
         "interpretation": "离卦象征光明、依附。明两作，大人以继明照于四方。得此卦者宜依附正道，光明磊落。日月丽乎天，百谷草木丽乎土。柔顺中正则吉。"},
    # 下经
    31: {"name": "泽山咸", "upper": 1, "lower": 6, "judgment": "亨利贞，取女吉", "element": "金土",
         "interpretation": "咸卦象征感应、感情。山上有泽，以虚受人。得此卦者人际关系良好，感情和睦。天地感而万物化生，男女感而情意相通。宜顺势而为。"},
    32: {"name": "雷风恒", "upper": 3, "lower": 4, "judgment": "亨，无咎，利贞，利有攸往", "element": "木木",
         "interpretation": "恒卦象征恒久、持久。雷风相与，巽而动。得此卦者宜持之以恒，不宜半途而废。天地之道恒久而不已。守正持久，终会成功。"},
    33: {"name": "天山遁", "upper": 0, "lower": 6, "judgment": "亨，小利贞", "element": "金土",
         "interpretation": "遁卦象征退避、隐退。天下有山，君子退隐。得此卦者当前宜知进退，不可硬碰。小利贞，不宜大动干戈。适时退避是智慧。"},
    34: {"name": "雷天大壮", "upper": 3, "lower": 0, "judgment": "利贞", "element": "木金",
         "interpretation": "大壮卦象征强盛、壮大。雷在天上，声势浩大。得此卦者力量正盛，但需守正。君子以非礼弗履，强盛之时更要约束自己，避免恃强凌弱。"},
    35: {"name": "火地晋", "upper": 2, "lower": 7, "judgment": "康侯用锡马蕃庶，昼日三接", "element": "火土",
         "interpretation": "晋卦象征前进、晋升。明出地上，旭日东升。得此卦者事业上升，前程光明。自昭明德，积极进取。正是大有作为之时。"},
    36: {"name": "地火明夷", "upper": 7, "lower": 2, "judgment": "利艰贞", "element": "土火",
         "interpretation": "明夷卦象征光明受伤。明入地中，黑暗笼罩。得此卦者正处困境，才德被掩。宜韬光养晦，内文明而外柔顺，在艰难中坚持正道。"},
    37: {"name": "风火家人", "upper": 4, "lower": 2, "judgment": "利女贞", "element": "木火",
         "interpretation": "家人卦象征家庭、内部。风自火出，家道兴旺。得此卦者宜注重家庭和内部事务。言有物而行有恒，家和万事兴。"},
    38: {"name": "火泽睽", "upper": 2, "lower": 1, "judgment": "小事吉", "element": "火金",
         "interpretation": "睽卦象征乖离、分歧。上火下泽，两相背离。得此卦者人际关系可能出现分歧和矛盾。宜求同存异，小事可成大事难为。君子以同而异。"},
    39: {"name": "水山蹇", "upper": 5, "lower": 6, "judgment": "利西南，不利东北", "element": "水土",
         "interpretation": "蹇卦象征艰难、跛足。山上有水，前行困难。得此卦者正处艰难之中，宜另寻出路。见险而能止，知矣哉。西南方有出路。"},
    40: {"name": "雷水解", "upper": 3, "lower": 5, "judgment": "利西南，无所往，其来复吉", "element": "木水",
         "interpretation": "解卦象征解脱、化解。雷雨作，百果草木皆甲坼。得此卦者困境即将解除。赦过宥罪，宽以待人。雨过天晴，万象更新。"},
    41: {"name": "山泽损", "upper": 6, "lower": 1, "judgment": "有孚元吉，无咎可贞", "element": "土金",
         "interpretation": "损卦象征减损、损失。山下有泽，损下益上。得此卦者可能需要做出牺牲以换取更大利益。损刚益柔有时，损益盈虚与时偕行。"},
    42: {"name": "风雷益", "upper": 4, "lower": 3, "judgment": "利有攸往，利涉大川", "element": "木木",
         "interpretation": "益卦象征增益、受益。风雷相益，其道大光。得此卦者获天时地利，正在上升期。见善则迁，有过则改。宜积极进取，大有收获。"},
    43: {"name": "泽天夬", "upper": 1, "lower": 0, "judgment": "扬于王庭，孚号有厉", "element": "金金",
         "interpretation": "夬卦象征决断、决裂。泽上于天，施禄及下。得此卦者面临重大决定，需要果断。君子以施禄及下，居德则忌。决而和，当断则断。"},
    44: {"name": "天风姤", "upper": 0, "lower": 4, "judgment": "女壮，勿用取女", "element": "金木",
         "interpretation": "姤卦象征相遇、邂逅。天下有风，后以施命诰四方。得此卦者可能遇到意外的缘分或机会。但也需防意外之变，一阴始生需警惕。"},
    45: {"name": "泽地萃", "upper": 1, "lower": 7, "judgment": "亨，王假有庙", "element": "金土",
         "interpretation": "萃卦象征聚集、荟萃。泽上于地，万物汇聚。得此卦者人气聚集，适合组织活动。君子以除戎器，戒不虞。聚而有备，盛而不乱。"},
    46: {"name": "地风升", "upper": 7, "lower": 4, "judgment": "元亨，用见大人，勿恤", "element": "土木",
         "interpretation": "升卦象征上升、晋升。地中生木，循序渐进。得此卦者事业稳步上升。积小以高大，顺而巽。踏踏实实往上走，终能达成目标。"},
    47: {"name": "泽水困", "upper": 1, "lower": 5, "judgment": "亨贞，大人吉无咎", "element": "金水",
         "interpretation": "困卦象征困境、受困。泽无水，枯竭之象。得此卦者正处困境之中，资源匮乏。君子以致命遂志，坚守信念终能脱困。"},
    48: {"name": "水风井", "upper": 5, "lower": 4, "judgment": "改邑不改井，无丧无得", "element": "水木",
         "interpretation": "井卦象征水井、养育。木上有水，井以养人。得此卦者宜修德养人，稳守根基。往来井井，汔至亦未繘井。根基不丢，进退从容。"},
    49: {"name": "泽火革", "upper": 1, "lower": 2, "judgment": "己日乃孚，元亨利贞", "element": "金火",
         "interpretation": "革卦象征变革、革新。泽中有火，水火相息。得此卦者面临重大变革。天地革而四时成，顺天应人。变革之时已到，宜主动求变。"},
    50: {"name": "火风鼎", "upper": 2, "lower": 4, "judgment": "元吉亨", "element": "火木",
         "interpretation": "鼎卦象征鼎器、更新。木上有火，烹饪之象。得此卦者宜革故鼎新，建立新秩序。君子以正位凝命。取新去旧，焕然一新。"},
    51: {"name": "震为雷", "upper": 3, "lower": 3, "judgment": "亨，震来虩虩，笑言哑哑", "element": "木木",
         "interpretation": "震卦象征震动、惊雷。洊雷震，君子以恐惧修省。得此卦者可能遇到突发事件。震惊百里，不丧匕鬯。临危不乱，借机自省。"},
    52: {"name": "艮为山", "upper": 6, "lower": 6, "judgment": "艮其背，不获其身", "element": "土土",
         "interpretation": "艮卦象征停止、静止。兼山艮，君子以思不出其位。得此卦者宜适可而止，知止不殆。时止则止，时行则行。动不失其时，其道光明。"},
    53: {"name": "风山渐", "upper": 4, "lower": 6, "judgment": "女归吉，利贞", "element": "木土",
         "interpretation": "渐卦象征渐进、缓慢发展。山上有木，以渐而高。得此卦者事情需循序渐进，不可急于求成。居贤德善俗，稳扎稳打。"},
    54: {"name": "雷泽归妹", "upper": 3, "lower": 1, "judgment": "征凶，无攸利", "element": "木金",
         "interpretation": "归妹卦象征婚嫁、结合。泽上有雷，归妹。得此卦者可能有结合之事（婚姻、合作等），但需谨慎。君子以永终知敝，预见到可能的结局。"},
    55: {"name": "雷火丰", "upper": 3, "lower": 2, "judgment": "亨，王假之，勿忧宜日中", "element": "木火",
         "interpretation": "丰卦象征丰盛、盛大。雷电皆至，光明盛大。得此卦者时运亨通，如日中天。君子以折狱致刑。盛极必衰，宜日中则昃的警惕。"},
    56: {"name": "火山旅", "upper": 2, "lower": 6, "judgment": "小亨，旅贞吉", "element": "火土",
         "interpretation": "旅卦象征旅行、客居。山上有火，旅。得此卦者可能处于变动、漂泊之中。君子以明慎用刑而不留狱。旅途中宜谨慎，不可久留。"},
    57: {"name": "巽为风", "upper": 4, "lower": 4, "judgment": "小亨，利有攸往，利见大人", "element": "木木",
         "interpretation": "巽卦象征顺入、谦逊。随风巽，君子以申命行事。得此卦者宜谦逊柔顺，顺势而入。重巽以申命，刚巽乎中正而志行。"},
    58: {"name": "兑为泽", "upper": 1, "lower": 1, "judgment": "亨利贞", "element": "金金",
         "interpretation": "兑卦象征喜悦、言说。丽泽兑，君子以朋友讲习。得此卦者人际关系和谐，心情愉悦。说以先民，民忘其劳。宜与人分享和交流。"},
    59: {"name": "风水涣", "upper": 4, "lower": 5, "judgment": "亨，王假有庙，利涉大川", "element": "木水",
         "interpretation": "涣卦象征涣散、离散。风行水上，涣。得此卦者可能人心涣散，需要凝聚。先王以享于帝立庙。宜建立核心，统合人心。"},
    60: {"name": "水泽节", "upper": 5, "lower": 1, "judgment": "亨，苦节不可贞", "element": "水金",
         "interpretation": "节卦象征节制、节度。泽上有水，节。得此卦者宜有节制，不可放纵。君子以制数度，议德行。节以制度，不伤财不害民。"},
    61: {"name": "风泽中孚", "upper": 4, "lower": 1, "judgment": "豚鱼吉，利涉大川，利贞", "element": "木金",
         "interpretation": "中孚卦象征诚信、信实。泽上有风，中孚。得此卦者以诚信为本。君子以议狱缓死。信及豚鱼，诚信能感动一切。"},
    62: {"name": "雷山小过", "upper": 3, "lower": 6, "judgment": "亨利贞，可小事不可大事", "element": "木土",
         "interpretation": "小过卦象征小有过越。山上有雷，小过。得此卦者宜做小事不宜大事。君子以行过乎恭，丧过乎哀，用过乎俭。小过可纠，大过则危。"},
    63: {"name": "水火既济", "upper": 5, "lower": 2, "judgment": "亨小，利贞，初吉终乱", "element": "水火",
         "interpretation": "既济卦象征已经成功。水在火上，既济。得此卦者事情已经完成，但需防盛极而衰。君子以思患而豫防之。守成更难，居安思危。"},
    64: {"name": "火水未济", "upper": 2, "lower": 5, "judgment": "亨，小狐汔济，濡其尾", "element": "火水",
         "interpretation": "未济卦象征尚未成功。火在水上，未济。得此卦者事情尚未完成，功亏一篑。君子以慎辨物居方。不可半途而废，坚持最后一步。"},
}


def get_hexagram_number(upper_trigram: int, lower_trigram: int) -> int:
    """根据上下卦索引找到卦序"""
    for num, info in HEXAGRAMS.items():
        if info["upper"] == upper_trigram and info["lower"] == lower_trigram:
            return num
    return 0


# ============================================================
# 六爻铜钱卦
# ============================================================

def coin_toss() -> int:
    """
    模拟三枚铜钱掷卦
    返回爻值：6=老阴(变爻) 7=少阳 8=少阴 9=老阳(变爻)
    """
    toss = [random.randint(0, 1) for _ in range(3)]
    heads = sum(toss)
    # 3个正面=老阳(9), 2正1反=少阴(8), 1正2反=少阳(7), 0正面=老阴(6)
    mapping = {3: 9, 2: 8, 1: 7, 0: 6}
    return mapping[heads]


def cast_hexagram() -> Tuple[List[int], List[int]]:
    """
    掷六次，从初爻到上爻
    返回：(爻值列表, 变爻位置列表)
    """
    lines = []
    changing = []
    for i in range(6):
        val = coin_toss()
        lines.append(val)
        if val in (6, 9):  # 老阴或老阳 = 变爻
            changing.append(i)
    return lines, changing


def lines_to_trigrams(lines: List[int]) -> Tuple[int, int]:
    """将六爻转为上下卦索引"""
    def line_to_yin_yang(val):
        return 1 if val in (7, 9) else 0  # 少阳/老阳→阳爻, 少阴/老阴→阴爻
    
    upper = (line_to_yin_yang(lines[5]) << 2) | (line_to_yin_yang(lines[4]) << 1) | line_to_yin_yang(lines[3])
    lower = (line_to_yin_yang(lines[2]) << 2) | (line_to_yin_yang(lines[1]) << 1) | line_to_yin_yang(lines[0])
    
    return TRIGRAM_BIN.get(upper, 7), TRIGRAM_BIN.get(lower, 7)


def get_changed_lines(lines: List[int], changing: List[int]) -> List[int]:
    """获取变卦的爻"""
    new_lines = lines.copy()
    for idx in changing:
        if new_lines[idx] == 6:
            new_lines[idx] = 7  # 老阴→少阳
        elif new_lines[idx] == 9:
            new_lines[idx] = 8  # 老阳→少阴
    return new_lines


def format_hexagram_result(lines: List[int], changing: List[int]):
    """格式化六爻占卜结果"""
    hex_name = {6: "老阴 ⚋⚊", 7: "少阳 ⚊", 8: "少阴 ⚋", 9: "老阳 ⚊⚋"}
    
    u1, l1 = lines_to_trigrams(lines)
    h_num = get_hexagram_number(u1, l1)
    h_info = HEXAGRAMS.get(h_num, {"name": "未知卦"})
    
    # 变卦
    changed_lines = get_changed_lines(lines, changing)
    u2, l2 = lines_to_trigrams(changed_lines)
    ch_num = get_hexagram_number(u2, l2)
    ch_info = HEXAGRAMS.get(ch_num, {"name": "未知卦"})
    
    result = {
        "本卦": {"序号": h_num, "名称": h_info["name"], "上卦": BAGUA[u1]["name"], "下卦": BAGUA[l1]["name"]},
        "变卦": {"序号": ch_num, "名称": ch_info["name"], "上卦": BAGUA[u2]["name"], "下卦": BAGUA[l2]["name"]} if changing else None,
        "爻象": [],
        "变爻": [i+1 for i in changing],
    }
    
    for i in range(5, -1, -1):
        pos = ["上爻", "五爻", "四爻", "三爻", "二爻", "初爻"][i]
        marker = " ← 变爻" if i in changing else ""
        yao_type = "阳" if lines[i] in (7, 9) else "阴"
        result["爻象"].append(f"  {pos}: {hex_name[lines[i]]}（{yao_type}）{marker}")
    
    return result


def interpret_coin_divination(lines: List[int], changing: List[int]):
    """解读六爻占卜"""
    u1, l1 = lines_to_trigrams(lines)
    h_num = get_hexagram_number(u1, l1)
    h_info = HEXAGRAMS.get(h_num)
    
    if not h_info:
        return "无法解读"
    
    out = []
    out.append(f"📯 六爻铜钱占卜")
    out.append(f"")
    out.append(f"🔮 本卦：第{h_num}卦「{h_info['name']}」")
    out.append(f"   上{BAGUA[u1]['name']}({BAGUA[u1]['nature']})下{BAGUA[l1]['name']}({BAGUA[l1]['nature']})")
    out.append(f"   卦辞：{h_info['judgment']}")
    out.append(f"   解读：{h_info['interpretation']}")
    
    if changing:
        changed_lines = get_changed_lines(lines, changing)
        u2, l2 = lines_to_trigrams(changed_lines)
        ch_num = get_hexagram_number(u2, l2)
        ch_info = HEXAGRAMS.get(ch_num)
        
        out.append(f"")
        out.append(f"🔄 变卦：第{ch_num}卦「{ch_info['name']}」")
        out.append(f"   变爻位置：第{', '.join(map(str, [i+1 for i in changing]))}爻")
        out.append(f"   卦辞：{ch_info['judgment']}")
        out.append(f"   解读：{ch_info['interpretation']}")
        
        # 综合解读
        out.append(f"")
        out.append(f"📖 综合解读：")
        out.append(f"   本卦「{h_info['name']}」代表当前状态，变卦「{ch_info['name']}」代表发展趋势。")
        
        if len(changing) == 1:
            yao = changing[0] + 1
            out.append(f"   第{yao}爻为变爻，是本卦的关键动点，请重点关注此爻的变化趋势。")
        elif len(changing) >= 2:
            out.append(f"   本卦有{len(changing)}个变爻，变化较为复杂。以本卦为主参考当前，变卦为未来走向。")
    else:
        out.append(f"")
        out.append(f"📌 本卦六爻皆静，无变爻。以本卦卦辞为主要参考。")
    
    return "\n".join(out)


# ============================================================
# 梅花易数
# ============================================================

def meihua_number_divination(numbers: List[int]) -> Dict:
    """梅花易数 - 数字起卦法"""
    if len(numbers) < 3:
        # 补足用当前时间
        now = datetime.now()
        while len(numbers) < 3:
            numbers.append(now.microsecond % 100)
    
    upper_idx = numbers[0] % 8
    lower_idx = numbers[1] % 8
    dongyao = numbers[2] % 6  # 0-5, 对应初爻到上爻
    
    h_num = get_hexagram_number(upper_idx, lower_idx)
    h_info = HEXAGRAMS.get(h_num, {"name": "未知卦"})
    
    # 互卦
    # 本卦六爻: 初(0)二(1)三(2)四(3)五(4)上(5)
    # 互卦上卦 = 本卦三四五爻
    # 互卦下卦 = 本卦二三四爻
    # 这里简化处理
    
    # 变卦：动爻变
    changed_upper = upper_idx
    changed_lower = lower_idx
    # 动爻在上卦(爻4-6)或下卦(爻1-3)
    if dongyao >= 3:  # 上卦
        # 动上卦中的某爻
        pass
    else:  # 下卦
        pass
    
    ch_num = get_hexagram_number(upper_idx, lower_idx)  # 简化
    
    return {
        "方法": "梅花易数·数字起卦",
        "数字": numbers[:3],
        "上卦": BAGUA[upper_idx],
        "下卦": BAGUA[lower_idx],
        "动爻": dongyao + 1,
        "本卦": {"序号": h_num, "名称": h_info["name"]},
        "解读": h_info.get("interpretation", ""),
    }


def meihua_time_divination():
    """梅花易数 - 时间起卦法（农历时间）"""
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    
    # 时辰对应: 子1 丑2 寅3 ...
    hour_zhi = ((hour + 1) // 2) % 12 + 1
    
    upper = (year + month + day) % 8
    lower = (year + month + day + hour_zhi) % 8
    dongyao = (year + month + day + hour_zhi) % 6
    
    return meihua_number_divination([upper if upper != 0 else 8, lower if lower != 0 else 8, dongyao if dongyao != 0 else 6])


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("周易占卜工具")
        print()
        print("用法:")
        print("  python iching.py coin              — 六爻铜钱卦（随机掷六次）")
        print("  python iching.py meihua [n1 n2 n3] — 梅花易数（数字起卦）")
        print("  python iching.py meihua time       — 梅花易数（时间起卦）")
        print("  python iching.py hex [序号]         — 查看指定卦的详细解读")
        print("  python iching.py list              — 列出全部64卦")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "coin":
        lines, changing = cast_hexagram()
        result = format_hexagram_result(lines, changing)
        
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print(result["爻象"][0].replace("  ", ""))
            for i in range(1, 5):
                print(result["爻象"][i].replace("  ", ""))
            print(result["爻象"][5].replace("  ", ""))
            print("=" * 60)
            print()
            print(interpret_coin_divination(lines, changing))
    
    elif cmd == "meihua":
        if len(sys.argv) >= 5:
            numbers = [int(x) for x in sys.argv[2:5]]
        elif len(sys.argv) >= 3 and sys.argv[2] == "time":
            numbers = None
        else:
            # 随机生成
            numbers = [random.randint(1, 999) for _ in range(3)]
        
        if numbers is None:
            result = meihua_time_divination()
        else:
            result = meihua_number_divination(numbers)
        
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("=" * 60)
            print(f"  🌸 梅花易数占卜")
            if numbers:
                print(f"  起卦数字：{numbers}")
            print("=" * 60)
            print(f"  上卦：{result['上卦']['symbol']} {result['上卦']['name']}（{result['上卦']['nature']}）")
            print(f"  下卦：{result['下卦']['symbol']} {result['下卦']['name']}（{result['下卦']['nature']}）")
            print(f"  动爻：第{result['动爻']}爻")
            print(f"  本卦：第{result['本卦']['序号']}卦「{result['本卦']['名称']}」")
            print(f"  解读：{result['解读']}")
            print("=" * 60)
    
    elif cmd == "hex":
        if len(sys.argv) < 3:
            print("请指定卦序号，如: python iching.py hex 1")
            sys.exit(1)
        num = int(sys.argv[2])
        info = HEXAGRAMS.get(num)
        if not info:
            print(f"未找到第{num}卦")
            sys.exit(1)
        
        print("=" * 60)
        print(f"  第{num}卦：{info['name']}")
        print("=" * 60)
        print(f"  上卦：{BAGUA[info['upper']]['symbol']} {BAGUA[info['upper']]['name']}（{BAGUA[info['upper']]['nature']}）")
        print(f"  下卦：{BAGUA[info['lower']]['symbol']} {BAGUA[info['lower']]['name']}（{BAGUA[info['lower']]['nature']}）")
        print(f"  五行：{info['element']}")
        print(f"  卦辞：{info['judgment']}")
        print(f"  解读：{info['interpretation']}")
        print("=" * 60)
    
    elif cmd == "list":
        print("六十四卦速查表：")
        print("-" * 60)
        for num in sorted(HEXAGRAMS.keys()):
            info = HEXAGRAMS[num]
            upper_sym = BAGUA[info['upper']]['symbol']
            lower_sym = BAGUA[info['lower']]['symbol']
            print(f"  {num:2d}. {info['name']:<8s} {upper_sym}{lower_sym}  {info['judgment']}")
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()