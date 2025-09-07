#--- START OF FILE run_pet_report.py ---

import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

# run_pet_report.py (Orchestrator Script)
# VERSION 1.0.47 - PATCH 19: AI Prompt Cleaning & Page Order Fixes
# VERSION 1.0.46 - PATCH 12: Gender Arg & Pronoun Mode Propagation
# VERSION 1.0.45 - PATCH 12: Full Memorial & Pronoun System (Refined)
# VERSION 1.0.44 - PATCH 11: Memorial Mode Cleanup (Hide AI instruction from PDF)
# VERSION 1.0.43 - PATCH 10: Memorial Mode Finalization (Tone & Tense)
# VERSION 1.0.42 - Integrated AI Pet Portrait feature (CLI simulation)
# VERSION 1.0.41 - PATCH 9: Integrated dynamic species-specific example blocks.
# ... (previous version history)

# Standard library imports
import argparse
import json
import traceback
import logging
import re # Added for cleaning voice annotations and other text processing
from datetime import datetime
from collections import Counter
import uuid # For unique temporary file names for uploaded images

# --- OpenAI client type check for CLI invocation guard ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Attempt to import Pillow for chart image placeholder ---
try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    pillow_available = True
except ImportError:
    pillow_available = False
    PILImage = None
    ImageDraw = None
    ImageFont = None 
    print("INFO: Pillow (PIL) library not found. Cannot create placeholder chart image if needed.")

# --- Key Project Modules ---
try:
    from common.advanced_calculate_astrology import calculate_pet_chart 
    from common.generate_chart_image import generate_chart_image, DEFAULT_CHART_STYLE
    from pet_report.prompt_definitions_pet import (
        PET_PROMPTS as PROMPTS,
        SECTION_LAYOUT_PRESETS,
        SECTIONS_FOR_PET_REPORT
    )
    from common.voice_engine import apply_voice_to_prompt, PET_VOICE_PERSONA
    from common.utils_pet import get_species_example_block 
    from image_ai import generate_cosmic_pet_image 
    try:
        from pet_report.pdf_generator_pet import generate_astrology_pdf as generate_pet_pdf
        print("INFO: Imported generate_astrology_pdf from pet_report.pdf_generator_pet")
    except ImportError:
        try:
             from pet_report.pet_report import generate_pet_pdf # Fallback
             print("INFO: Imported generate_pet_pdf from pet_report.pet_report (fallback)")
        except ImportError as e_inner:
             print(f"ERROR: Could not import PDF generation function: {e_inner}")
             def generate_pet_pdf(**kwargs): # Dummy function
                 print("ERROR: PDF Generator function not found!")
                 return False
except ImportError as e:
    print(f"ERROR: Oh no! Python couldn't find one of the important code pieces: {e}")
    print(f"The missing part seems to be related to: {e.name}")
    current_path = sys.path
    print("\nCurrent sys.path:")
    for p in current_path:
        print(p)
    print(f"\nProject root added to path: {project_root}")
    sys.exit(1)

# ─── Helper to strip internal annotations ───
# PATCH 19: Updated regex to be comprehensive, matching pdf_generator_pet.py
def _clean_mika_voice(text: str) -> str:
    """
    Remove any parenthetical annotations like (Mika’s Voice: …), 
    (Reminder: This is a loving tribute...), etc. from the given string.
    Handles surrounding whitespace and is case-insensitive.
    """
    if not isinstance(text, str):
        return text
    # This regex aims to remove "(Mika's Voice:...)", "(Reminder: This is a loving tribute...)", etc.
    return re.sub(r"\s*\(\s*(?:Mika['’]s Voice:|Reminder: This is a loving tribute for.*?|This section is part of a loving memorial for.*?|Instruction to AI:.*?|Note to AI:.*?)[^)]*\)\s*", " ", text, flags=re.IGNORECASE | re.DOTALL).strip()

# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- Astrological Symbol Mapping for Text Replacement ---
ASTRO_SYMBOL_MAP = {
    "☉": "[Sun]", "☽": "[Moon]", "☿": "[Mercury]", "♀": "[Venus]", "♂": "[Mars]",
    "♃": "[Jupiter]", "♄": "[Saturn]", "♅": "[Uranus]", "♆": "[Neptune]", "♇": "[Pluto]",
    "☊": "[N.Node]", "☋": "[S.Node]", "♈": "[Ari]", "♉": "[Tau]",
    "♊": "[Gem]", "♋": "[Can]", "♌": "[Leo]", "♍": "[Vir]", "♎": "[Lib]",
    "♏": "[Sco]", "♐": "[Sag]", "♑": "[Cap]", "♒": "[Aqu]", "♓": "[Pis]",
    "⚷": "[Chr]", 
}

# --- SYMBOL PATCH MAP ---
SYMBOL_PLACEHOLDER_TO_GLYPH_MAP = {
    "[Sun]": "☉",
    "[Moon]": "☽",
    "[Mercury]": "☿",
    "[Venus]": "♀",
    "[Mars]": "♂",
    "[Jupiter]": "♃",
    "[Saturn]": "♄",
    "[Uranus]": "♅",
    "[Neptune]": "♆",
    "[Pluto]": "♇",
    "[North Node]": "☊",
    "[South Node]": "☋",
    "[Chiron]": "⚷",
    "[Lilith]": "⚸"
}


# --- Utility function to clean template strings ---
def clean_template_string_for_formatting(template_str: str) -> str:
    if not isinstance(template_str, str):
        return template_str

    def replacer(match):
        content_in_braces = match.group(1).strip()
        key_part = re.split(r'[#,]', content_in_braces, 1)[0].strip()
        return "{" + key_part + "}"
    return re.sub(r"\{([_a-zA-Z0-9]+)\s*(?:#.*?|,.*?)\}", r"{\1}", template_str)


# --- Function to extract all CLEAN placeholders from prompt definitions ---
def get_all_placeholders_from_prompts_definitions(prompts_list):
    placeholders = set()
    placeholder_pattern = re.compile(r"\{([_a-zA-Z0-9]+)\}")

    def extract_from_string(s):
        if isinstance(s, str):
            temp_cleaned_s = clean_template_string_for_formatting(s)
            found_placeholders_content = placeholder_pattern.findall(temp_cleaned_s)
            for item_key in found_placeholders_content:
                if item_key:
                    placeholders.add(item_key)
    def traverse(data):
        if isinstance(data, dict):
            for value in data.values():
                traverse(value)
        elif isinstance(data, list):
            for item in data:
                traverse(item)
        elif isinstance(data, str):
            extract_from_string(data)
    traverse(prompts_list)
    return placeholders

CLEANED_PLACEHOLDER_KEYS = get_all_placeholders_from_prompts_definitions(PROMPTS)
logger.info(f"Extracted {len(CLEANED_PLACEHOLDER_KEYS)} unique cleaned placeholder keys from prompt definitions.")


# --- Base Placeholder Fallbacks for Pet Reports (Comprehensive & Synchronized) ---
BASE_PLACEHOLDER_FALLBACKS_PET = {
    # Core Info
    "pet_name": "Your Beloved Pet", "species": "companion", "pet_sound": "gentle sound",
    "nickname": "Buddy", "client_name": "Valued Guardian",
    "birth_date": "a recent January 1st", 
    "birth_date_formatted": "a very special day in time", 
    "birth_time": "High Noon", "birth_location": "a magical place",
    "breed": "a truly unique and special mix", 
    "pet_breed": "a unique soul", 
    "breed_name": "Special Blend",
    "breed_lowercase_article_noun_phrase": "a one-of-a-kind friend",
    "species_plural": "companions",
    "age": "a delightful age",

    # Astrological Signs
    "sun_sign_name": "Leo", "moon_sign_name": "Cancer", "rising_sign_name": "Virgo",
    "mercury_sign_name": "Gemini", "venus_sign_name": "Libra", "mars_sign_name": "Aries",
    "jupiter_sign_name": "Sagittarius", "saturn_sign_name": "Capricorn", "uranus_sign_name": "Aquarius",
    "neptune_sign_name": "Pisces", "pluto_sign_name": "Scorpio",
    "north_node_sign_name": "Sagittarius", "south_node_sign_name": "Gemini",
    "chiron_sign_name": "Pisces", "black_moon_lilith_sign_name": "Scorpio",
    "north_node_sign": "Sagittarius",

    # Dominants
    "dominant_sign_1": "Leo", "dominant_sign_2": "Cancer",
    "dominant_element": "a mysterious cosmic essence", "dominant_element_1": "Fire", "dominant_element_2": "Earth",
    "dominant_modality": "a curious cosmic rhythm", "dominant_modality_1": "Fixed", "dominant_modality_2": "Mutable",
    "least_represented_element": "an area for gentle exploration",

    # Elemental/Modality Descriptions
    "element_balance": "a harmonious blend of energies", "modality_balance": "a flexible approach to life's adventures",
    "element_modality": "a vibrant tapestry of energies", "elemental_style": "their unique cosmic signature",
    "element_1_description": "a primary energetic force shaping their being",
    "element_2_description": "a secondary energetic influence adding depth",
    "element_dominance_style_phrase": "a fascinating blend of elemental energies",
    "Elemental Style explanation": "their fundamental way of interacting with the world, full of sparkle",
    "Modality Style explanation": "how they instinctively approach challenges and opportunities",
    "Combined vibe example": "a truly unique and enchanting character, full of surprises",
    "Short example of dominant element behavior": "acting on their primary energetic drive with enthusiasm",
    "Short example of dominant modality behavior": "using their typical, charming approach to situations",
    "fire_percentage": 25.0, "earth_percentage": 25.0, "air_percentage": 25.0, "water_percentage": 25.0,

    # Moon & Karmic
    "moon_phase_name": "Full Moon",
    "moon_sign_emotional_need": "plenty of snuggles and a safe, cozy hideaway",
    "example_behavior_karmic_theme_1": "heroically barking at shadows to defend the homestead",
    "karmic_theme_1": "learning the profound depths of unconditional love and trust",
    "karmic_pattern_2": "a familiar, comforting old habit, like a well-loved chew toy",
    "example_behavior_karmic_pattern_2": "repeating a cherished daily routine with gusto",
    "karmic_lessons_example_behavior_theme_1": "bravely sniffing a new toy with cautious optimism",
    "karmic_lessons_example_behavior_pattern_2": "insisting on the same sunny nap spot every afternoon",
    "karmic_lessons_example_1": "tentatively exploring a new part of the garden",
    "karmic_lessons_example_2": "learning to share their favorite chew toy (sometimes!)",
    "karmic_lessons_example_3": "waiting patiently (for a whole three seconds!) for a treat",


    # Fixed Stars
    "planet_or_point_fixed_star_1": "their Moon conjunct the bright star Sirius",
    "fixed_star_1_name": "Sirius", "fixed_star_1_traits": "a touch of brilliance, loyalty, and a hint of ancient wisdom",
    "fixed_star_1_brief_behavior_example": "showing an uncanny understanding or a noble gaze",
    "optional_fixed_star_2_prompt_text": "",
    "fixed_star_2_name": "Regulus", "planet_or_point_fixed_star_2": "their Sun conjunct the regal star Regulus",
    "fixed_star_2_traits": "a regal and noble bearing, with a flair for the dramatic",
    "fixed_star_2_brief_behavior_example": "acting like the true king or queen of the castle",
    "optional_fixed_star_2": "",

    # Aspects & Chart Ruler
    "aspect_description_1": "a harmonious cosmic dance between their inner planets",
    "aspect_description_2": "an intriguing stellar dialogue adding unique quirks",
    "chart_ruler": "Mars, the planet of action",
    "aspects_example_1": "suddenly switching from playful zoomies to intense bird-watching",
    "aspects_example_2": "knowing exactly when you're about to open the treat bag from three rooms away",
    "aspects_example_3": "masterfully hiding your sock and then looking completely innocent",


    # Keywords
    "sun_sign_keyword_adj_1": "radiant", "sun_sign_keyword_noun_1": "vitality", "sun_sign_keyword_adv_1": "brightly",
    "moon_sign_keyword_adj_1": "sensitive", "moon_sign_keyword_noun_1": "comfort", "moon_sign_keyword_adv_1": "softly",
    "mercury_sign_keyword_adj_1": "quick-witted", "mercury_sign_keyword_noun_1": "chatter", "mercury_sign_keyword_adv_1": "nimbly",
    "venus_sign_keyword_adj_1": "charming", "venus_sign_keyword_noun_1": "cuddles", "venus_sign_keyword_adv_1": "sweetly",
    "mars_sign_keyword_adj_1": "playful", "mars_sign_keyword_noun_1": "zest", "mars_sign_keyword_adv_1": "boldly",
    "rising_sign_keyword_adj_1": "observant", "rising_sign_keyword_adj_2": "graceful",
    "north_node_keyword_adj_1": "adventurous", "north_node_keyword_adj_2": "purposeful", "north_node_keyword_noun_1": "growth",
    "south_node_keyword_adj_1": "nostalgic", "south_node_keyword_noun_1": "familiarity", "south_node_keyword_adv_1": "comfortably",
    "keyword_adj_1_for_sun_sign_name": "radiant", "keyword_noun_1_for_sun_sign_name": "vitality", "keyword_adv_1_for_sun_sign_name": "brightly",
    "keyword_adj_1_for_moon_sign_name": "sensitive", "keyword_noun_1_for_moon_sign_name": "comfort", "keyword_adv_1_for_moon_sign_name": "softly",
    "keyword_adj_1_for_mercury_sign_name": "quick-witted", "keyword_noun_1_for_mercury_sign_name": "chatter", "keyword_adv_1_for_mercury_sign_name": "nimbly",
    "keyword_adj_1_for_rising_sign_name": "observant", "keyword_adj_2_for_rising_sign_name": "graceful",
    "keyword_noun_1_for_venus_sign_name": "cuddles", "keyword_adj_1_for_venus_sign_name": "charming", "keyword_adv_1_for_venus_sign_name": "sweetly",
    "keyword_adj_1_for_mars_sign_name": "playful", "keyword_noun_1_for_mars_sign_name": "zest", "keyword_adv_1_for_mars_sign_name": "boldly",
    "keyword_adj_1_for_north_node_sign_name": "adventurous", "keyword_adj_2_for_north_node_sign_name": "purposeful", "keyword_noun_1_for_north_node_sign_name": "growth",
    "keyword_adj_1_for_south_node_sign_name": "nostalgic",

    # Dominant Sign Keywords
    "keyword_trait_for_sign1_dominant": "protective and leading",
    "dominant_sign_1_keyword_trait": "brave and bold",
    "dominant_sign_1_short_behavioral_phrase": "confidently exploring new territories",
    "dominant_sign_1_signature_feeling": "a sense of regal self-assurance",
    "dominant_sign_2_keyword_trait": "gentle and observant",
    "dominant_sign_2_contextual_behavior": "when feeling safe and cozy",
    "short_behavioral_phrase_sign1_dominant": "leading the pack with confidence",
    "signature_feeling_sign1_dominant": "feeling confident and regal",
    "keyword_trait_for_sign2_dominant": "nurturing and caring",
    "contextual_behavior_sign2_dominant": "when feeling secure and loved",

    # Breed Specifics 
    "common_positive_breed_trait_1": "unwavering loyalty and abundant warmth",
    "common_positive_breed_trait_2": "a charming quirkiness that melts hearts",
    "typical_breed_behavior_1": "being their wonderful, breed-typical selves",
    "sun_sign_trait_contrasting_or_enhancing": "an extra dash of sunny sparkle to their nature",
    "rising_sign_trait_flavor": "a unique and captivating way of greeting the world",
    "common_breed_temperament": "generally lovely and well-dispositioned",
    "breed_instinct_example": "following their natural nose on exciting adventures",
    "breed_o_scope_common_positive_trait_1": "being incredibly smart and playful", 
    "breed_o_scope_typical_behavior_1": "expertly lounging in sunbeams",
    "breed_o_scope_sun_sign_contrast_enhance": "a surprising burst of energetic zoomies",
    "breed_o_scope_rising_sign_flavor": "a touch more cautious than expected, observing before engaging",
    "breed_o_scope_common_temperament": "wonderfully easygoing",
    "breed_o_scope_instinct_example": "instinctively chasing anything that moves",
    "breed_o_scope_example_1": "suddenly performing a playful pounce during a serious nap",
    "breed_o_scope_example_2": "offering a gentle head-nuzzle, contradicting their 'tough' appearance",
    "breed_o_scope_example_3": "meticulously arranging their toys before playing",
    "breed_behavior_keywords": "their wonderfully unique species-specific behaviors and instincts", 

    # Care & Interaction
    "rising_sign_expression_style": "an open and welcoming heart",
    "rising_sign_social_tip": "letting them approach new friends and situations at their own pace",
    "elemental_care_style": "engaging in activities that perfectly match their innate energy",
    "sun_sign_self_image_nurture_style": "celebrating their core spirit and unique talents daily",
    "companion_care_moon_emotional_need": "a soft blanket and gentle whispers",
    "companion_care_rising_expression_style": "a burst of joyful energy",
    "companion_care_rising_social_tip": "allow them to sniff everything first",
    "companion_care_elemental_style_care": "plenty of outdoor adventures for their fiery spirit",
    "companion_care_sun_self_image_nurture": "praising their unique quirks and funny habits",
    "companion_care_example_1": "thriving on a predictable daily routine",
    "companion_care_example_2": "responding best to calm, reassuring tones",
    "companion_care_example_3": "getting a mischievous twinkle in their eye when learning new tricks",

    # Example Behaviors 
    "sun_sign_example_1": "basking in a sunbeam like true royalty", "sun_sign_example_2": "leading the charge on walks with joyful barks", "sun_sign_example_3": "offering a comforting head-nuzzle when you need it most",
    "moon_sign_example_1": "seeking out the coziest, most hidden nap spot", "moon_sign_example_2": "knowing just when you need a gentle paw or a soft purr", "moon_sign_example_3": "having a specific 'safe' toy they carry everywhere",
    "mercury_sign_example_1": "learning new tricks with surprising speed (if treats are involved!)", "mercury_sign_example_2": "communicating displeasure with a very dramatic sigh", "mercury_sign_example_3": "cleverly figuring out how to open the cupboard where snacks are kept",
    "venus_sign_example_1": "gently nudging your hand for more pets", "venus_sign_example_2": "bringing you their favorite toy as a sign of affection", "venus_sign_example_3": "giving slow, loving blinks from across the room",
    "mars_sign_example_1": "engaging in enthusiastic (and sometimes clumsy) play-fighting", "mars_sign_example_2": "stubbornly refusing to move from their comfy spot on the sofa", "mars_sign_example_3": "getting a sudden burst of zoomies around the house",
    "rising_sign_example_1": "boldly and curiously greeting new friends at the door", "rising_sign_example_2": "cautiously observing new situations from a safe distance before engaging", "rising_sign_example_3": "charming everyone they meet with an irresistible tail wag or happy chirp",
    "north_node_example_1": "tentatively exploring a new toy with great curiosity", "north_node_example_2": "showing surprising bravery in a new or unfamiliar situation", "north_node_example_3": "learning a new trick or command with surprising enthusiasm",
    "chiron_example_1": "always seeming to know when someone in the family is feeling down and offering comfort", "chiron_example_2": "being particularly gentle with younger or more vulnerable members of the household", "chiron_example_3": "having a favorite quiet spot where they go to recharge their gentle spirit",
    "lilith_example_1": "giving a very distinct 'leave me alone' look when they're not in the mood for interaction", "lilith_example_2": "having a specific toy or spot that is THEIRS and no one else's", "lilith_example_3": "sometimes preferring their own company, observing the world with a mysterious gaze",
    "south_node_example_1": "retreating to their favorite old blanket for ultimate comfort", "south_node_example_2": "repeating a tried-and-true cute antic that always gets a smile", "south_node_example_3": "instinctively knowing the best way to beg for treats with those puppy-dog eyes",
    "element_modality_example_1": "initiating playtime with gusto and unwavering determination", "element_modality_example_2": "stubbornly insisting on their favorite nap spot, unmoved by pleas", "element_modality_example_3": "curiously investigating every new sound with adaptable focus",
    "dominant_combo_example_1": "strutting their stuff like the star they are, then meticulously cleaning a paw", "dominant_combo_example_2": "boldly exploring a new room, then carefully considering the best nap spot", "dominant_combo_example_3": "demanding cuddles with authority, then melting into a puddle of purrs",
    "element_balance_example_dominant_fire": "chasing sunbeams across the floor with fiery enthusiasm", "element_balance_example_earth_low_air": "preferring familiar comforts and routines over newfangled ideas or toys", "element_balance_example_mixed_low_water": "offering a toy when you're sad, their own practical way of showing they care",
    "snack_snooze_example_fire": "needing a good zoomie session before they can even think about settling down for a nap", "snack_snooze_example_earth": "having very particular opinions about where their food bowl should be and when dinner is served", "snack_snooze_example_water": "only napping soundly if they're curled up in their favorite human's lap or a very secure den",
    "Example 1 for Sun sign": "basking in a sunbeam like true royalty", "Example 2 for Sun sign": "leading the charge on walks", "Example 3 for Sun sign": "offering a comforting head-nuzzle",
    "Example 1 for Moon sign": "seeking out the coziest nap spot", "Example 2 for Moon sign": "knowing when you need comfort", "Example 3 for Moon sign": "having a 'safe' toy",
    "Example 1 for Rising Sign": "boldly greeting new friends", "Example 2 for Rising Sign": "cautiously observing", "Example 3 for Rising Sign": "charming everyone",
    "Example 1 for North Node": "exploring a new toy", "Example 2 for North Node": "showing bravery", "Example 3 for North Node": "learning a new trick",
    "Example 1 for South Node": "retreating to an old blanket", "Example 2 for South Node": "repeating a cute antic", "Example 3 for South Node": "knowing how to beg",
    "Example 1 showcasing element + modality": "initiating playtime with determination", "Example 2 showcasing element + modality": "stubbornly insisting on a nap spot", "Example 3 showcasing element + modality": "curiously investigating sounds",
    "Example 1 for dominant Fire": "chasing sunbeams with enthusiasm",
    "Example 1": "behaving in their uniquely charming way", "Example 2": "showing off their adorable quirks", "Example 3": "surprising you with their cleverness",
    "Example 1 for dominant sign 1 or combo": "strutting their stuff like the star they are", "Example 2 for dominant sign 1 or combo": "meticulously arranging their favorite things", "Example 3 showing dominant energies, perhaps in a funny contrast if two are present": "boldly exploring then carefully considering",
    "Example 2 for Earth + low Air": "preferring familiar comforts over newfangled ideas", "Example 3 involving mixed or low Water": "offering a toy when you're sad, their own way of caring",
    "Example 2 for Earth dominant": "demanding dinner at the exact same time, every single day", "Example 3 for Water dominant": "hiding under the bed during a thunderstorm",
    "species_examples": "    - Displaying their wonderfully unique and cosmic personality traits.", 

    # Soul Archetype Nicknames
    "sun_sign_soul_archetype_nickname": "Your Little Superstar", "moon_sign_soul_archetype_nickname": "Your Comfort Captain", "mercury_sign_soul_archetype_nickname": "Your Clever Companion", "venus_sign_soul_archetype_nickname": "Your Love Bug", "mars_sign_soul_archetype_nickname": "Your Playful Pow-erhouse", "rising_sign_soul_archetype_nickname": "Your Charming Ambassador", "north_node_soul_archetype_nickname": "Your Adventure Seeker", "chiron_soul_archetype_nickname": "Your Gentle Healer", "lilith_soul_archetype_nickname": "Your Wild Spirit", "south_node_soul_archetype_nickname": "Your Familiar Friend", "element_modality_soul_archetype_nickname": "Your Unique Spark", "aspects_soul_archetype_nickname": "Your Cosmic Character", "dominant_combo_soul_archetype_nickname": "Your Star Player", "fixed_stars_soul_archetype_nickname": "Your Celestial Sparkler", "element_balance_soul_archetype_nickname": "Your Elemental Blend", "karmic_lessons_soul_archetype_nickname": "Your Soulful Student", "snack_snooze_soul_archetype_nickname": "Your Comfort Connoisseur", "breed_o_scope_soul_archetype_nickname": "Your One-of-a-Kind Mix", 
    "companion_care_soul_archetype_nickname": "Your Cosmic Co-Pilot",

    # Fallbacks for prompt-specific placeholders
    "sun_sign_activity_suggestion": "a super-fast zoomie session in the yard or a new puzzle toy",
    "moon_sign_comfort_activity_suggestion": "an extra-soft old sweater of yours to snuggle with or some quiet grooming time",
    "mercury_sign_analogy": "the one who tries to hold a full conversation using only eyebrow wiggles and dramatic tail thumps",
    "venus_sign_analogy": "the one who believes the best way to show love is by aggressively demanding belly rubs, right now",
    "mars_sign_analogy": "the one who views the vacuum cleaner as a mortal enemy to be vanquished daily",
    "rising_sign_analogy": "the one who greets every visitor like a long-lost friend, possibly with overwhelming enthusiasm",
    "element_modality_style_explanation": "all about action, enthusiasm, and those spectacular zoomies - think of them as a little sparkler!",
    "element_modality_approach_explanation": "be an initiator, the one who says 'Hey, let's investigate that rustling leaf NOW!'",
    "element_modality_combined_vibe_example": "a Fiery Cardinal go-getter who launches into playtime with gusto",
    "element_modality_short_dominant_element_behavior_example": "fiery zoomie-powered",
    "element_modality_short_dominant_modality_behavior_example": "decisive 'let's go now'",

    "Insert analogy": "behaving in their uniquely charming and intelligent way",
    "Insert a fun, relatable analogy for Rising Sign in that sign - e.g., for Aries Rising": "making their grand entrance in a style that's all their own",
    "Suggest a simple, sign-appropriate activity": "a delightful game or a favorite pastime they adore",
    "Suggest a simple, sign-appropriate comfort item/activity": "their most cherished comforting ritual or a special treat",

    # Fallbacks for new pronoun placeholders 
    "he_she": "they", "his_her": "their", "him_her": "them",
}


# --- Script Configuration & Path Definitions ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')
DEFAULT_FONTS_DIR = os.path.join(DEFAULT_ASSETS_DIR, 'fonts') # Corrected: fonts dir inside assets
DEFAULT_DATA_JSONS_DIR = os.path.join(project_root, 'common', 'Data jsons')
REPORTS_OUTPUT_BASE_DIR = os.path.join(project_root, 'astro_reports_output')


# --- Define Ephemeris Path ---
EPHEMERIS_PATH = r"C:\Users\danie\OneDrive\swisseph"
if not os.path.isdir(EPHEMERIS_PATH):
    print(f"WARNING: The Ephemeris path wasn't found here: {EPHEMERIS_PATH}")
    EPHEMERIS_PATH = None
else:
    print(f"Using Ephemeris Path: {EPHEMERIS_PATH}")

# --- OpenAI Client Setup ---
openai_client = None
AI_MODEL = "gpt-4o-mini" 
AI_TEMPERATURE = 0.7 

if OpenAI:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Cannot initialize OpenAI client.")
        openai_client = OpenAI(api_key=api_key)
        print(f"OpenAI client initialized.")
        AI_MODEL = os.getenv("AI_MODEL", AI_MODEL)
        try:
            AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", str(AI_TEMPERATURE)))
        except ValueError:
            print(f"Warning: Invalid AI_TEMPERATURE env var '{os.getenv('AI_TEMPERATURE')}'. Using default: {AI_TEMPERATURE}")
        print(f"Using AI Model: {AI_MODEL}, Temperature: {AI_TEMPERATURE}")
    except ValueError as e:
        print(f"WARNING: OpenAI configuration error: {e}. AI calls will be skipped if not in test mode and AI mode is on.")
        openai_client = None
    except Exception as e: 
        print(f"WARNING: Could not initialize OpenAI client: {type(e).__name__} - {e}. AI calls will be skipped if not in test mode and AI mode is on.")
        openai_client = None
else:
    print("WARNING: OpenAI library not found or failed to import. AI calls will be skipped if not in test mode and AI mode is on.")

# --- Global placeholder for chart data, accessible by content generation functions ---
calculated_chart_data_global = {}

# --- Define sound per species ---
PET_SOUNDS = {
    "cat": "Mew", "dog": "Woof", "horse": "Neigh", "bird": "Chirp", "rabbit": "Thump",
    "hamster": "Squeak", "lizard": "Hiss", "turtle": "Shuffle", "default": "Pawstep"
}

# --- OpenAI API Call Function ---
def call_openai_updated(ssml_prompt, client_name, section_key, max_tokens=1000):
    if not openai_client:
        logger.warning(f"OpenAI client not initialized. Skipping AI call for section {section_key}.")
        return f"[AI Call Skipped - OpenAI Client Not Initialized for section {section_key}]"
    logger.info(f"Calling OpenAI for {client_name} - {section_key} (Model: {AI_MODEL}, Temp: {AI_TEMPERATURE})...")
    try:
        response = openai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are Mika, a playful, insightful, and heartwarming pet astrology oracle. You speak directly to the pet's guardian about their beloved companion, using clear, engaging language suitable for a cherished keepsake report."},
                {"role": "user", "content": ssml_prompt}
            ],
            max_tokens=max_tokens,
            temperature=AI_TEMPERATURE
        )
        if response.choices and response.choices[0].message and response.choices[0].message.content:
             raw_ai_content = response.choices[0].message.content.strip()
             # PATCH 19: Ensure _clean_mika_voice (with updated regex) is applied here.
             cleaned_ai_content = _clean_mika_voice(raw_ai_content)
             return cleaned_ai_content
        else:
            logger.warning(f"OpenAI response structure unexpected or content empty for section {section_key}.")
            return f"[AI Response Empty or Malformed for section {section_key}]"
    except Exception as e:
        logger.error(f"OpenAI API call failed for section {section_key}: {type(e).__name__} - {e}")
        return f"[OpenAI Call Error for section {section_key} - Type: {type(e).__name__}, Details: {str(e)}]"

# --- Dedicated Context Preparation for Pet Report ---
def _prepare_pet_prompt_context(
    section_key: str, chart_data: dict, pet_name: str, pet_species: str, 
    pet_breed: str, 
    pet_sound: str, birth_date: str,
    birth_time: str,
    skip_fixed_stars: bool = False,
    pronoun_mode: str = "name" 
):
    context_for_formatting = {'pet_name': pet_name, 'client_name': pet_name, 'species': pet_species,
                              'breed': pet_breed if pet_breed else "a unique and special friend",
                              'pet_sound': pet_sound,
                              'birth_date': birth_date,
                              'birth_time': birth_time,
                              'skip_fixed_stars': skip_fixed_stars,
                              'pronoun_mode': pronoun_mode} 
    
    breed_input_for_patch = pet_breed
    breed_raw_for_pet_breed_placeholder = breed_input_for_patch.strip() if isinstance(breed_input_for_patch, str) else ""

    if not breed_raw_for_pet_breed_placeholder or breed_raw_for_pet_breed_placeholder.lower() in ["unknown", "mixed", "none", ""]:
        context_for_formatting["pet_breed"] = "a unique soul"
    else:
        context_for_formatting["pet_breed"] = breed_raw_for_pet_breed_placeholder

    if chart_data and isinstance(chart_data, dict):
        context_for_formatting["species"] = chart_data.get("species", context_for_formatting.get("species"))

    if not context_for_formatting.get("species"):
        context_for_formatting["species"] = "mystical being"
    
    formatted_birth_date_str = BASE_PLACEHOLDER_FALLBACKS_PET['birth_date_formatted']
    if birth_date and isinstance(birth_date, str):
        try:
            date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
            formatted_birth_date_str = date_obj.strftime("%A, %B %d, %Y")
        except ValueError:
            logger.warning(f"Could not parse birth_date string '{birth_date}' for formatting. Using fallback.")
            if chart_data and chart_data.get('birth_details'):
                bd = chart_data['birth_details']
                day_of_week = bd.get('day_of_week', '')
                month_name = bd.get('month_name', '')
                day_num = bd.get('day', '')
                year_num = bd.get('year', '')
                if all([day_of_week, month_name, day_num, year_num]):
                    formatted_birth_date_str = f"{day_of_week}, {month_name} {day_num}, {year_num}"
                else:
                    formatted_birth_date_str = BASE_PLACEHOLDER_FALLBACKS_PET['birth_date_formatted']
            else:
                formatted_birth_date_str = BASE_PLACEHOLDER_FALLBACKS_PET['birth_date_formatted']
        except Exception as e:
            logger.error(f"Unexpected error formatting birth_date '{birth_date}': {e}. Using fallback.")
            formatted_birth_date_str = BASE_PLACEHOLDER_FALLBACKS_PET['birth_date_formatted']
    context_for_formatting['birth_date_formatted'] = formatted_birth_date_str
    
    for key, fallback_value in BASE_PLACEHOLDER_FALLBACKS_PET.items():
        context_for_formatting.setdefault(key, fallback_value)

    if chart_data and isinstance(chart_data, dict):
        context_for_formatting["species"] = chart_data.get("species", context_for_formatting["species"])
        context_for_formatting["species_plural"] = context_for_formatting["species"] + "s" if context_for_formatting["species"] and isinstance(context_for_formatting["species"], str) else "companions"

        retrieved_breed_name_from_chart = chart_data.get("breed_name", None)
        final_breed_name = retrieved_breed_name_from_chart if retrieved_breed_name_from_chart and retrieved_breed_name_from_chart.strip() else pet_breed

        context_for_formatting["breed_name"] = final_breed_name if final_breed_name and final_breed_name.strip() else BASE_PLACEHOLDER_FALLBACKS_PET["breed_name"]

        if not context_for_formatting["breed_name"] or context_for_formatting["breed_name"].lower() in ["none", "unknown", "mixed", ""]:
            context_for_formatting["breed_lowercase_article_noun_phrase"] = f"a {context_for_formatting['species']}" if context_for_formatting['species'] else "a unique friend"
            context_for_formatting["breed"] = BASE_PLACEHOLDER_FALLBACKS_PET["breed"]
            context_for_formatting["breed_name"] = BASE_PLACEHOLDER_FALLBACKS_PET["breed_name"]
        else:
            context_for_formatting["breed_lowercase_article_noun_phrase"] = f"a {context_for_formatting['breed_name'].lower()}"
            context_for_formatting["breed"] = context_for_formatting['breed_name']


        positions = chart_data.get('positions', {})
        angles = chart_data.get('angles', {})
        planet_to_context_map = {
            'Sun': 'sun_sign_name', 'Moon': 'moon_sign_name', 'Mercury': 'mercury_sign_name',
            'Venus': 'venus_sign_name', 'Mars': 'mars_sign_name', 'Jupiter': 'jupiter_sign_name',
            'Saturn': 'saturn_sign_name', 'Uranus': 'uranus_sign_name', 'Neptune': 'neptune_sign_name',
            'Pluto': 'pluto_sign_name', 'Chiron': 'chiron_sign_name',
            'Black Moon Lilith': 'black_moon_lilith_sign_name',
            'North Node': 'north_node_sign_name',
            'South Node': 'south_node_sign_name'
        }

        for chart_planet_key, context_sign_key in planet_to_context_map.items():
            sign_val = positions.get(chart_planet_key, {}).get('sign')
            if isinstance(sign_val, str) and ("Error" in sign_val or "Exception" in sign_val or not sign_val.strip()):
                fallback_sign_name = BASE_PLACEHOLDER_FALLBACKS_PET.get(context_sign_key, "a mystical sign")
                context_for_formatting[context_sign_key] = fallback_sign_name
                logger.info(f"Sign Error Fallback: '{context_sign_key}' for '{chart_planet_key}' was error ('{sign_val}'), used base fallback '{fallback_sign_name}'.")
            elif sign_val:
                context_for_formatting[context_sign_key] = sign_val

        if 'north_node_sign_name' in context_for_formatting:
            context_for_formatting['north_node_sign'] = context_for_formatting['north_node_sign_name']

        asc_sign_val = angles.get('Ascendant', {}).get('sign')
        if isinstance(asc_sign_val, str) and ("Error" in asc_sign_val or "Exception" in asc_sign_val or not asc_sign_val.strip()):
            fallback_asc_sign_name = BASE_PLACEHOLDER_FALLBACKS_PET.get('rising_sign_name', "a captivating aura")
            context_for_formatting['rising_sign_name'] = fallback_asc_sign_name
            logger.info(f"Sign Error Fallback: 'rising_sign_name' for Ascendant was error ('{asc_sign_val}'), used base fallback '{fallback_asc_sign_name}'.")
        elif asc_sign_val:
            context_for_formatting['rising_sign_name'] = asc_sign_val

        chart_signatures = chart_data.get('chart_signatures', {})
        element_balance_percentages = chart_data.get('elemental_balance', {})

        prompt_dom_elem_1 = chart_signatures.get('prompt_dominant_element_1', BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_1'])
        prompt_dom_elem_2 = chart_signatures.get('prompt_dominant_element_2', BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2'])

        if prompt_dom_elem_1 and prompt_dom_elem_1 != BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_1'] and \
           (prompt_dom_elem_2 == prompt_dom_elem_1 or prompt_dom_elem_2 == "None" or prompt_dom_elem_2 == BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2']):
            if element_balance_percentages:
                sorted_elements = sorted(
                    [(el, pct) for el, pct in element_balance_percentages.items() if el != prompt_dom_elem_1 and el != "None" and el != "Error"],
                    key=lambda item: item[1],
                    reverse=True
                )
                if sorted_elements:
                    prompt_dom_elem_2 = sorted_elements[0][0]
                else:
                    prompt_dom_elem_2 = "a subtle influence"
            else:
                 prompt_dom_elem_2 = "a subtle influence" if prompt_dom_elem_1 else BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2']

        prompt_least_elem = chart_signatures.get('prompt_least_represented_element', BASE_PLACEHOLDER_FALLBACKS_PET['least_represented_element'])

        element_properties_map = {
            "Fire": "passionate and energetic", "Earth": "grounded and practical",
            "Air": "curious and communicative", "Water": "sensitive and intuitive",
            "Error": "a unique cosmic signature", "None": "a subtle energetic influence",
            "perfectly balanced": "perfectly balanced",
            "other elements less emphasized": "other elements being less emphasized but still part of their charm",
            "a subtle influence": "a subtle influence"
        }

        context_for_formatting['dominant_element_1'] = prompt_dom_elem_1 if prompt_dom_elem_1 and prompt_dom_elem_1 != "None" else BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_1']
        context_for_formatting['dominant_element_2'] = prompt_dom_elem_2 if prompt_dom_elem_2 and prompt_dom_elem_2 != "None" else BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2']
        context_for_formatting['least_represented_element'] = prompt_least_elem if prompt_least_elem and prompt_least_elem != "None" else BASE_PLACEHOLDER_FALLBACKS_PET['least_represented_element']

        desc1_trait = element_properties_map.get(context_for_formatting['dominant_element_1'], "a primary energetic force")
        if context_for_formatting['dominant_element_2'] == context_for_formatting['dominant_element_1'] or \
           context_for_formatting['dominant_element_2'] in ["None", "a subtle influence", BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2']]:
            desc2_trait = "a subtle secondary energetic influence" if context_for_formatting['dominant_element_1'] else element_properties_map.get(BASE_PLACEHOLDER_FALLBACKS_PET['dominant_element_2'])
        else:
            desc2_trait = element_properties_map.get(context_for_formatting['dominant_element_2'], "a secondary energetic influence")

        context_for_formatting['element_1_description'] = f"a style that’s {desc1_trait}"
        context_for_formatting['element_2_description'] = f"hints of {desc2_trait}"

        context_for_formatting['dominant_element'] = chart_signatures.get('dominant_element', context_for_formatting['dominant_element'])
        context_for_formatting['dominant_modality'] = chart_signatures.get('dominant_modality', context_for_formatting['dominant_modality'])

        for el_name_cap in ["Fire", "Earth", "Air", "Water"]:
            el_name_lower = el_name_cap.lower()
            context_for_formatting[f"{el_name_lower}_percentage"] = element_balance_percentages.get(el_name_cap, 0.0)

        elem1_name = context_for_formatting['dominant_element_1']
        elem2_name = context_for_formatting['dominant_element_2']
        elem1_pct = element_balance_percentages.get(elem1_name, 0.0)
        elem2_pct = element_balance_percentages.get(elem2_name, 0.0)

        element_dominance_phrase = BASE_PLACEHOLDER_FALLBACKS_PET['element_dominance_style_phrase']

        if elem1_name != "None" and elem1_name != "Error":
            if elem2_name != "None" and elem2_name != "Error" and elem2_name != elem1_name:
                if abs(elem1_pct - elem2_pct) <= 1.5:
                    element_dominance_phrase = f"an equal blend of {elem1_name} and {elem2_name}"
                elif elem1_pct > elem2_pct:
                    element_dominance_phrase = f"mostly {elem1_name}, with {elem2_name.lower()} as a notable secondary influence"
                else:
                    element_dominance_phrase = f"mostly {elem2_name}, with {elem1_name.lower()} as a notable secondary influence"
            else:
                element_dominance_phrase = f"predominantly {elem1_name}"
        elif elem2_name != "None" and elem2_name != "Error":
             element_dominance_phrase = f"predominantly {elem2_name}"

        context_for_formatting['element_dominance_style_phrase'] = element_dominance_phrase
        logger.info(f"Calculated element_dominance_style_phrase: '{element_dominance_phrase}' "
                    f"(Elem1: {elem1_name}@{elem1_pct}%, Elem2: {elem2_name}@{elem2_pct}%)")


        if not skip_fixed_stars:
            fixed_stars_details = chart_data.get('fixed_star_links', [])
            if fixed_stars_details and len(fixed_stars_details) > 0:
                star1_match_info = fixed_stars_details[0]
                context_for_formatting.update({
                    'fixed_star_1_name': star1_match_info.get('star', context_for_formatting['fixed_star_1_name']),
                    'planet_or_point_fixed_star_1': f"{star1_match_info.get('linked_planet', 'Their astrological point')} conjunct {star1_match_info.get('star', 'a notable star')}",
                    'fixed_star_1_traits': star1_match_info.get('star_info', {}).get('keywords', ["unique stellar traits"])[0] if star1_match_info.get('star_info', {}).get('keywords') else context_for_formatting['fixed_star_1_traits'],
                    'fixed_star_1_brief_behavior_example': star1_match_info.get('star_info', {}).get('brief_interpretation', context_for_formatting['fixed_star_1_brief_behavior_example']),
                })

                raw_template_for_star2 = ""
                for p_def in PROMPTS: 
                    if p_def.get("section_id") == "fixed_stars":
                        raw_template_for_star2 = p_def.get("ai_prompt_parts", {}).get("optional_fixed_star_2_prompt_text", "")
                        break

                if len(fixed_stars_details) > 1 and raw_template_for_star2:
                    star2_match_info = fixed_stars_details[1]
                    context_for_formatting.update({
                        'fixed_star_2_name': star2_match_info.get('star', context_for_formatting['fixed_star_2_name']),
                        'planet_or_point_fixed_star_2': f"{star2_match_info.get('linked_planet', 'Their astrological point')} conjunct {star2_match_info.get('star', 'another star')}",
                        'fixed_star_2_traits': star2_match_info.get('star_info', {}).get('keywords', ["other stellar qualities"])[0] if star2_match_info.get('star_info', {}).get('keywords') else context_for_formatting['fixed_star_2_traits'],
                        'fixed_star_2_brief_behavior_example': star2_match_info.get('star_info', {}).get('brief_interpretation', context_for_formatting['fixed_star_2_brief_behavior_example']),
                    })
                    context_for_formatting['optional_fixed_star_2_prompt_text'] = clean_template_string_for_formatting(raw_template_for_star2)
                else:
                    context_for_formatting['optional_fixed_star_2_prompt_text'] = ""
            else: 
                context_for_formatting['optional_fixed_star_2_prompt_text'] = ""
        else: 
            context_for_formatting['optional_fixed_star_2_prompt_text'] = ""
            context_for_formatting['fixed_star_1_name'] = ""
            context_for_formatting['planet_or_point_fixed_star_1'] = ""
            context_for_formatting['fixed_star_1_traits'] = ""
            context_for_formatting['fixed_star_1_brief_behavior_example'] = ""
            context_for_formatting['fixed_star_2_name'] = ""
            context_for_formatting['planet_or_point_fixed_star_2'] = ""
            context_for_formatting['fixed_star_2_traits'] = ""
            context_for_formatting['fixed_star_2_brief_behavior_example'] = ""

        birth_details_from_chart = chart_data.get('birth_details', {})
        if 'chart_ruler' in birth_details_from_chart:
            context_for_formatting['chart_ruler'] = birth_details_from_chart['chart_ruler']

        context_for_formatting['dominant_sign_1'] = chart_signatures.get('dominant_sign_1', context_for_formatting['dominant_sign_1'])
        context_for_formatting['dominant_sign_2'] = chart_signatures.get('dominant_sign_2', context_for_formatting['dominant_sign_2'])

    else: 
        logger.warning(f"Chart data missing or invalid for section '{section_key}', relying heavily on fallbacks.")

    species_specific_behavior_cues = {
        "dog": "loyal companionship, tail wags, sniff adventures, squirrel chasing, ball fetching",
        "cat": "silent pouncing, sunbeam naps, independent curiosity, windowsill watching",
        "bird": "chirpy greetings, mirror fascination, sky-gazing",
        "fallback": "unique quirks and cosmic instincts"
    }
    species_key_for_cues = context_for_formatting.get("species", "fallback").lower() if isinstance(context_for_formatting.get("species"), str) else "fallback"
    context_for_formatting["breed_behavior_keywords"] = species_specific_behavior_cues.get(
        species_key_for_cues, species_specific_behavior_cues["fallback"]
    )
    
    try:
        species_for_examples = context_for_formatting.get("species", "default")
        examples_text = get_species_example_block(species_for_examples, section_key) 
        context_for_formatting["species_examples"] = examples_text
    except Exception as e_species_ex:
        logger.error(f"Failed to get species-specific examples for section '{section_key}', species '{context_for_formatting.get('species', 'unknown')}': {e_species_ex}")
        context_for_formatting["species_examples"] = "    - Displaying their wonderfully unique and cosmic personality traits." 
    
    all_expected_keys_for_fallback_check = CLEANED_PLACEHOLDER_KEYS.copy()
    pronoun_placeholders_to_exclude = {"he_she", "his_her", "him_her"}
    keys_for_standard_fallback = all_expected_keys_for_fallback_check - pronoun_placeholders_to_exclude

    for key in keys_for_standard_fallback:
        if key not in context_for_formatting:
            species_name_for_fallback = context_for_formatting.get('species', 'pet')
            pet_name_for_fallback = context_for_formatting.get('pet_name', 'Your Pet')

            fallback_value = f"the unique essence of {pet_name_for_fallback}'s {key.replace('_', ' ')}"
            if "sign_name" in key: fallback_value = "CosmicSign"
            elif "keyword_adj" in key: fallback_value = "wonderfully unique"
            elif "keyword_noun" in key: fallback_value = "charming quirk"
            elif "keyword_adv" in key: fallback_value = "adorably"
            elif "example" in key or key.startswith("Example") or key == "species_examples":
                fallback_value = f"your {species_name_for_fallback} showcasing their special personality"
            elif key == "optional_fixed_star_2_prompt_text": fallback_value = "" 
            elif "suggestion" in key or "analogy" in key:
                fallback_value = f"a delightful way {pet_name_for_fallback} expresses their inner self"
            elif key == "pet_breed": fallback_value = "their wonderfully unique nature" 
            elif key == "breed_behavior_keywords": 
                fallback_value = species_specific_behavior_cues.get(
                    context_for_formatting.get("species", "fallback").lower() if isinstance(context_for_formatting.get("species"), str) else "fallback",
                    species_specific_behavior_cues["fallback"]
                )

            context_for_formatting[key] = fallback_value
            logger.info(f"SAFETY NET 2: Injected dynamic fallback for missing key '{key}' in section '{section_key}': '{fallback_value}'")

    return context_for_formatting


# --- Function to get AI sections content ---
def get_ai_sections_content(
    client_name, current_occasion_mode, current_pet_breed, current_pet_species,
    current_birth_date_str, current_birth_time_str, current_pet_sound,
    section_definitions_source, 
    skip_fixed_stars: bool = False,
    pronoun_mode: str = "name" 
):
    processed_sections = []
    global calculated_chart_data_global 

    if not section_definitions_source or not isinstance(section_definitions_source, list):
         logger.error(f"Source prompt definitions not loaded or invalid. Cannot generate content.")
         return []

    for prompt_def in section_definitions_source:
        if not isinstance(prompt_def, dict):
            logger.warning(f"Skipping invalid prompt definition (not a dictionary): {prompt_def}")
            continue

        section_id = prompt_def.get('section_id')

        if section_id == "fixed_stars" and skip_fixed_stars:
            logger.info(f"AI Content Gen: Skipping 'fixed_stars' section (ID: {section_id}) as skip_fixed_stars is True.")
            continue

        header_template_raw = prompt_def.get('header_template', prompt_def.get('header', f"Section {section_id}"))
        header_template = _clean_mika_voice(clean_template_string_for_formatting(str(header_template_raw)))

        ai_prompt_parts_raw = prompt_def.get('ai_prompt_parts', {})
        ai_prompt_parts_cleaned_for_prompt_construction = {}
        if isinstance(ai_prompt_parts_raw, dict):
            def _clean_prompt_parts_recursively(d_raw): 
                cleaned_d = {}
                for k_raw, v_raw in d_raw.items():
                    if isinstance(v_raw, str):
                        temp_cleaned = clean_template_string_for_formatting(v_raw)
                        cleaned_d[k_raw] = _clean_mika_voice(temp_cleaned)
                    elif isinstance(v_raw, dict):
                        cleaned_d[k_raw] = _clean_prompt_parts_recursively(v_raw)
                    elif isinstance(v_raw, list):
                         cleaned_d[k_raw] = [
                             _clean_prompt_parts_recursively(i_raw) if isinstance(i_raw, dict)
                             else (_clean_mika_voice(clean_template_string_for_formatting(i_raw)) if isinstance(i_raw, str) else i_raw)
                             for i_raw in v_raw
                         ]
                    else:
                        cleaned_d[k_raw] = v_raw 
                return cleaned_d
            ai_prompt_parts_cleaned_for_prompt_construction = _clean_prompt_parts_recursively(ai_prompt_parts_raw)

        section_quote_template_raw = prompt_def.get('quote')
        section_quote_template = _clean_mika_voice(clean_template_string_for_formatting(str(section_quote_template_raw))) if section_quote_template_raw else None

        transition_connector_template_raw = prompt_def.get('transition_connector')
        transition_connector_template = _clean_mika_voice(clean_template_string_for_formatting(str(transition_connector_template_raw))) if transition_connector_template_raw else None

        static_content_raw = prompt_def.get('static_content', '')
        static_content_cleaned_template = _clean_mika_voice(clean_template_string_for_formatting(str(static_content_raw))) if static_content_raw else ''


        if not section_id or not header_template: 
            logger.warning(f"Skipping prompt definition with missing 'section_id' or 'header_template' (after cleaning): {prompt_def}")
            continue

        logger.info(f"Processing AI content for: {section_id} - {str(header_template)[:70]}...")

        ai_body_text = ""
        header_text_formatted = str(header_template) 
        quote_text_formatted = str(section_quote_template) if section_quote_template else None
        transition_connector_formatted = str(transition_connector_template) if transition_connector_template else None

        try:
            context_for_formatting = _prepare_pet_prompt_context(
                section_key=section_id, chart_data=calculated_chart_data_global,
                pet_name=client_name, pet_species=current_pet_species, pet_breed=current_pet_breed,
                pet_sound=current_pet_sound, birth_date=current_birth_date_str, birth_time=current_birth_time_str,
                skip_fixed_stars=skip_fixed_stars,
                pronoun_mode=pronoun_mode 
            )

            header_text_formatted = header_template.format(**context_for_formatting)
            if quote_text_formatted:
                quote_text_formatted = quote_text_formatted.format(**context_for_formatting)
            if transition_connector_formatted:
                transition_connector_formatted = transition_connector_formatted.format(**context_for_formatting)

            base_prompt_for_section = ""
            if isinstance(ai_prompt_parts_cleaned_for_prompt_construction, dict) and ai_prompt_parts_cleaned_for_prompt_construction:
                prompt_pieces = []
                def build_prompt_from_cleaned(parts_data):
                    if isinstance(parts_data, str):
                        if parts_data.strip(): prompt_pieces.append(parts_data.strip())
                    elif isinstance(parts_data, dict):
                        for val_item in parts_data.values(): build_prompt_from_cleaned(val_item)
                    elif isinstance(parts_data, list):
                        for item_in_list in parts_data: build_prompt_from_cleaned(item_in_list)
                build_prompt_from_cleaned(ai_prompt_parts_cleaned_for_prompt_construction)
                full_ai_prompt_str_from_cleaned_parts = "\n\n".join(prompt_pieces)

                star2_template_from_context = context_for_formatting.get('optional_fixed_star_2_prompt_text', "")
                cleaned_star2_template = str(star2_template_from_context)
                temp_context_for_main_prompt = context_for_formatting.copy()
                if cleaned_star2_template:
                    temp_context_for_main_prompt['optional_fixed_star_2_prompt_text'] = cleaned_star2_template.format(**context_for_formatting)
                else:
                    temp_context_for_main_prompt['optional_fixed_star_2_prompt_text'] = ""

                base_prompt_for_section = full_ai_prompt_str_from_cleaned_parts.format(**temp_context_for_main_prompt)
            elif static_content_cleaned_template:
                base_prompt_for_section = static_content_cleaned_template.format(**context_for_formatting)

            
            prompt_for_ai_engine = base_prompt_for_section 
            final_base_prompt_for_voice_engine = base_prompt_for_section 

            if current_occasion_mode == "pet_memorial":
                ai_pronoun_guidance_note = ""
                if pronoun_mode == "he":
                    ai_pronoun_guidance_note = f"Use past tense and refer to {client_name} as 'he' or 'him'."
                elif pronoun_mode == "she":
                    ai_pronoun_guidance_note = f"Use past tense and refer to {client_name} as 'she' or 'her'."
                else: 
                    ai_pronoun_guidance_note = f"Use past tense and refer to {client_name} by name. Avoid 'they/their'."
                
                # PATCH 19: This memorial instruction is for the AI. The _clean_mika_voice in call_openai_updated
                # (which now has the comprehensive regex) should remove it if the AI echoes it.
                memorial_instruction_for_ai = (
                    f"(Instruction to AI: This is a loving tribute for {client_name}. {ai_pronoun_guidance_note})\n\n"
                )
                final_base_prompt_for_voice_engine = memorial_instruction_for_ai + base_prompt_for_section
            
            if final_base_prompt_for_voice_engine.strip(): 
                ssml_wrapped_prompt = apply_voice_to_prompt(
                    base_prompt=final_base_prompt_for_voice_engine, 
                    persona=PET_VOICE_PERSONA,
                    species=context_for_formatting.get('species'),
                    client_name=client_name,
                    section_id=section_id,
                    occasion_mode=current_occasion_mode,
                    pronoun_mode=pronoun_mode 
                )
                ai_body_text = call_openai_updated(ssml_wrapped_prompt, client_name, section_id)
            else:
                logger.info(f"No 'ai_prompt_parts' or 'static_content' for section {section_id}. Content will be fallback.")


            if transition_connector_formatted:
                 ai_body_text = (ai_body_text + f"\n\n{transition_connector_formatted}").strip()

            if not ai_body_text.strip():
                 fallback_pet_name = context_for_formatting.get('pet_name', 'Your pet')
                 if current_occasion_mode == "pet_memorial":
                     ai_body_text = f"Reflecting on {fallback_pet_name}'s unique spirit for this aspect of their life brings gentle memories. Their essence was truly special."
                 else:
                     ai_body_text = f"This special glimpse into {fallback_pet_name}'s cosmic story is still unfolding. Their unique charm is undeniable, a true testament to their wonderful spirit!"

                 if transition_connector_formatted:
                     ai_body_text += f"\n\n{transition_connector_formatted}"
                 logger.warning(f"Section {section_id} resulted in empty AI/static content. Injected fallback message.")

            for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                if isinstance(header_text_formatted, str):
                    header_text_formatted = header_text_formatted.replace(placeholder, glyph)
                if isinstance(ai_body_text, str):
                    ai_body_text = ai_body_text.replace(placeholder, glyph)
                if isinstance(quote_text_formatted, str):
                    quote_text_formatted = quote_text_formatted.replace(placeholder, glyph)

            final_quote_for_pdf = quote_text_formatted
            current_divider_tag = prompt_def.get('divider_tag', section_id)
            processed_sections.append({
                'section_id': section_id, 'header': header_text_formatted, 'ai_content': ai_body_text,
                'quote': final_quote_for_pdf, 'meta': prompt_def.get('meta', {}), 'divider_tag': current_divider_tag
            })

        except (KeyError, ValueError) as format_error:
            logger.error(f"Formatting error in section {section_id} (after cleaning templates and preparing context): {type(format_error).__name__} - {format_error}. This indicates a persistent issue.", exc_info=True)
            missing_key_info = str(format_error).strip("'")

            emergency_fallback_context = context_for_formatting
            header_text_fallback = str(header_template_raw).replace("{pet_name}", client_name).replace("{species}",current_pet_species)
            try: header_text_fallback = _clean_mika_voice(header_template).format(**emergency_fallback_context)
            except Exception: pass

            quote_text_fallback = None
            if section_quote_template_raw:
                quote_text_fallback = _clean_mika_voice(str(section_quote_template_raw)).replace("{pet_name}", client_name)
                if section_quote_template:
                    try: quote_text_fallback = section_quote_template.format(**emergency_fallback_context)
                    except Exception: pass

            transition_connector_fallback = ""
            if transition_connector_template_raw:
                transition_connector_fallback = _clean_mika_voice(str(transition_connector_template_raw))
                if transition_connector_template:
                    try: transition_connector_fallback = transition_connector_template.format(**emergency_fallback_context)
                    except Exception: pass

            for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                if isinstance(header_text_fallback, str): header_text_fallback = header_text_fallback.replace(placeholder, glyph)
                if isinstance(quote_text_fallback, str): quote_text_fallback = quote_text_fallback.replace(placeholder, glyph)
                if isinstance(transition_connector_fallback, str): transition_connector_fallback = transition_connector_fallback.replace(placeholder, glyph)

            processed_sections.append({
                'section_id': section_id, 'header': header_text_fallback,
                'ai_content': f"[REPORT GENERATION INFO: Section '{section_id}' uses heartwarming general insights for {client_name} as specific details like '{missing_key_info}' are being uniquely interpreted. Their cosmic story is wonderfully special!]\n\n{transition_connector_fallback}".strip(),
                'quote': quote_text_fallback, 'meta': prompt_def.get('meta', {}),
                'divider_tag': prompt_def.get('divider_tag', section_id)
            })
        except Exception as e_section:
            logger.error(f"Unexpected error processing section {section_id}: {type(e_section).__name__} - {e_section}", exc_info=True)
            header_text_general_error = _clean_mika_voice(str(header_template_raw)).replace("{pet_name}", client_name).replace("{species}", current_pet_species)
            quote_text_general_error = (_clean_mika_voice(str(section_quote_template_raw)).replace("{pet_name}", client_name) if section_quote_template_raw else None)
            transition_connector_general_error = (_clean_mika_voice(str(transition_connector_template_raw)).replace("{pet_name}", client_name) if transition_connector_template_raw else "")

            for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                if isinstance(header_text_general_error, str): header_text_general_error = header_text_general_error.replace(placeholder, glyph)
                if isinstance(quote_text_general_error, str): quote_text_general_error = quote_text_general_error.replace(placeholder, glyph)
                if isinstance(transition_connector_general_error, str): transition_connector_general_error = transition_connector_general_error.replace(placeholder, glyph)

            processed_sections.append({
                'section_id': section_id, 'header': header_text_general_error,
                 'ai_content': f"[ERROR: Failed to process section {section_id}. Your pet's cosmic story is still special, full of wonder and delight!]\n\n{transition_connector_general_error}".strip(),
                 'quote': quote_text_general_error,
                 'meta': prompt_def.get('meta', {}), 'divider_tag': prompt_def.get('divider_tag', section_id)
            })
    return processed_sections

# --- Main Orchestration Function ---
def main(
    name: str = None, species: str = None, breed: str = None,
    birth_date: str = None, birth_time: str = None, city: str = None, country_code: str = None,
    latitude: float = None, longitude: float = None, tz_str: str = None,
    output_dir_param: str = None, utc_offset: float = None, occasion: str = 'pet_default',
    assets_dir: str = DEFAULT_ASSETS_DIR, fonts_dir: str = DEFAULT_FONTS_DIR,
    data_jsons_dir: str = DEFAULT_DATA_JSONS_DIR, chart_image_arg: str = None,
    pet_image_path_param: str = None,
    gender_input: str = None, 
    test_mode: bool = False,
    ai_mode: bool = False,
    skip_fixed_stars: bool = False
):
    log_level = logging.INFO if test_mode else logging.WARNING # Adjusted default based on typical use
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s - %(message)s', force=True)
    logger.info(f"Logging configured to {logging.getLevelName(log_level)}.")

    args_namespace = None
    current_pet_name = name
    current_species = species
    current_breed = breed
    current_birth_date = birth_date
    current_birth_time = birth_time
    current_city = city
    current_country_code = country_code
    current_latitude = latitude
    current_longitude = longitude
    current_tz_str = tz_str
    current_output_dir = output_dir_param
    current_utc_offset = utc_offset
    current_occasion_mode = occasion
    current_assets_dir = assets_dir
    current_fonts_dir = fonts_dir
    current_data_jsons_dir = data_jsons_dir
    current_chart_image_arg = chart_image_arg
    current_pet_image_path_input = pet_image_path_param
    current_gender_input_val = gender_input 
    current_test_mode = test_mode
    current_ai_mode = ai_mode
    current_skip_fixed_stars = skip_fixed_stars

    if __name__ == "__main__":
        print("INFO: Script called directly. Parsing arguments from command line.")
        parser = argparse.ArgumentParser(description="Generate a full pet astrology report PDF.")
        parser.add_argument('--name', required=True, help="Pet name")
        parser.add_argument('--species', required=True, choices=['cat','dog', 'horse', 'bird', 'rabbit', 'hamster', 'lizard', 'turtle', 'other'], help="Pet species")
        parser.add_argument('--breed', default="", help="Pet breed. Optional. Provide empty string if not applicable, e.g. --breed \"\"")
        parser.add_argument('--birth_date', required=True, help="Birth date YYYY-MM-DD")
        parser.add_argument('--birth_time', required=False, default="12:00", help="Birth time HH:MM (24h). Use 'unknown' or omit for 12:00.")
        parser.add_argument('--city', required=True, help="Birth city")
        parser.add_argument('--country_code', required=True, help="Birth country code (e.g., US)")
        parser.add_argument('--latitude', type=float, required=True, help="Latitude")
        parser.add_argument('--longitude', type=float, required=True, help="Longitude")
        parser.add_argument('--tz_str', required=True, help="Timezone string (e.g., America/New_York)")
        parser.add_argument('--output_dir', default=os.path.join(REPORTS_OUTPUT_BASE_DIR, 'pet_reports_pdf'), help="Directory for the final PDF report.")
        parser.add_argument('--utc_offset', type=float, help="UTC offset (e.g., -5.0). Alternative if tz_str is problematic.")
        parser.add_argument('--occasion', default='pet_default', help="Occasion for prompts (influences report tone/content).")
        parser.add_argument('--assets_dir', default=DEFAULT_ASSETS_DIR, help="Path to assets directory.")
        parser.add_argument('--fonts_dir', default=DEFAULT_FONTS_DIR, help="Path to fonts directory.")
        parser.add_argument('--data_jsons_dir', default=DEFAULT_DATA_JSONS_DIR, help="Path to data JSONs directory.")
        parser.add_argument('--chart_image', help="Optional path to a pre-generated chart image file (astrology wheel).")
        parser.add_argument('--pet_image_path', help="Path to an optional pet image for the AI transformed cover.")
        parser.add_argument('--gender', type=str, choices=['male', 'female'], help='Optional: Gender of the pet')
        parser.add_argument("--test-mode", action="store_true", help="Use dummy content and skip OpenAI calls. Overrides --ai_mode for OpenAI calls.")
        parser.add_argument("--ai_mode", action="store_true", default=False, help="Enable AI content generation. If False, or if --test-mode is active, uses fallback/dummy content.")
        parser.add_argument("--skip_fixed_stars", action="store_true", default=False, help="If set, the 'Fixed Stars' section will be omitted from the report.")

        args_namespace = parser.parse_args()
        current_pet_name = args_namespace.name
        current_species = args_namespace.species
        current_breed = args_namespace.breed if args_namespace.breed is not None else ""
        current_birth_date = args_namespace.birth_date
        current_birth_time = args_namespace.birth_time
        if not current_birth_time or current_birth_time.lower() in ("unknown", "n/a"):
            print("⚠️ Birth time unknown or not provided—defaulting to 12:00 (noon).")
            current_birth_time = "12:00"
        current_city = args_namespace.city; current_country_code = args_namespace.country_code
        current_latitude = args_namespace.latitude; current_longitude = args_namespace.longitude
        current_tz_str = args_namespace.tz_str
        current_output_dir = args_namespace.output_dir
        current_utc_offset = args_namespace.utc_offset; current_occasion_mode = args_namespace.occasion
        current_assets_dir = args_namespace.assets_dir; current_fonts_dir = args_namespace.fonts_dir
        current_data_jsons_dir = args_namespace.data_jsons_dir; current_chart_image_arg = args_namespace.chart_image
        current_pet_image_path_input = args_namespace.pet_image_path
        current_gender_input_val = args_namespace.gender 
        current_test_mode = args_namespace.test_mode
        current_ai_mode = args_namespace.ai_mode
        current_skip_fixed_stars = args_namespace.skip_fixed_stars

        new_log_level = logging.DEBUG if current_test_mode else logging.INFO # More verbose for test, info for normal
        if logging.getLogger().getEffectiveLevel() != new_log_level: # Check if re-config is needed
            logging.basicConfig(level=new_log_level, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s - %(message)s', force=True)
            logger.info(f"Logging re-configured to {logging.getLevelName(new_log_level)} based on CLI args.")
    else: 
        if current_birth_time is None or current_birth_time.lower() in ("", "unknown", "n/a"):
            print("⚠️ Birth time unknown or not provided—defaulting to 12:00 (noon).")
            current_birth_time = "12:00"
        if current_output_dir is None:
            current_output_dir = os.path.join(REPORTS_OUTPUT_BASE_DIR, 'pet_reports_pdf')
        
    if not all([current_pet_name, current_species, current_birth_date, current_birth_time, current_city, current_country_code, isinstance(current_latitude, (float, int)), isinstance(current_longitude, (float, int)), current_tz_str, current_output_dir]):
        logger.error("Essential information for the pet report is missing or invalid.")
        if __name__ == "__main__" and args_namespace: print("Please provide all required arguments when running from the command line. Use --help for details.")
        return

    if current_gender_input_val == "male":
        pronoun_mode_to_use = "he"
    elif current_gender_input_val == "female":
        pronoun_mode_to_use = "she"
    else:  
        pronoun_mode_to_use = "name"
    logger.info(f"Pronoun mode set to: '{pronoun_mode_to_use}' based on gender input '{current_gender_input_val}'")


    try:
        os.makedirs(REPORTS_OUTPUT_BASE_DIR, exist_ok=True)
        os.makedirs(current_output_dir, exist_ok=True)
        os.makedirs(current_data_jsons_dir, exist_ok=True)
        os.makedirs(current_assets_dir, exist_ok=True); os.makedirs(os.path.join(current_assets_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(current_assets_dir, "images", "covers"), exist_ok=True)
        os.makedirs(os.path.join(current_assets_dir, "images", "dividers"), exist_ok=True)
        os.makedirs(current_fonts_dir, exist_ok=True)
        # Ensure /tmp exists, as AI pet image feature might use it
        tmp_dir = "/tmp"
        if not os.path.exists(tmp_dir):
            try: 
                os.makedirs(tmp_dir)
                logger.info(f"Created directory: {tmp_dir}")
            except OSError as e_tmp: 
                logger.warning(f"Could not create {tmp_dir} directory: {e_tmp}. Image processing might fail if it relies on this path.")
    except OSError as e:
        logger.error(f"Couldn't create needed folders: {e}"); return

    missing_in_base_fallbacks = sorted(list(CLEANED_PLACEHOLDER_KEYS - set(BASE_PLACEHOLDER_FALLBACKS_PET.keys())))
    if missing_in_base_fallbacks:
        if 'species_examples' not in CLEANED_PLACEHOLDER_KEYS and 'species_examples' in missing_in_base_fallbacks:
             logger.info("NOTE: 'species_examples' is expected from prompt_definitions_pet.py. Ensure it's added there.")
        true_missing_for_warning = [ph for ph in missing_in_base_fallbacks if ph != 'species_examples']
        if true_missing_for_warning:
            pronoun_phs = {"he_she", "his_her", "him_her"}
            true_missing_for_warning_filtered = [ph for ph in true_missing_for_warning if ph not in pronoun_phs]
            if true_missing_for_warning_filtered:
                logger.warning(f"WARNING: {len(true_missing_for_warning_filtered)} placeholders from prompts NOT in BASE_PLACEHOLDER_FALLBACKS_PET: {', '.join(true_missing_for_warning_filtered)}")
    else:
        logger.info("All placeholders from prompts definitions are present in BASE_PLACEHOLDER_FALLBACKS_PET or handled dynamically.")

    print(f"--- Starting Pet Astrology Report for: {current_pet_name} ({current_species}) ---")
    if current_occasion_mode == "pet_memorial":
        print(f"--- PET MEMORIAL MODE for {current_pet_name} (Pronoun Mode: {pronoun_mode_to_use}) ---")
    if current_test_mode: print("--- RUNNING IN TEST MODE (forces dummy/fallback content) ---")
    if current_skip_fixed_stars: print("--- FIXED STARS SECTION: WILL BE SKIPPED ---")
    if current_ai_mode:
        print("--- AI MODE: ON ---")
        if not openai_client and not current_test_mode: print("    WARNING: AI Mode is ON, but OpenAI client is not available. Will use dummy/fallback content.")
    else: print("--- AI MODE: OFF (will use dummy/fallback content) ---")


    pet_sound = PET_SOUNDS.get(current_species.lower(), PET_SOUNDS["default"])
    logger.info(f"Determined pet sound: {pet_sound} for species: {current_species}")

    try:
        birth_datetime_obj = datetime.strptime(f"{current_birth_date} {current_birth_time}", "%Y-%m-%d %H:%M")
        year_val, month_val, day_val = birth_datetime_obj.year, birth_datetime_obj.month, birth_datetime_obj.day
        hour_val, minute_val = birth_datetime_obj.hour, birth_datetime_obj.minute
    except ValueError:
        logger.error(f"Invalid birth date/time format. Use YYYY-MM-DD and HH:MM. Got date: '{current_birth_date}', time: '{current_birth_time}'"); return

    assets_for_pdf_context = {}
    assets_for_pdf_context['custom_pet_image_url'] = None
    
    if current_pet_image_path_input:
        logger.info(f"Pet image path provided: {current_pet_image_path_input}")
        if os.path.exists(current_pet_image_path_input):
            # Ensure /tmp (or a configurable temp dir) exists and is writable
            temp_dir_for_images = "/tmp" # Make this configurable if needed
            os.makedirs(temp_dir_for_images, exist_ok=True)

            temp_uploaded_image_filename = f"{uuid.uuid4()}_{os.path.basename(current_pet_image_path_input)}"
            temp_uploaded_image_path_for_ai = os.path.join(temp_dir_for_images, temp_uploaded_image_filename)
            try:
                with open(current_pet_image_path_input, "rb") as src_file, open(temp_uploaded_image_path_for_ai, "wb") as dst_file:
                    dst_file.write(src_file.read())
                logger.info(f"Copied user-provided pet image to temporary path for AI processing: {temp_uploaded_image_path_for_ai}")

                transformed_image_url = generate_cosmic_pet_image(
                    uploaded_image_path=temp_uploaded_image_path_for_ai,
                    pet_name=current_pet_name,
                    species=current_species,
                    breed=current_breed
                )
                if transformed_image_url:
                    assets_for_pdf_context['custom_pet_image_url'] = transformed_image_url
                    logger.info(f"Custom pet image transformed. URL will be passed to PDF generator: {transformed_image_url}")
                else:
                    logger.warning("Failed to generate transformed pet image. No custom image will be used.")

                try:
                    os.remove(temp_uploaded_image_path_for_ai)
                    logger.info(f"Cleaned up temporary uploaded image from {temp_dir_for_images}: {temp_uploaded_image_path_for_ai}")
                except OSError as e_rem:
                    logger.error(f"Error removing temporary uploaded image {temp_uploaded_image_path_for_ai}: {e_rem}")
            except Exception as e_img_proc:
                logger.error(f"Error processing pet image {current_pet_image_path_input}: {e_img_proc}", exc_info=True)
                if os.path.exists(temp_uploaded_image_path_for_ai):
                    try: os.remove(temp_uploaded_image_path_for_ai)
                    except OSError: pass
        else:
            logger.warning(f"Provided pet image path does not exist: {current_pet_image_path_input}")
    else:
        logger.info("No pet image path provided, skipping custom AI cover image generation.")

    print("\nStep 1: Calculating astrological chart...")
    global calculated_chart_data_global
    calculated_chart_data_global = calculate_pet_chart(
        name=current_pet_name, species=current_species, breed=current_breed,
        birth_date=current_birth_date, birth_time=current_birth_time,
        city=current_city, country_code=current_country_code,
        latitude=current_latitude, longitude=current_longitude,
        tz_str=current_tz_str,
        utc_offset_hours=current_utc_offset,
        ephemeris_path_used=EPHEMERIS_PATH,
    )

    if not isinstance(calculated_chart_data_global, dict) or calculated_chart_data_global.get("error"):
        error_msg = calculated_chart_data_global.get('error', 'Chart calculation failed') if isinstance(calculated_chart_data_global, dict) else "Unknown chart calculation error"
        logger.error(f"{error_msg}"); return
    print("Chart calculation successful!")

    chart_image_path_for_pdf = current_chart_image_arg
    if not chart_image_path_for_pdf:
        positions = calculated_chart_data_global.get("positions")
        if positions:
            print("\nStep 1.5: Generating astrological chart image (wheel)...")
            chart_output_dir = os.path.join(REPORTS_OUTPUT_BASE_DIR, 'chart_images')
            try: os.makedirs(chart_output_dir, exist_ok=True)
            except OSError as e:
                logger.warning(f"Could not create chart image output directory '{chart_output_dir}': {e}. Will attempt to save in main output dir.")
                chart_output_dir = REPORTS_OUTPUT_BASE_DIR # Fallback to main reports output
            safe_pet_name_for_file = "".join(c for c in current_pet_name if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
            chart_filename = f"chart_wheel_{safe_pet_name_for_file}.png"
            chart_output_path = os.path.join(chart_output_dir, chart_filename)
            house_cusps = calculated_chart_data_global.get("house_info", {}).get("cusps")
            try:
                generate_chart_image(positions_data=positions, house_cusps_data=house_cusps, output_file=chart_output_path, style=DEFAULT_CHART_STYLE)
                print(f"Astrology wheel chart image generated successfully: {chart_output_path}")
                chart_image_path_for_pdf = chart_output_path
            except Exception as e_chart_gen:
                logger.error(f"Astrology wheel chart image generation failed: {type(e_chart_gen).__name__} - {e_chart_gen}", exc_info=True)
                chart_image_path_for_pdf = None
        else:
            logger.info("No 'positions' data found in chart calculation. Skipping astrology wheel chart image generation.")
            chart_image_path_for_pdf = None
    else:
        logger.info(f"Using pre-provided astrology wheel chart image path: {chart_image_path_for_pdf}")
    assets_for_pdf_context['chart_image_path'] = chart_image_path_for_pdf

    toc_header_formatting_context = _prepare_pet_prompt_context(
        section_key="TOC_Header_Setup", chart_data=calculated_chart_data_global,
        pet_name=current_pet_name, pet_species=current_species, pet_breed=current_breed,
        pet_sound=pet_sound, birth_date=current_birth_date, birth_time=current_birth_time,
        skip_fixed_stars=current_skip_fixed_stars,
        pronoun_mode=pronoun_mode_to_use 
    )

    placeholder_toc_lines = []
    if SECTIONS_FOR_PET_REPORT and isinstance(SECTIONS_FOR_PET_REPORT, list):
        temp_idx = 0
        # Add Chart Wheel to TOC if it exists, before other sections
        if assets_for_pdf_context.get('chart_image_path') and os.path.exists(str(assets_for_pdf_context.get('chart_image_path'))):
            temp_idx += 1
            placeholder_toc_lines.append(f"{temp_idx}. Your Pet's Cosmic Blueprint (Chart Wheel)")

        for section_def in SECTIONS_FOR_PET_REPORT:
            if section_def.get("section_id") == "fixed_stars" and current_skip_fixed_stars:
                logger.info(f"Placeholder TOC: Skipping 'fixed_stars' section_id: {section_def.get('section_id')} due to skip_fixed_stars=True.")
                continue
            if section_def.get("divider_tag") == "toc" or section_def.get("section_id") == "toc": continue

            raw_label_template = section_def.get("meta", {}).get("section_title") or \
                                 section_def.get("header_template", section_def.get("header", f"Section {section_def.get('section_id', 'Unknown')}"))
            label_template_cleaned_mika = _clean_mika_voice(clean_template_string_for_formatting(str(raw_label_template)))
            temp_idx += 1
            try:
                label = label_template_cleaned_mika.format(**toc_header_formatting_context)
            except (KeyError, ValueError) as e:
                logger.warning(f"Formatting TOC label for '{section_def.get('section_id', 'Unknown Section')}' ('{label_template_cleaned_mika}') failed. Error: {e}. Using fallback.")
                safe_context_on_error = toc_header_formatting_context.copy()
                if isinstance(e, KeyError):
                    missing_key_str = str(e).strip("'")
                    safe_context_on_error.setdefault(missing_key_str, f"[{missing_key_str}]")
                try:
                    label = label_template_cleaned_mika.format(**safe_context_on_error)
                except Exception as e_inner_fmt:
                    logger.error(f"Double fault formatting TOC label '{label_template_cleaned_mika}' even with specific fallback: {e_inner_fmt}")
                    label = str(raw_label_template)

            if isinstance(label, str):
                for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                    label = label.replace(placeholder, glyph)
            placeholder_toc_lines.append(f"{temp_idx}. {label}")

    placeholder_toc_text = "\n".join(placeholder_toc_lines) if placeholder_toc_lines else "Your pet's cosmic map is being charted!"
    placeholder_toc_section_dict = {
        "section_id": "00_Table_of_Contents_Placeholder", "header": "🌌 Map of the Milky Way & Your Pet’s Path",
        "ai_content": placeholder_toc_text, "quote": "“Even the tiniest paw leaves a print on the stars.” – Unknown Cosmic Companion",
        "divider_tag": "toc", "meta": {"section_number": "0"}
    }
    logger.info(f"Placeholder Text-TOC content generated with {len(placeholder_toc_lines)} entries.")

    print("\nStep 2: Fetching all section content...")
    all_fetched_content_list = []
    use_live_ai = current_ai_mode and not current_test_mode and openai_client is not None

    if use_live_ai:
        print("   Source: Live AI. Calling OpenAI for content...")
        all_fetched_content_list = get_ai_sections_content(
            client_name=current_pet_name, current_occasion_mode=current_occasion_mode,
            current_pet_breed=current_breed, current_pet_species=current_species,
            current_birth_date_str=current_birth_date, current_birth_time_str=current_birth_time,
            current_pet_sound=pet_sound, section_definitions_source=PROMPTS,
            skip_fixed_stars=current_skip_fixed_stars,
            pronoun_mode=pronoun_mode_to_use 
        )
        logger.info(f"Fetched {len(all_fetched_content_list)} AI content blocks.")
    else:
        reason = ""
        if not current_ai_mode: reason = "AI Mode is OFF"
        elif current_test_mode: reason = "Test Mode is ON"
        elif not openai_client: reason = "OpenAI client not available"
        print(f"   Source: Dummy/Fallback content ({reason})...")
        try:
            from pet_report.assets.dummy_pet_content import DUMMY_CONTENT
            dummy_context_base = _prepare_pet_prompt_context(
                section_key="Dummy_Content_Setup", chart_data=calculated_chart_data_global,
                pet_name=current_pet_name, pet_species=current_species, pet_breed=current_breed,
                pet_sound=pet_sound, birth_date=current_birth_date, birth_time=current_birth_time,
                skip_fixed_stars=current_skip_fixed_stars,
                pronoun_mode=pronoun_mode_to_use 
            )

            for dummy_sid, dummy_template_data in DUMMY_CONTENT.items():
                if dummy_sid == "fixed_stars" and current_skip_fixed_stars:
                    logger.info(f"Dummy Content: Skipping 'fixed_stars' section (ID: {dummy_sid}) as skip_fixed_stars is True.")
                    continue

                header_raw = dummy_template_data.get('header_template', dummy_template_data.get('header', dummy_sid))
                header_cleaned_template_mika = _clean_mika_voice(clean_template_string_for_formatting(str(header_raw)))
                try:
                    header = header_cleaned_template_mika.format(**dummy_context_base)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Formatting dummy header for '{dummy_sid}' failed. Error: {e}")
                    header = str(header_raw).replace("{pet_name}", current_pet_name)

                ai_content_raw = dummy_template_data.get('ai_content', '')
                ai_content_cleaned_mika = _clean_mika_voice(str(ai_content_raw)) # Clean dummy content too
                ai_content_template = clean_template_string_for_formatting(ai_content_cleaned_mika)
                try:
                    ai_content = ai_content_template.format(**dummy_context_base)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Formatting dummy ai_content for '{dummy_sid}' failed. Error: {e}")
                    ai_content = ai_content_cleaned_mika

                dummy_transition_raw = dummy_template_data.get('transition_connector')
                if dummy_transition_raw:
                    dummy_transition_cleaned_mika = _clean_mika_voice(str(dummy_transition_raw))
                    dummy_transition_template = clean_template_string_for_formatting(dummy_transition_cleaned_mika)
                    try:
                        formatted_dummy_connector = dummy_transition_template.format(**dummy_context_base)
                        if isinstance(ai_content, str): ai_content += f"\n\n{formatted_dummy_connector}"
                        else: ai_content = formatted_dummy_connector
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Formatting dummy transition for '{dummy_sid}' failed. Error: {e}")
                        if isinstance(ai_content, str): ai_content += f"\n\n{dummy_transition_cleaned_mika}"
                        else: ai_content = dummy_transition_cleaned_mika

                quote_raw = dummy_template_data.get('quote', '')
                quote_cleaned_mika = _clean_mika_voice(str(quote_raw)) if quote_raw else None
                quote_template = clean_template_string_for_formatting(quote_cleaned_mika) if quote_cleaned_mika else None
                quote = None
                if quote_template:
                    try: quote = quote_template.format(**dummy_context_base)
                    except (KeyError, ValueError) as e:
                        logger.warning(f"Formatting dummy quote for '{dummy_sid}' failed. Error: {e}")
                        quote = quote_cleaned_mika

                for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                    if isinstance(header, str): header = header.replace(placeholder, glyph)
                    if isinstance(ai_content, str): ai_content = ai_content.replace(placeholder, glyph)
                    if isinstance(quote, str): quote = quote.replace(placeholder, glyph)

                all_fetched_content_list.append({
                    'section_id': dummy_sid, 'header': header, 'ai_content': ai_content,
                    'quote': quote, 'table_data': dummy_template_data.get("table_data"),
                    'meta': dummy_template_data.get('meta', {}),
                    'divider_tag': dummy_template_data.get('divider_tag', dummy_sid)
                })
            logger.info(f"Loaded {len(all_fetched_content_list)} dummy content blocks with cleaning.")
        except ImportError:
            logger.error(f"Could not import DUMMY_CONTENT. Fallback content generation will rely on prompt definitions only.")
            if PROMPTS and isinstance(PROMPTS, list):
                minimal_context_for_fallback_loop = _prepare_pet_prompt_context(
                    section_key="Minimal_Fallback_Loop_Setup", chart_data={},
                    pet_name=current_pet_name, pet_species=current_species, pet_breed=current_breed,
                    pet_sound=pet_sound, birth_date=current_birth_date, birth_time=current_birth_time,
                    skip_fixed_stars=current_skip_fixed_stars,
                    pronoun_mode=pronoun_mode_to_use 
                )
                for section_def_item in PROMPTS:
                    sid = section_def_item.get("section_id", "unknown_section")
                    if sid == "fixed_stars" and current_skip_fixed_stars:
                        logger.info(f"Minimal Fallback: Skipping 'fixed_stars' section (ID: {sid}) as skip_fixed_stars is True.")
                        continue

                    header_tpl_raw = section_def_item.get("header_template", section_def_item.get("header", "Section Header"))
                    header_tpl_cleaned_mika = _clean_mika_voice(clean_template_string_for_formatting(str(header_tpl_raw)))
                    try: hdr = header_tpl_cleaned_mika.format(**minimal_context_for_fallback_loop)
                    except (KeyError, ValueError): hdr = _clean_mika_voice(str(header_tpl_raw)).replace("{pet_name}", current_pet_name)

                    fallback_transition_raw = section_def_item.get("transition_connector", "")
                    fallback_transition_cleaned_mika = _clean_mika_voice(clean_template_string_for_formatting(str(fallback_transition_raw)))
                    fallback_transition = ""
                    if fallback_transition_cleaned_mika:
                        try: fallback_transition = fallback_transition_cleaned_mika.format(**minimal_context_for_fallback_loop)
                        except: fallback_transition = fallback_transition_cleaned_mika

                    body_content_parts = []
                    raw_body_parts = section_def_item.get("ai_prompt_parts", {})
                    if isinstance(raw_body_parts, dict):
                        cleaned_body_prompt_parts = {}
                        def local_clean_nested_dict_strings(d_raw, is_top_level_part=True):
                            cleaned_d = {}
                            for k_raw, v_raw in d_raw.items():
                                if isinstance(v_raw, str):
                                    text_to_clean_fmt = clean_template_string_for_formatting(v_raw)
                                    cleaned_d[k_raw] = _clean_mika_voice(text_to_clean_fmt)
                                elif isinstance(v_raw, dict): cleaned_d[k_raw] = local_clean_nested_dict_strings(v_raw, False)
                                elif isinstance(v_raw, list):
                                     cleaned_d[k_raw] = [ local_clean_nested_dict_strings(i_raw, False) if isinstance(i_raw, dict) else (_clean_mika_voice(clean_template_string_for_formatting(i_raw)) if isinstance(i_raw, str) else i_raw) for i_raw in v_raw ]
                                else: cleaned_d[k_raw] = v_raw
                            return cleaned_d
                        cleaned_body_prompt_parts = local_clean_nested_dict_strings(raw_body_parts)
                        def gather_body_strings_from_cleaned(parts_data_body):
                            if isinstance(parts_data_body, str):
                                if parts_data_body.strip(): body_content_parts.append(parts_data_body.strip())
                            elif isinstance(parts_data_body, dict):
                                for val_item_body in parts_data_body.values(): gather_body_strings_from_cleaned(val_item_body)
                            elif isinstance(parts_data_body, list):
                                for item_in_list_body in parts_data_body: gather_body_strings_from_cleaned(item_in_list_body)
                        gather_body_strings_from_cleaned(cleaned_body_prompt_parts)

                    formatted_body_content = ""
                    if body_content_parts:
                        try: formatted_body_content = ("\n\n".join(body_content_parts)).format(**minimal_context_for_fallback_loop)
                        except (KeyError, ValueError): formatted_body_content = "\n\n".join(body_content_parts)

                    if not formatted_body_content.strip():
                        formatted_body_content = f"This section, '{hdr}', offers a special insight into {current_pet_name}'s unique cosmic makeup. Every pet is a star!"

                    ai_content_final = formatted_body_content
                    if fallback_transition:
                        if isinstance(ai_content_final, str): ai_content_final += f"\n\n{fallback_transition}"
                        else: ai_content_final = fallback_transition

                    for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
                        if isinstance(hdr, str): hdr = hdr.replace(placeholder, glyph)
                        if isinstance(ai_content_final, str): ai_content_final = ai_content_final.replace(placeholder, glyph)

                    all_fetched_content_list.append({
                        'section_id': sid, 'header': hdr, 'ai_content': ai_content_final.strip() if isinstance(ai_content_final, str) else "",
                        'quote': None, 'meta': section_def_item.get('meta', {}),
                        'divider_tag': section_def_item.get('divider_tag', sid)
                    })
                logger.info(f"Generated {len(all_fetched_content_list)} minimal placeholders due to DUMMY_CONTENT import failure.")
        except Exception as e:
            logger.error(f"Error loading or formatting dummy content: {e}", exc_info=True)

    fetched_content_map = {s['section_id']: s for s in all_fetched_content_list if 'section_id' in s}
    # PATCH 19: The placeholder TOC section is not added here anymore, pdf_generator_pet.py handles its own TOC generation.
    # final_sections_for_pdf = [placeholder_toc_section_dict] 
    final_sections_for_pdf = []


    general_header_formatting_context = _prepare_pet_prompt_context(
        section_key="General_Header_Final_Assembly", chart_data=calculated_chart_data_global,
        pet_name=current_pet_name, pet_species=current_species, pet_breed=current_breed,
        pet_sound=pet_sound, birth_date=current_birth_date, birth_time=current_birth_time,
        skip_fixed_stars=current_skip_fixed_stars,
        pronoun_mode=pronoun_mode_to_use 
    )
    birth_details = calculated_chart_data_global.get('birth_details', {})
    general_header_formatting_context.update({
        'age': birth_details.get('age_string_long', general_header_formatting_context.get('age')),
        'birth_location': f"{birth_details.get('city', general_header_formatting_context.get('city','Unknown City'))}, {birth_details.get('country', general_header_formatting_context.get('country','??'))}",
    })
    sun_sign_details_data = calculated_chart_data_global.get('sun_sign_details', {})
    if isinstance(sun_sign_details_data, dict):
        general_header_formatting_context.update(sun_sign_details_data)

    print(f"\nAssembling final PDF sections based on SECTIONS_FOR_PET_REPORT ({len(SECTIONS_FOR_PET_REPORT)} definitions)...")
    for section_def_from_layout in SECTIONS_FOR_PET_REPORT:
        sid = section_def_from_layout.get("section_id")
        if not sid:
            logger.warning(f"SECTIONS_FOR_PET_REPORT item missing section_id: {section_def_from_layout}"); continue

        if sid == "fixed_stars" and current_skip_fixed_stars:
            logger.info(f"Final PDF Assembly: Skipping 'fixed_stars' section (ID: {sid}) as skip_fixed_stars is True.")
            continue
        
        # PATCH 19: TOC is handled by PDF generator, so skip any TOC-specific tags here.
        if section_def_from_layout.get("divider_tag") == "toc": 
            continue

        retrieved_content_block = fetched_content_map.get(sid, {})

        header_template_from_layout_raw = section_def_from_layout.get("header_template", section_def_from_layout.get("header", "Untitled Section"))
        header_template_from_layout_cleaned_mika = _clean_mika_voice(clean_template_string_for_formatting(str(header_template_from_layout_raw)))
        try:
            final_header_text = header_template_from_layout_cleaned_mika.format(**general_header_formatting_context)
        except (KeyError, ValueError) as e_fmt_hdr:
            logger.warning(f"Formatting final header for '{sid}' ('{header_template_from_layout_cleaned_mika}') failed. Error: {e_fmt_hdr}. Using basic fallback.")
            final_header_text = _clean_mika_voice(str(header_template_from_layout_raw)).replace("{pet_name}", current_pet_name)
        except Exception as e_fmt_hdr_other:
            logger.error(f"Unexpected error formatting final header for '{sid}': {e_fmt_hdr_other}. Using basic fallback.")
            final_header_text = _clean_mika_voice(str(header_template_from_layout_raw)).replace("{pet_name}", current_pet_name)

        ai_content_to_use = retrieved_content_block.get("ai_content", "")
        # PATCH 19: Final safety clean on AI content from map, although call_openai_updated should have handled it.
        ai_content_to_use = _clean_mika_voice(ai_content_to_use)

        if not ai_content_to_use or (isinstance(ai_content_to_use, str) and not ai_content_to_use.strip()):
            ai_content_to_use = f"This special glimpse into {current_pet_name}'s cosmic story for the section '{final_header_text}' is still unfolding with wonder and charm. Their unique spirit shines brightly!"
            logger.info(f"Section {sid} had blank AI content in final assembly, injected fallback message.")

        quote_to_use = retrieved_content_block.get("quote")
        # PATCH 19: Clean quote from map as well
        quote_to_use = _clean_mika_voice(quote_to_use)


        for placeholder, glyph in SYMBOL_PLACEHOLDER_TO_GLYPH_MAP.items():
            if isinstance(final_header_text, str): final_header_text = final_header_text.replace(placeholder, glyph)
            if isinstance(ai_content_to_use, str): ai_content_to_use = ai_content_to_use.replace(placeholder, glyph)
            if isinstance(quote_to_use, str): quote_to_use = quote_to_use.replace(placeholder, glyph)

        final_sections_for_pdf.append({
            "section_id": sid, "header": final_header_text, "ai_content": ai_content_to_use,
            "quote": quote_to_use, "divider_tag": section_def_from_layout.get("divider_tag", sid),
            "meta": retrieved_content_block.get("meta", section_def_from_layout.get("meta", {})),
            "table_data": retrieved_content_block.get("table_data")
        })
        logger.info(f"Assembled section: {sid} - '{str(final_header_text)[:50]}...' with divider_tag: '{section_def_from_layout.get('divider_tag', sid)}'")

    print(f"\nStep 3: Creating PDF with {len(final_sections_for_pdf)} content sections (TOC generated internally by PDF module)...")
    safe_name_for_file = "".join(c for c in current_pet_name if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output_path_pdf = os.path.join(current_output_dir, f"{safe_name_for_file}_{current_species}_{ts}.pdf")
    print(f"The PDF will be saved as: {final_output_path_pdf}")

    final_astrology_wheel_chart_to_use = assets_for_pdf_context.get('chart_image_path')
    if not final_astrology_wheel_chart_to_use and pillow_available and ImageFont:
        print("INFO: Astrology wheel chart image not available or generation failed. Attempting to create a placeholder image with Pillow.")
        placeholder_chart_image_name = f"placeholder_chart_{safe_name_for_file}_{ts}.png"
        placeholder_output_dir = os.path.join(REPORTS_OUTPUT_BASE_DIR, 'chart_images')
        try:
            os.makedirs(placeholder_output_dir, exist_ok=True)
            potential_placeholder_path = os.path.join(placeholder_output_dir, placeholder_chart_image_name)
            img = PILImage.new('RGB', (400, 400), color='lightgrey')
            d = ImageDraw.Draw(img)
            text_to_draw = f"Astrology Chart Placeholder\nfor {current_pet_name} ({current_species})"
            font = None
            try: font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                try: font = ImageFont.load_default()
                except Exception as e_font_load: logger.warning(f"Could not load default font: {e_font_load}. Text on placeholder might be missing.")

            if font:
                # Use textbbox if available (Pillow >= 8.0.0) for better centering
                if hasattr(d, 'textbbox'): 
                    # anchor "mm" for middle-middle might simplify, or calculate from lt
                    text_bbox = d.textbbox((200, 200), text_to_draw, font=font, anchor="mm", align="center")
                    # For multiline, textbbox might give overall box. Manual adjustment might still be needed if anchor="mm" isn't perfect.
                    # text_x = (400 - (text_bbox[2] - text_bbox[0])) / 2
                    # text_y = (400 - (text_bbox[3] - text_bbox[1])) / 2
                    # d.text((text_x, text_y), text_to_draw, fill=(0,0,0), font=font, align="center")
                    d.text((200, 200), text_to_draw, fill=(0,0,0), font=font, anchor="mm", align="center")
                elif hasattr(d, 'textsize'): # Fallback for older Pillow
                    text_width, text_height = d.textsize(text_to_draw, font=font)
                    # Approx center for multiline (textsize may not be perfect for multiline height)
                    num_lines = text_to_draw.count('\n') + 1
                    line_height_approx = text_height / num_lines 
                    total_text_block_height = line_height_approx * num_lines # Use this or just text_height
                    x = (400 - text_width) / 2
                    y = (400 - total_text_block_height) / 2 
                    d.text((x, y), text_to_draw, fill=(0,0,0), font=font, align="center")
                else: # Basic fallback
                    d.text((10, 180), text_to_draw, fill=(0,0,0), font=font, align="center") # align might not be supported
            else: # No font loaded
                 d.text((10, 180), f"Chart for\n{current_pet_name}", fill=(0,0,0))

            img.save(potential_placeholder_path)
            final_astrology_wheel_chart_to_use = potential_placeholder_path
            assets_for_pdf_context['chart_image_path'] = final_astrology_wheel_chart_to_use
            logger.info(f"Using created placeholder astrology wheel chart image: {final_astrology_wheel_chart_to_use}")
        except Exception as e_img_placeholder:
            logger.warning(f"Could not create Pillow placeholder astrology wheel chart image: {e_img_placeholder}.")
    elif not final_astrology_wheel_chart_to_use and not pillow_available:
        logger.info("Astrology wheel chart image not available and Pillow is not available for placeholder.")

    pdf_gen_full_context = {
        'client_name': current_pet_name,
        'species': current_species,
        'pet_breed': current_breed,
        'pet_sound': pet_sound,
        'chart_data': calculated_chart_data_global,
        'sections': final_sections_for_pdf,
        'occasion_mode': current_occasion_mode,
        'assets_dir': current_assets_dir,
        'fonts_dir': current_fonts_dir,
        'data_jsons_dir': current_data_jsons_dir,
        'PET_PROMPTS': PROMPTS, # For any internal logic in PDF gen that might need it
        'SECTION_LAYOUT_PRESETS': SECTION_LAYOUT_PRESETS, # Same as above
        'is_pet_report': True,
        'skip_fixed_stars': current_skip_fixed_stars,
        'pronoun_mode': pronoun_mode_to_use 
    }
    pdf_gen_full_context.update(assets_for_pdf_context)


    try:
        logger.info(f"Calling generate_pet_pdf. Astrology Wheel: {pdf_gen_full_context.get('chart_image_path')}, Custom Pet Portrait URL: {pdf_gen_full_context.get('custom_pet_image_url')}, Pronoun Mode: {pdf_gen_full_context.get('pronoun_mode')}")
        success = generate_pet_pdf(
            output_path=final_output_path_pdf,
            # Pass generation_context as the primary way to send data
            generation_context=pdf_gen_full_context 
        )
        if success:
            print(f"\nWoohoo! Pet report PDF created: {final_output_path_pdf}")
        else:
            print("\nOh no! The PDF wasn't created. Check for earlier error messages from the PDF generator.")
    except TypeError as te:
         logger.error(f"TypeError calling PDF generator: {te}. This might indicate a mismatch in expected arguments for generate_pet_pdf.", exc_info=True)
    except Exception as e_pdf:
        logger.error(f"PDF creation failed: {e_pdf}", exc_info=True)

    print(f"\n--- All done with {current_pet_name}'s Pet Astrology Report! ---")

def test_mode_cli_arg_present():
    return "--test-mode" in sys.argv

def skip_fixed_stars_cli_arg_present():
    return "--skip_fixed_stars" in sys.argv

if __name__ == '__main__':
    # Ensure logger is configured before any logging calls
    initial_log_level_main = logging.DEBUG if test_mode_cli_arg_present() else logging.INFO
    logging.basicConfig(level=initial_log_level_main, format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(module)s.%(funcName)s - %(message)s', force=True)
    logger = logging.getLogger(__name__) # Re-get logger for main block after config
    logger.info(f"Initial logging configured to {logging.getLevelName(initial_log_level_main)} for __main__ block.")


    calculated_chart_data_global = {} # Initialize global

    ai_mode_intended_cli = "--ai_mode" in sys.argv and not test_mode_cli_arg_present()

    if ai_mode_intended_cli:
        if OpenAI is None: logger.warning("\nIMPORTANT: OpenAI library not found or failed to import. AI calls will be skipped even if --ai_mode is on.")
        elif not os.getenv("OPENAI_API_KEY"): logger.warning("\nIMPORTANT: OPENAI_API_KEY environment variable not set. AI calls will be skipped even if --ai_mode is on.")
        elif not openai_client: logger.warning("\nIMPORTANT: OpenAI client failed to initialize (check API key or other setup). AI calls will be skipped even if --ai_mode is on.")
    elif not test_mode_cli_arg_present() and not "--ai_mode" in sys.argv :
         if not openai_client: logger.info("\nINFO: OpenAI client not available. AI content will not be generated. Falling back to dummy content by default unless --ai_mode is specified AND client is configured.")

    main()
#--- END OF FILE run_pet_report.py ---
