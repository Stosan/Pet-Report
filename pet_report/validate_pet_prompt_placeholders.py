#validate_pet_prompt_placeholders.py

import os
import re
import json

# Define the path to your prompt definitions
PROMPT_DEFS_PATH = "./pet_report/prompt_definitions_pet.py"

# Define known safe base fallbacks
BASE_PLACEHOLDER_FALLBACKS_PET = {
    "pet_name", "species", "pet_sound", "sun_sign_name", "moon_sign_name", "rising_sign_name",
    "venus_sign_name", "mars_sign_name", "mercury_sign_name", "north_node_sign_name", "south_node_sign_name",
    "chiron_sign_name", "black_moon_lilith_sign_name", "dominant_element_1", "dominant_element_2",
    "dominant_modality_1", "dominant_modality_2", "element_balance", "modality_balance",
    "moon_phase_name", "keyword_adj_1_for_sun_sign_name", "keyword_adj_1_for_moon_sign_name",
    "keyword_adj_1_for_mercury_sign_name", "keyword_noun_1_for_venus_sign_name",
    "keyword_adj_1_for_mars_sign_name", "keyword_adj_1_for_north_node_sign_name",
    "keyword_adj_1_for_south_node_sign_name", "example_behavior_karmic_theme_1",
    "moon_sign_emotional_need", "planet_or_point_fixed_star_1", "keyword_trait_for_sign1_dominant",
    "chart_ruler", "common_positive_breed_trait_1", "keyword_adj_1_for_rising_sign_name",
    "keyword_adj_2_for_rising_sign_name", "keyword_noun_1_for_sun_sign_name", "keyword_adv_1_for_sun_sign_name",
    "keyword_noun_1_for_moon_sign_name", "keyword_adv_1_for_moon_sign_name", "keyword_noun_1_for_mercury_sign_name",
    "keyword_adv_1_for_mercury_sign_name", "keyword_adj_1_for_venus_sign_name", "keyword_noun_1_for_venus_sign_name",
    "keyword_adv_1_for_venus_sign_name", "keyword_adj_1_for_mars_sign_name", "keyword_noun_1_for_mars_sign_name",
    "keyword_adv_1_for_mars_sign_name", "keyword_adj_2_for_north_node_sign_name", "keyword_noun_1_for_north_node_sign_name",
    "fixed_star_1_name", "dominant_sign_1", "karmic_theme_1", "Example 1 for Fire dominant",
    "common_positive_breed_trait_2", "nickname", "element_modality", "breed", "breed_name",
    "client_name", "birth_date", "birth_time", "elemental_style", "aspect_description_1", "aspect_description_2"
}

# Regex pattern to capture placeholders in {placeholder_name}
placeholder_pattern = re.compile(r"\{([^}]+)\}")

# Parse the Python prompt file safely
def extract_placeholders_from_prompt_defs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        file_contents = f.read()

    # Extract the PET_PROMPTS list from the file
    match = re.search(r"PET_PROMPTS\s*=\s*(\[[\s\S]+?\])\n\n", file_contents)
    if not match:
        raise ValueError("Could not locate PET_PROMPTS list in the file.")

    # Evaluate the list safely
    prompt_json = eval(match.group(1), {"__builtins__": None}, {})

    all_placeholders_used = set()
    for section in prompt_json:
        for key in ["header", "header_template", "quote"]:
            if key in section and isinstance(section[key], str):
                found = placeholder_pattern.findall(section[key])
                all_placeholders_used.update(found)

        if "ai_prompt_parts" in section:
            parts = section["ai_prompt_parts"]
            if isinstance(parts, dict):
                for subpart in parts.values():
                    if isinstance(subpart, str):
                        found = placeholder_pattern.findall(subpart)
                        all_placeholders_used.update(found)
                    elif isinstance(subpart, dict):
                        for val in subpart.values():
                            if isinstance(val, str):
                                found = placeholder_pattern.findall(val)
                                all_placeholders_used.update(found)

    return all_placeholders_used

used_placeholders = extract_placeholders_from_prompt_defs(PROMPT_DEFS_PATH)

missing_from_fallbacks = sorted(used_placeholders - BASE_PLACEHOLDER_FALLBACKS_PET)

import pandas as pd
import ace_tools as tools; tools.display_dataframe_to_user(name="Missing Placeholders", dataframe=pd.DataFrame(missing_from_fallbacks, columns=["Missing Placeholder"]))
