from enum import IntEnum


class Stat(IntEnum):
    Str = 0
    Agi = 1
    Vit = 2
    Int = 3
    Dex = 4
    Luk = 5


class WeaponType(IntEnum):
    Mace = 0


class Weapon:
    def __init__(self, weapon_type: WeaponType, damage, damage_modifier = 1.0):
        self.type = weapon_type
        self.damage = damage
        self.damage_modifier = damage_modifier


class CharacterClass(IntEnum):
    Monk = 0


class Character:
    def __init__(self, character_class: CharacterClass, base_level, weapon: Weapon, transcended = False):
        self.character_class = character_class
        self.base_level = base_level
        self.weapon = weapon
        self.transcended = transcended


def determine_optimal_stats(character: Character, minimum_flee=0, minimum_hit=0):
    return max(
        (stats for stats in generate_stat_distributions(character)),
        key=lambda stats: determine_score(character, stats, minimum_flee, minimum_hit)
    )


INITIAL_STAT = 1
MAXIMUM_STAT = 99
INITIAL_STATS = (
    1,
    1,
    1,
    1,
    1,
    1
)
INITIAL_STAT_POINTS = 48
INITIAL_STAT_POINTS_TRANSCENDED = 100
MELEE_WEAPON_TYPES = {WeaponType.Mace}
# See: https://wiki.talonro.com/ASPD#Weapon_Delay
WEAPON_DELAYS = {
    CharacterClass.Monk: {
        WeaponType.Mace: 57.5
    }
}
LAST_STAT = max(Stat)


def generate_stat_distributions(character):
    stats = list(INITIAL_STATS)
    available_stat_points = determine_total_available_stat_points(character)
    yield from generate_stat_distributions_sub(character, stats, Stat.Str, available_stat_points)


def generate_stat_distributions_sub(character, stats, stat, available_stat_points):
    stats = stats.copy()
    stats[stat] = INITIAL_STAT
    yield from generate_stat_distributions_sub2(character, stats, stat, available_stat_points)
    while (
        stats[stat] <= MAXIMUM_STAT and
        available_stat_points >= determine_cost_for_next_stat_point(stats[stat])
    ):
        stats[stat] += 1
        available_stat_points -= determine_cost_for_stat_point(stats[stat])
        yield from generate_stat_distributions_sub2(character, stats, stat, available_stat_points)


def generate_stat_distributions_sub2(character, stats, stat, available_stat_points):
    if stat < LAST_STAT:
        yield from generate_stat_distributions_sub(character, stats, Stat(stat + 1), available_stat_points)
    elif available_stat_points < determine_cost_for_next_stat_point(stats[stat]):
        yield stats


def determine_total_available_stat_points(character):
    return determine_initial_stat_points(character) + determine_stat_points_received_for_level_ups(character.base_level)


def determine_initial_stat_points(character):
    return INITIAL_STAT_POINTS_TRANSCENDED if character.transcended else INITIAL_STAT_POINTS


def determine_stat_points_received_for_level_ups(base_level):
    stat_points = 0
    for level in range(1, base_level):
        stat_points += level // 5 + 3
    return stat_points


def determine_cost_for_next_stat_point(stat_point_amount):
    return determine_cost_for_stat_point(stat_point_amount + 1)


def determine_cost_for_stat_point(stat_point):
    return (stat_point - 1) // 10 + 2


def determine_score(character, stats, minimum_flee, minimum_hit):
    flee = calculate_flee(character, stats)
    if flee < minimum_flee:
        return 0
    hit = calculate_hit(character, stats)
    if hit < minimum_hit:
        return 0
    else:
        return determine_dps(character, stats)


def calculate_flee(character, stats):
    skill_bonus = 15  # Level 10 Monk Flee
    level = character.base_level
    agi = stats[Stat.Agi]
    item_bonus = 12  # Eden Group Manteau II
    mobs = 1
    return skill_bonus + 100 + (level + agi + item_bonus) * (1 - ((mobs - 2) * 0.1))


def calculate_hit(character, stats):
    dex = stats[Stat.Dex]
    other_bonuses = 0
    return dex + other_bonuses + character.base_level


def determine_dps(character, stats):
    atk = character.weapon.damage_modifier * character.weapon.damage + \
        stats[Stat.Str] + \
        stats[Stat.Dex] // 5 + \
        stats[Stat.Luk] // 5
    triple_attack_chance = 0.20
    atk = (1 - triple_attack_chance) * atk + triple_attack_chance * (3 + 4 + 5.4) * atk
    aspd = calculate_aspd(character, stats)
    hits_per_second = calculate_hits_per_second(aspd)
    return atk * hits_per_second


def calculate_total_damage_from_dex(weapon_type, dex):
    if is_melee_weapon_type(weapon_type):
        return dex // 5


def calculate_total_damage_from_luk(weapon_type, luk):
    return luk // 5


def calculate_aspd(character, stats):
    weapon_delay = WEAPON_DELAYS[character.character_class][character.weapon.type]
    agi = stats[Stat.Agi]
    dex = stats[Stat.Dex]
    speed_mods = 0.1  # Concentration Potion
    return 200 - (weapon_delay - ((weapon_delay * agi / 25) + (weapon_delay * dex / 100)) / 10) * (1 - speed_mods)


def calculate_hits_per_second(aspd):
    return 50 / (200 - aspd)


def is_melee_weapon_type(weapon_type):
    return weapon_type in MELEE_WEAPON_TYPES


if __name__ == '__main__':
    base_level = 84
    stats = (
        1,
        1,
        1,
        1,
        1,
        1
    )
    weapon = Weapon(
        WeaponType.Mace,
        damage=175,
        damage_modifier=1.4
    )
    character = Character(
        CharacterClass.Monk,
        base_level,
        weapon
    )
    stats = determine_optimal_stats(
        character,
        minimum_flee=195,
        minimum_hit=116
    )
    print(stats)
