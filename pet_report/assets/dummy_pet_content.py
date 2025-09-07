# pet_report/assets/dummy_pet_content.py

DUMMY_CONTENT = {
    "cover": {
        "header": "Dummy Cover Title for {client_name}",
        "ai_content": "This is dummy cover content for {client_name}, the {species}.",
        "quote": "A dummy quote for the cover."
    },
    "section_1": { # Example section_id, adapt to your actual IDs
        "header": "Dummy Section 1: Introduction",
        "ai_content": "This is some dummy static text for the introduction section. We are not calling OpenAI because we are in test mode. This section would normally introduce the wonders of pet astrology for {client_name}.",
        "quote": "Dummy thoughts for a starry night."
    },
    "01_Pet_Intro": {
        "header": "Dummy Paws Prologue for {client_name}",
        "ai_content": "Welcome {client_name} ({species})! This is your dummy cosmic tail. Test mode is active, so this is static content.",
        "quote": "The stars are full of dummy wags and purrs."
    },
    "02_Pet_Core": {
        "header": "Dummy Core Spirit of {client_name}",
        "ai_content": "{client_name} is a bundle of dummy joy with a heart of static gold. Their sun sign shows a playful and loyal nature, all from this test content.",
        "quote": "Every dummy paw print is a step on a starry path."
    },
    "03_Client_Details_Pet": {
        "header": "Dummy Cosmic ID Card",
        "ai_content": "This section usually contains a table with pet details. In test mode, we're just showing this message.",
        "table_data": {
            "Pet Name": {"details": "{client_name} (Dummy)"},
            "Species": {"details": "{species} (Dummy)"},
            "Breed": {"details": "Test Breed (Dummy)"},
            "Sun Sign": {"details": "Aquarius (Dummy)"}
        },
        "quote": "Dummy details from the ether."
    },
    "05_Special_Divider_Section": { # Example, adjust to your actual IDs
        "header": "Dummy Wellness Whiskers",
        "ai_content": "Playtime is essential for {client_name}'s happiness. Consider dummy puzzle toys! This is static test content.",
        "quote": "A healthy pet is a happy dummy constellation."
    },
    "health_wellness": { # Example, adjust to your actual IDs
        "header": "Dummy Health & Wellness Insights",
        "ai_content": "In test mode, here's some dummy advice for {client_name}'s well-being. Lots of virtual pats and static treats!",
        "quote": "To dummy health and beyond!"
    },
    "play_behavior": { # Example, adjust to your actual IDs
        "header": "Dummy Play & Behavior Notes",
        "ai_content": "Exploring {client_name}'s dummy play style and behavior patterns. This content is static and for testing purposes.",
        "quote": "Let the dummy games begin!"
    },
    "99_Pet_Outro": {
        "header": "Dummy Final Paw-spective",
        "ai_content": "May your journey with {client_name} be filled with starry nights and sunny days! This is dummy concluding text. Bye {client_name}!",
        "quote": "The universe loves a happy dummy pet."
    }
    # Add more section_ids and their dummy content as needed
    # Ensure keys match the 'section_id' used in your PET_PROMPTS
}