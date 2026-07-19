#!/usr/bin/env python3
"""
OP Kit Omega — Command Generator
Parse NBT kit dan generate /give commands untuk Java & Bedrock
Usage: python3 gen_commands.py [--java | --bedrock | --chest]
"""

import json
import sys

# Enchantment ID → name mapping (Bedrock/Java hybrid)
ENCH_MAP = {
    0:  ("protection",           "protection"),
    1:  ("fire_protection",      "fire_protection"),
    2:  ("feather_falling",      "feather_falling"),
    3:  ("blast_protection",     "blast_protection"),
    4:  ("projectile_protection","projectile_protection"),
    5:  ("respiration",          "respiration"),
    6:  ("aqua_affinity",        "aqua_affinity"),
    7:  ("thorns",               "thorns"),
    8:  ("depth_strider",        "depth_strider"),
    9:  ("unbreaking",           "unbreaking"),
    10: ("sharpness",            "sharpness"),
    11: ("smite",                "smite"),
    12: ("bane_of_arthropods",   "bane_of_arthropods"),
    13: ("knockback",            "knockback"),
    14: ("fire_aspect",          "fire_aspect"),
    15: ("looting",              "looting"),
    16: ("efficiency",           "efficiency"),
    17: ("silk_touch",           "silk_touch"),
    18: ("fortune",              "fortune"),
    19: ("power",                "power"),
    20: ("punch",                "punch"),
    21: ("flame",                "flame"),
    22: ("infinity",             "infinity"),
    23: ("luck_of_the_sea",      "luck_of_the_sea"),
    24: ("lure",                 "lure"),
    25: ("frost_walker",         "frost_walker"),
    26: ("mending",              "mending"),
    27: ("binding_curse",        "curse_of_binding"),
    28: ("vanishing_curse",      "curse_of_vanishing"),
    29: ("impaling",             "impaling"),
    30: ("riptide",              "riptide"),
    31: ("loyalty",              "loyalty"),
    32: ("channeling",           "channeling"),
    33: ("multishot",            "multishot"),
    34: ("piercing",             "piercing"),
    35: ("quick_charge",         "quick_charge"),
}

# Kit definition
KIT = [
    {"name": "diamond_sword",      "count": 1,  "ench": [10,11,12,13,14,15,9,26,7]},
    {"name": "bow",                 "count": 1,  "ench": [19,20,21,22,9,26]},
    {"name": "arrow",               "count": 64, "ench": []},
    {"name": "diamond_pickaxe",     "count": 1,  "ench": [16,18,17,9,26]},
    {"name": "diamond_shovel",      "count": 1,  "ench": [16,18,17,9,26]},
    {"name": "diamond_axe",         "count": 1,  "ench": [16,18,17,10,9,26]},
    {"name": "diamond_helmet",      "count": 1,  "ench": [0,3,4,1,5,6,7,9,26]},
    {"name": "diamond_chestplate",  "count": 1,  "ench": [0,3,4,1,7,9,26]},
    {"name": "diamond_leggings",    "count": 1,  "ench": [0,3,4,1,7,9,26]},
    {"name": "diamond_boots",       "count": 1,  "ench": [0,3,4,1,2,8,7,9,26]},
    {"name": "elytra",              "count": 1,  "ench": [9,26]},
    {"name": "shield",              "count": 1,  "ench": [9,26]},
    {"name": "fishing_rod",         "count": 1,  "ench": [23,24,9,26]},
    {"name": "flint_and_steel",     "count": 1,  "ench": [9,26]},
    {"name": "shears",              "count": 1,  "ench": [16,9,26]},
    {"name": "enchanted_golden_apple","count": 64,"ench": []},
    {"name": "enchanted_golden_apple","count": 64,"ench": []},
    {"name": "enchanted_golden_apple","count": 64,"ench": []},
    {"name": "experience_bottle",   "count": 64, "ench": []},
    {"name": "wither_spawn_egg",    "count": 64, "ench": []},
    {"name": "ender_dragon_spawn_egg","count": 64,"ench": []},
    {"name": "elder_guardian_spawn_egg","count": 64,"ench": []},
    {"name": "tnt",                 "count": 64, "ench": []},
]

LEVEL = 32767

def gen_java():
    print("# OP Kit Omega — Java Edition Give Commands")
    print("# Paste ke command block atau chat (butuh OP)\n")
    for item in KIT:
        name = item["name"]
        count = item["count"]
        enchs = item["ench"]
        if enchs:
            ench_str = ",".join(
                f'{{id:"minecraft:{ENCH_MAP[e][1]}",lvl:{LEVEL}s}}' for e in enchs
            )
            nbt = f'{{Unbreakable:1b,Enchantments:[{ench_str}]}}'
            print(f'give @p minecraft:{name}{nbt} {count}')
        else:
            print(f'give @p minecraft:{name} {count}')
    print(f"\n# Total items: {len(KIT)}")

def gen_bedrock():
    print("# OP Kit Omega — Bedrock Edition Give Commands")
    print("# Paste ke chat satu per satu (butuh OP/cheats)\n")
    for item in KIT:
        name = item["name"]
        count = item["count"]
        enchs = item["ench"]
        if enchs:
            ench_entries = ", ".join(
                f'"{ENCH_MAP[e][0]}": {LEVEL}' for e in enchs
            )
            nbt = '{' + f'"minecraft:enchantments":{{"enchantments":{{{ench_entries}}}}}' + '}'
            print(f'/give @s {name} {count} 0 {nbt}')
        else:
            print(f'/give @s {name} {count}')
    print(f"\n# Total commands: {len(KIT)}")

def gen_chest_cmd():
    """Generate single /setblock command (Java) untuk chest dengan semua item"""
    print("# Single Command — Summon chest dengan OP Kit (Java Edition)")
    print("# Paste ke chat sebagai 1 command (bisa panjang — pakai command block!)\n")
    items_nbt = []
    for i, item in enumerate(KIT):
        name = item["name"]
        count = item["count"]
        enchs = item["ench"]
        slot_tag = f"Slot:{i}b"
        if enchs:
            ench_str = ",".join(
                f'{{id:"minecraft:{ENCH_MAP[e][1]}",lvl:{LEVEL}s}}' for e in enchs
            )
            item_str = f'{{id:"minecraft:{name}",Count:{count}b,{slot_tag},tag:{{Unbreakable:1b,Enchantments:[{ench_str}]}}}}'
        else:
            item_str = f'{{id:"minecraft:{name}",Count:{count}b,{slot_tag}}}'
        items_nbt.append(item_str)

    all_items = ",".join(items_nbt)
    cmd = f'/setblock ~ ~1 ~ minecraft:chest{{Items:[{all_items}]}} replace'
    print(cmd)
    print(f"\n# Command length: {len(cmd)} chars")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--java"
    if mode == "--bedrock":
        gen_bedrock()
    elif mode == "--chest":
        gen_chest_cmd()
    else:
        gen_java()
