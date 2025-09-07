#--- START OF FILE prompt_definitions_pet.py ---

# Modified prompt_definitions_pet.py
# This version meticulously cleans all placeholders to simple keys
# and moves all descriptive/example content to comments.
# NB: If ValueErrors related to format specifiers or single braces persist
# after run_pet_report.py updates, the string literals below need
# extremely careful auditing for any unescaped literal '{' or '}'
# (should be '{{' or '}}') or patterns like '{key: non_standard_char}'
# that Python's .format() might misinterpret.

PET_PROMPTS = [
{
"section_id": "sun_sign",
"header_template": " {pet_name}'s Radiant Sun Sign: The Heart of Their Sparkle in {sun_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika's Voice: Observational, loving, witty)
Ever notice that special something about {pet_name}? That unique shine in their eyes, the particular way they {pet_sound} when they're truly happy, or that little swagger in their step when they know they're about to get a treat? That, my friend, is their Sun sign energy beaming through! It’s like their own personal superpower, the core of their amazing little personality, and the main reason they're so uniquely, wonderfully them. Perhaps you remember well the day they were born, {birth_date_formatted}.
""", # --- PATCH 3: Example usage of birth_date_formatted ---
"astrological_heart": """
(Mika's Voice: Genuinely insightful without being preachy, explains astrology simply)
In the big cosmic playground, the Sun ☉ is the star of the show – literally! It tells us what makes {pet_name} tick, what energizes them, and how their fundamental character shines. With their Sun in {sun_sign_name}, {pet_name} is basically a {sun_sign_name} superstar in {breed_lowercase_article_noun_phrase} costume!

This means they're naturally inclined to be {sun_sign_keyword_adj_1}.
They're probably all about {sun_sign_keyword_noun_1},
and their main way of expressing their fabulous self is often quite {sun_sign_keyword_adv_1}.
It’s their factory default setting for awesomeness!
""", 
"pet_specific_examples": """
(Mika's Voice: Grounded in real pet behavior, species-aware examples)
So, how does this {sun_sign_name} sunshine play out in real life for a {species} like {pet_name}? Well, you've probably seen it a million times!

    Does {pet_name} ({sun_sign_example_1})

    Or maybe they ({sun_sign_example_2})

    And don't forget how they ({sun_sign_example_3})

That's their {sun_sign_name} Sun, pure and simple, making them the one-of-a-kind character you know and love.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika's Voice: Fun, informal, engaging activity)
Want to really see {pet_name}'s {sun_sign_name} Sun blaze? Try this: Tomorrow, dedicate a whole five minutes to something you know makes their little heart sing based on these {sun_sign_name} vibes – maybe it's ({sun_sign_activity_suggestion}).
Just watch that inner sparkle ignite! No pressure, just a bit of fun to celebrate their core awesomeness.
""", 
"light_reflection_question": """
(Mika's Voice: Warm, prompting a smile of recognition)
When {pet_name} is being their most unapologetically {sun_sign_name} self, what’s the one quirky thing they do that always makes you laugh or melts your heart?
"""
},
"soul_archetype_nickname": """
(Mika's Voice: Affectionate, adds a sweet pet nickname)
Yep, with a Sun in {sun_sign_name}, {pet_name} isn't just any {species}; they're your very own little '{sun_sign_soul_archetype_nickname}'!
Cherish that radiant, unique spark.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "1",
"section_title": "Solar Snuggles & Spotlight Moves"
},
"transition_connector": "Now that we've basked in their sunny sparkle, let's gently tiptoe into the softer moonlight of their emotional world."
},
{
"section_id": "moon_sign",
"header_template": " {pet_name}'s Emotional Glow: The Secret Moonlight in {moon_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika's Voice: Observational, loving, witty, with a slightly softer, more intuitive feel for the Moon)
Alright, so we know {pet_name}’s Sun sign is their big, bright personality spotlight. But what about those quieter moments? The soft sighs, the contented purrs (or happy little {pet_sound}s!), the way they just know when you need a furry friend nearby? That, dear friend, is the gentle glow of their Moon sign. It's their heart's secret language, their inner comfort-o-meter, and the key to what truly makes them feel safe, loved, and understood.
""",
"astrological_heart": """
(Mika's Voice: Genuinely insightful without being preachy, explains astrology simply with a touch of warmth)
In the magical map of the stars, the Moon ☽ isn't just a pretty nightlight; it represents our deepest feelings, our instincts, and what we need to feel emotionally cozy and secure. For your wonderful {pet_name}, their Moon was nestled in the sign of {moon_sign_name} when they joined the world. This means their emotional world is painted with the tender shades of {moon_sign_name}.

So, when it comes to feelings, they're likely to be {moon_sign_keyword_adj_1}.
They probably find their ultimate comfort in {moon_sign_keyword_noun_1},
and when they're showing you their soft underbelly (sometimes literally!), they do it with a distinctly {moon_sign_keyword_adv_1} kind of vibe.
It’s their soul's preferred brand of fuzzy slippers!
""", 
"pet_specific_examples": """
(Mika's Voice: Grounded in real pet behavior, species-aware examples, focusing on emotional expression and comfort-seeking)
You've likely seen this lunar loveliness in action with your {species}, {pet_name}! For instance:

    Does {pet_name} ({moon_sign_example_1})

    Or perhaps they ({moon_sign_example_2})

    And isn't it sweet how they ({moon_sign_example_3})

That’s their {moon_sign_name} Moon, wearing its heart on its furry, feathery, or sleek sleeve, and showing you exactly what makes their little spirit feel cherished.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika's Voice: Fun, informal, engaging activity focused on emotional connection)
Want to give {pet_name}'s {moon_sign_name} Moon an extra special glow-up? Try this: Tonight, create a little 'cuddle puddle' or 'comfort corner' inspired by their Moon sign – maybe it’s ({moon_sign_comfort_activity_suggestion}).
Settle in with them for a few minutes of uninterrupted affection. No agenda, just pure, moonlit love.
""", 
"light_reflection_question": """
(Mika's Voice: Warm, prompting a heartfelt reflection)
What's that one little thing {pet_name} does when they're seeking comfort or showing affection that just melts you every single time, perfectly capturing their {moon_sign_name} heart?
"""
},
"soul_archetype_nickname": """
(Mika's Voice: Affectionate, adds a sweet pet nickname related to emotions/comfort)
Yes, with a Moon in {moon_sign_name}, your {pet_name} isn't just a {species}; they're your very own little '{moon_sign_soul_archetype_nickname}'!
Their feelings run deep, and their love is a quiet, steady moonlight in your life.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "2",
"section_title": "Moonbeam Moods & Gentle Glows"
},
"transition_connector": "Understanding their heart's whispers is key, and next, we'll tune into how their clever little mind ticks and 'talks'!"
},
{
"section_id": "mercury_sign",
"header_template": " {pet_name}'s Bright Ideas & Chatterbox Corner: Powered by Mercury in {mercury_sign_name}!",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Clever, warm, pet-savvy)
Ever caught {pet_name} trying to “explain” something to you with an expressive {pet_sound}, a dramatic stare, or an elaborate tail flick? That’s Mercury at work – the planet of communication and cleverness – and your little furball's got plenty of opinions! Whether they're silently plotting or narrating their own life like a four-legged podcast, Mercury helps decode what’s rattling around in that adorable noggin.
""",
"astrological_heart": """
(Mika’s Voice: Lightly witty, explains astrology clearly but charmingly)
Mercury ☿ is like your pet’s cosmic control panel for learning, thinking, and expressing themselves – even if words aren’t involved. With Mercury in {mercury_sign_name}, {pet_name} is naturally {mercury_sign_keyword_adj_1}.
They absorb the world through {mercury_sign_keyword_noun_1},
and their style of “talking” is typically {mercury_sign_keyword_adv_1}.

If Mercury in {mercury_sign_name} were a {species}, it’d be the one who {mercury_sign_analogy}.
""", 
"pet_specific_examples": """
(Mika’s Voice: Real pet observations with flavor)
Here’s where it gets fun. You might recognize Mercury in {mercury_sign_name} if {pet_name}:

    {mercury_sign_example_1}.

    {mercury_sign_example_2}.

    {mercury_sign_example_3}.

Smart cookie, this one.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Playful and clever)
Next time {pet_name} is trying to tell you something – maybe about the empty food bowl crisis or a mysterious squirrel sighting – try mimicking them. Bark back, meow melodramatically, or wiggle your eyebrows like you’re in on the plan. It’s a hilarious bonding moment and it’s Mercury-approved enrichment.
""",
"light_reflection_question": """
What’s your favorite example of {pet_name} being way smarter than they let on?
"""
},
"soul_archetype_nickname": """
With Mercury in {mercury_sign_name}, your {species} is basically a fuzzy little ‘{mercury_sign_soul_archetype_nickname}’ –
always thinking, always scheming, and always somehow one step ahead.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "3",
"section_title": "Clever Chirps & Curious Capers"
},
"transition_connector": "With such bright sparks of thought, it's only natural to wonder how they share their affection. Let's explore their unique love language next."
},
{
"section_id": "venus_sign",
"header_template": " {pet_name}'s Love Language: Venus in {venus_sign_name} Knows What Feels Good!",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Warm and charming)
Let’s talk love – the tail-wagging, biscuit-sharing, snuggle-demanding kind. Venus rules what makes us feel adored and how we show affection, and {pet_name} has their own cosmic flavor of fuzzy romance. Whether they’re a clingy cuddlebug or a “love you from over here” type, Venus is their affection operating system.
""",
"astrological_heart": """
(Mika’s Voice: Gently witty)
Venus ♀ in {venus_sign_name} means {pet_name} tends to seek love through {venus_sign_keyword_noun_1}
and express it {venus_sign_keyword_adv_1}.
This sign flavor makes them {venus_sign_keyword_adj_1}.

If Venus in {venus_sign_name} were a {species}, it’d be the one who {venus_sign_analogy}.
""", 
"pet_specific_examples": """
(Mika’s Voice: Grounded, sensory, often funny)
You might see their Venus show up when they:

    {venus_sign_example_1}.

    {venus_sign_example_2}.

    {venus_sign_example_3}.

It’s cosmic-level affection, {venus_sign_name}-style.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Cozy and playful)
Next cuddle session, try tuning in to their Venus vibe: pet them in their favorite spot, whisper sweet nothings, or offer that one toy they treat like royalty. Bonus points if they do the satisfied sigh or happy tail-thump afterward.
""",
"light_reflection_question": """
What’s the one little gesture that makes you melt because you know it’s your pet’s way of saying “I love you”?
"""
},
"soul_archetype_nickname": """
With Venus in {venus_sign_name}, your {species} is basically a ‘{venus_sign_soul_archetype_nickname}’ –
bringing love in their own signature style.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "4",
"section_title": "Cuddle Puddles & Cosmic Charms"
},
"transition_connector": "Knowing what makes them feel adored is wonderful, and now, let's see what fuels their playful pounces and energetic zoomies!"
},
{
"section_id": "mars_sign",
"header_template": " {pet_name}'s Zoomies & Grit: Mars in {mars_sign_name} Packs a Punch!",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Excited, energized)
Ever wondered what fuels your pet’s zoomies, dramatic digs, or heroic efforts to chase the same squirrel every day for three years straight? That’s Mars – the cosmic go-button! It governs drive, action, play style, and how your little fur-rocket handles frustration (or mischief!).
""",
"astrological_heart": """
(Mika’s Voice: Energetic, slightly cheeky)
Mars ♂ in {mars_sign_name} means {pet_name} tends to do stuff in a {mars_sign_keyword_adj_1} way.
Their energy is geared toward {mars_sign_keyword_noun_1},
and when they move, it’s usually {mars_sign_keyword_adv_1}.

If Mars in {mars_sign_name} were a {species}, it’d be the one that {mars_sign_analogy}.
""", 
"pet_specific_examples": """
(Mika’s Voice: Zippy and entertaining)
Spotting Mars in real life? Try these:

    {mars_sign_example_1}.

    {mars_sign_example_2}.

    {mars_sign_example_3}.

Their playbook is part gladiator, part goofball.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Interactive and validating)
Feeling brave? Create a “Mars moment”: Set up a short obstacle course, tug game, or treat hunt that lets {pet_name} burn off steam. Cheer them on like a sports commentator. You’ll see their {mars_sign_name} drive come alive – and it’s wildly entertaining.
""",
"light_reflection_question": """
When’s a time {pet_name} showed real grit or enthusiasm – the kind that had you laughing, applauding, or slightly worried about your furniture?
"""
},
"soul_archetype_nickname": """
With Mars in {mars_sign_name}, your {species} is a ‘{mars_sign_soul_archetype_nickname}’ –
fierce in play, bold in spirit.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "5",
"section_title": "Zoomie Zeal & Playful Prowess"
},
"transition_connector": "That fiery spirit sure is something! Building on that energy, let's see how they present their amazing self to the world at first glance."
},
{
"section_id": "rising_sign",
"header_template": " {pet_name}'s First Impression: The Sparkle They Show the World ({rising_sign_name} Rising)",
"ai_prompt_parts": {
"sparky_intro": """
(Mika's Voice: Charming, clever, observational)
You know how some pets just have a certain style when they meet someone new? That initial 'hello,' whether it's a confident tail-wag, a cautious sniff from afar, or a full-blown charm offensive complete with a dramatic {pet_sound}? That's their Rising Sign, or Ascendant, working its magic! It’s like the snazzy outfit they wear to the 'Meet the World' party, giving everyone a delightful first glimpse of the amazing {species} within.
""",
"astrological_heart": """
(Mika's Voice: Friendly, clear, explains astrology simply with a fun analogy)
So, picture this: the Rising Sign (astrologer-speak for Ascendant or ASC) is the zodiac sign that was peeking over the eastern horizon the very moment {pet_name} made their grand entrance into the world (on {birth_date_formatted}, no less!). It’s all about their social handshake, their instinctive approach to new things, and the first impression they make. With {pet_name}’s Rising Sign in {rising_sign_name}, their 'hello' to the universe comes with a lovely dash of {rising_sign_name} flair!

If the {rising_sign_name} Rising were {breed_lowercase_article_noun_phrase}, they’d be the one who ({rising_sign_analogy}).
This means {pet_name} tends to meet the world with an energy that's often {rising_sign_keyword_adj_1},
and their initial vibe is usually quite {rising_sign_keyword_adj_2}.
""", # --- PATCH 3: Example usage of birth_date_formatted ---
"pet_specific_examples": """
(Mika's Voice: Relatable, witty, species-aware examples of first impressions)
You’ve probably seen this {rising_sign_name} sparkle plenty of times with your {species}, {pet_name}! For instance:

    When a new visitor comes to the door, do they ({rising_sign_example_1})

    Or maybe when encountering another animal on a walk, {pet_name} ({rising_sign_example_2})

    And how about when you introduce a new toy or a change in scenery? Do they ({rising_sign_example_3})

That's their {rising_sign_name} Rising, setting the stage for the wonderful character you get to know more deeply every day!
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika's Voice: Light, engaging activity focused on social observation)
Want a fun little window into {pet_name}'s social style? Next time you're out and about (in a safe, comfy way for them, of course!) or a new friend pops by, consciously watch {pet_name}'s very first reaction for about 10 seconds. What’s their go-to move? The tail? The ears? The {pet_sound}? It's like watching their personal 'welcome committee' in action, powered by their {rising_sign_name} Rising!
""",
"light_reflection_question": """
(Mika's Voice: Warm, simple question prompting a fond memory)
Thinking back to the very first time you laid eyes on {pet_name}, or one of your earliest interactions, what was it about their initial 'hello' that utterly charmed you or made you smile?
"""
},
"soul_archetype_nickname": """
(Mika's Voice: Affectionate, adds a sweet pet nickname related to social style/first impressions)
With that {rising_sign_name} Rising, {pet_name} isn't just greeting the world; they're doing it as your very own little '{rising_sign_soul_archetype_nickname}'!
It’s all part of their unique, first-impression fabulousness.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "6",
"section_title": "Cosmic Collar Compass: First Impressions"
},
"transition_connector": "That first 'hello' tells us so much! Now, let’s follow the twinkle in their eye towards their soul’s special North Star path."
},
{
"section_id": "north_node",
"header_template": " {pet_name}'s Guiding Star: The North Node Beckoning in {north_node_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Curious, gentle encouragement, a little bit wondrous)
Ever watch {pet_name} get that little spark of curiosity, that sudden urge to try something just a wee bit new or different? Maybe it's a new path on your walk, a different way to ask for a treat, or even a tentative sniff of a friendly new {species}? That’s like a little wink from their North Node! It’s their inner compass, gently pointing towards exciting new ways for their wonderful little soul to blossom and grow, all while having you right there cheering them on.
""",
"astrological_heart": """
(Mika’s Voice: Informative but warm — explain the North Node clearly and simply, using a metaphor like 'compass,' 'growth garden,' or 'cosmic invitation')
In the big, twinkly map of the stars, the North Node ☊ isn't a strict set of directions, more like a friendly, cosmic invitation to explore. It shows the kind of experiences and qualities that can help {pet_name}'s spirit stretch and learn new things in this lifetime. With their North Node in {north_node_sign_name}, it’s like their personal 'Growth Garden' is inviting them to plant seeds of {north_node_keyword_adj_1}.

This means there's a gentle cosmic nudge for {pet_name} to perhaps become a bit more {north_node_keyword_adj_2},
or to find real joy in activities that involve {north_node_keyword_noun_1}.
It's all about adding new, wonderful experiences to their already amazing repertoire!
""", 
"pet_specific_examples": """
(Mika’s Voice: Playful and practical — show how a pet with this sign’s North Node might start exploring its qualities in real life, using 2–3 concrete, species-aware examples)
So, how might you see this {north_node_sign_name} North Node blossoming in your {species}, {pet_name}? Keep an eye out for these little adventures:

    Are they starting to ({north_node_example_1})

    Or maybe you've noticed {pet_name} ({north_node_example_2})

    And how about this for a growth spurt? ({north_node_example_3})

These aren't giant leaps, just sweet little paw-steps towards new ways of being, all part of their unique soul journey.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Invite the guardian to notice one way their pet might be blossoming toward these qualities, and encourage a fun, simple moment of encouragement or bonding)
Want to be {pet_name}'s number one cheerleader on their North Node adventure? Easy peasy! Next time you see them trying something that feels a little new or brave for them (even if it's just investigating that 'scary' vacuum cleaner from a slightly closer distance!), give them a quiet 'atta-pet!' with a happy tone and a favorite scratch. It’s like saying, 'Go you! I see you growing, and it’s awesome!'
""",
"light_reflection_question": """
(Mika’s Voice: Prompt a fond memory or recent “aha!” moment — how has {pet_name} been growing into their own?)
Can you think of a recent moment, big or small, where {pet_name} surprised you by being a little more {north_node_keyword_adj_1} or trying something that showed their inner {north_node_soul_archetype_nickname} shining through?
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Sweet, empowering nickname that reflects the growth journey — e.g., 'Braveheart in Training,' 'Soul Sprout,' 'Aspiring Angelpaw,' 'Curiosity Captain,' 'Little Bloom')
With their North Node in {north_node_sign_name}, {pet_name} is on a lovely path, like your very own '{north_node_soul_archetype_nickname}'!
Every new discovery makes their unique light shine even brighter.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "7",
"section_title": "Fur-tune GPS: Their North Node Path"
},
"transition_connector": "As they journey on their growth path, it's lovely to remember the quiet wisdom they carry. Next, we'll explore their gentle healing pawprints."
},
{
"section_id": "chiron",
"header_template": " Furry Healer Pawprints: Chiron’s Quiet Wisdom in {chiron_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Soft, gentle, a bit reverent — like storytelling by starlight)
Every pet has a superpower — not just in the way they bring joy, but in how they comfort us when we need it most. That magical ability often ties back to something deep in their chart: Chiron, the cosmic healer. It’s not always flashy, but it’s sacred. It’s the part of your fur-friend’s soul that knows how to hold space, even if they don’t know they’re doing it.
""",
"astrological_heart": """
(Mika’s Voice: Insightful but nurturing)
In astrology, Chiron is known as the “wounded healer.” It shows us where there’s a sensitive spot — a place of tenderness — but also where incredible compassion and wisdom can grow.

With Chiron in {chiron_sign_name}, {pet_name} carries a kind of emotional tuning fork. They might instinctively react to certain vibes in the environment, or show deep sensitivity around particular routines, sounds, or situations. But here’s the magic: that very sensitivity becomes a gift — helping them comfort others, protect their loved ones, or express a kind of silent empathy you can feel in your bones.

It’s not about what’s wrong with them. It’s about what they know, soul-deep, from carrying a little sacred scar that turns into light.
""",
"pet_specific_examples": """
(Mika’s Voice: Tender and observational)
Have you noticed how:

    {pet_name} {chiron_example_1}?

    They {chiron_example_2}?

    Or maybe they {chiron_example_3}?

Those are clues that their Chiron is quietly working behind the scenes, turning past sensitivity into healing presence.
""", 
"guardian_interaction": {
"try_this_for_fun": """
Today, take a moment to thank {pet_name} for the energy they hold for you — even if it’s just a head scratch and a whisper. They may not understand the words, but they’ll feel the love echo through the bond.
""",
"light_reflection_question": """
What’s one moment when {pet_name} helped you through something — not with a trick or a bark, but just by being their quiet, beautiful self?
"""
},
"soul_archetype_nickname": """
With Chiron in {chiron_sign_name}, your {species} is a gentle ‘{chiron_soul_archetype_nickname}’ —
soft where the world is hard, strong where it matters most.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "8",
"section_title": "Furry Healer Pawprints: Chiron's Wisdom"
},
"transition_connector": "Their capacity for quiet comfort is profound. But every sweet soul also has a spark of wild, untamed spirit – let's peek into that mystery next."
},
{
"section_id": "black_moon_lilith",
"header_template": " Mysterious Pawprints & Feral Fire: Lilith’s Wild Spirit in {black_moon_lilith_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Whispery, playful, with a knowing wink)
Alright, buckle your collar — we’re going deep into the mystical forest now! There’s a side to every pet that’s a little bit... wild. Not unruly — more like untamed, instinctive, and fiercely true to who they are. That’s where Lilith lives — the Black Moon point in their chart that speaks of primal spirit, secret strengths, and moments where your pet says, “I do things my way.”
""",
"astrological_heart": """
(Mika’s Voice: Softly powerful, like revealing a secret)
Black Moon Lilith isn’t a planet — it’s a point in space that symbolizes raw power and deep inner knowing. It’s where your pet says no thank you to what doesn’t resonate. With Lilith in {black_moon_lilith_sign_name}, {pet_name} holds a spark of independence, even rebellion — a part of them that doesn’t compromise and refuses to be tamed in certain areas.

This doesn’t mean they’re difficult. It means they’re whole. Authentic. Fierce in their values, even if those values are “I don’t like wet food” or “Only I get to choose when cuddles happen.”

Lilith helps your fur-friend walk through life with a touch of mystery and a lot of dignity.
""",
"pet_specific_examples": """
(Mika’s Voice: Clever and observant)
Ever noticed how:

    {pet_name} {lilith_example_1}?

    They {lilith_example_2}?

    Or maybe they’re just {lilith_example_3}?

That’s Lilith — reminding the world that even the cuddliest fluffball has a throne, claws, and boundaries.
""", 
"guardian_interaction": {
"try_this_for_fun": """
Next time {pet_name} shows their “don’t mess with me” moment — honor it. Give them space. Or a treat. Or maybe just a slow blink of respect. Their Lilith side is sacred and deserves reverence.
""",
"light_reflection_question": """
What’s one thing your pet refuses to do — no matter how much you try? And deep down, do you kind of love that about them?
"""
},
"soul_archetype_nickname": """
With Lilith in {black_moon_lilith_sign_name}, your {species} is a ‘{lilith_soul_archetype_nickname}’ —
fierce, fabulous, and never afraid to be unapologetically them.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "9",
"section_title": "Mysterious Pawprints & Lilith's Fire"
},
"transition_connector": "That fierce independence is part of their magic! Now, let's settle into the cozy comforts they've known all along, their soul's familiar sanctuary."
},
{
"section_id": "south_node",
"header_template": " {pet_name}'s Soulful Sanctuary: South Node Comforts in {south_node_sign_name}",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: observational, sweet, cheeky, gently familiar)
You know that one super endearing (or maybe slightly baffling?) thing {pet_name} has always done? That signature move, that go-to comfort habit, that little quirk that's just so… them? That's the sweet whisper of their South Node! It’s like their soul's favorite, well-worn armchair – a place of deep comfort, natural talents, and all the things they already know by heart from way back when.
""",
"astrological_heart": """
(Mika’s Voice: Informative but warm — explain the South Node simply, focusing on innate gifts and comfort zones)
So, if the North Node is the exciting new trail {pet_name} is exploring, the South Node ☋ is their beloved home base, packed with all their favorite snacks and coziest blankets. It tells us about the talents and tendencies they were practically born with, their soul's 'been there, done that, got the comfy t-shirt' zone. With {pet_name}'s South Node in {south_node_sign_name}, they arrived in your life already pretty darn good at being {south_node_keyword_adj_1}.

They likely find an almost instinctual comfort in {south_node_keyword_noun_1},
and when they're just being their most natural self, they often operate {south_node_keyword_adv_1}.
These aren't lessons to learn, but lovely gifts they already possess!
""", 
"pet_specific_examples": """
(Mika’s Voice: Playful and practical — show how a pet with this sign’s South Node might display their innate comfort traits and talents)
You've no doubt seen these {south_node_sign_name} superpowers in action since day one with your {species}, {pet_name}! For instance:

    Did they ({south_node_example_1})

    Or maybe {pet_name} has always ({south_node_example_2})

    And isn't it just classic {pet_name} how they ({south_node_example_3})

That’s their {south_node_sign_name} South Node shining – their beautiful, built-in baseline of brilliance and what makes them so wonderfully, predictably them.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Invite a moment of appreciation or light praise for what they do best, reinforcing their innate talents)
Here’s a sweet little game: Today, when {pet_name} does that classic {south_node_keyword_adj_1} thing they do so well – you know, the one that makes you smile and think, 'Yep, that's my {pet_name}!' – give them an extra-special bit of praise or their absolute favorite kind of scratch. It's like a little high-five for their soul's signature move!
""",
"light_reflection_question": """
(Mika’s Voice: Prompt a fond memory or recent “aha!” moment — what's a quirk they've had since the beginning that you adore?)
What’s one of {pet_name}'s oldest, most familiar habits or quirks – something they've done since they were tiny – that still makes your heart do a little happy flip just because it's so uniquely them?
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Sweet, comfort-focused nickname that reflects their innate gifts – e.g., 'The Familiar Snuggler,' 'The Cozy Old Soul,' 'Chief Nap Repeater')
With their South Node in {south_node_sign_name}, {pet_name} is like your very own '{south_node_soul_archetype_nickname}'.
They've got this comforting thing down to a fine art, and it's a wonderful part of what makes them your special companion.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "10",
"section_title": "Soulful Sanctuary: South Node Comforts"
},
"transition_connector": "Those innate gifts are so special! Flowing from this, we’ll explore the very core of their energy – their elemental drives and instinctive quirks."
},
{
"section_id": "element_modality",
"header_template": " {pet_name}'s Elemental Drives & Instinctive Quirks", 
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Curious, insightful, with a playful "aha!" tone)
Ever wonder about {pet_name}'s basic operating system? You know, beyond the cute fluff and those irresistible {pet_sound}s? We're talking about their core 'get-up-and-go' versus 'let's-just-snuggle' settings, or whether they're more of a 'let's start a party!' type or a 'hmm, let me ponder this dust bunny' philosopher. That’s where their dominant element and modality come in – it’s like their secret recipe for being uniquely {pet_name}!
""",
"astrological_heart": """
(Mika’s Voice: Friendly, clear explanation of elements and modalities using fun metaphors)
Alright, so in the cosmic kitchen of personality, every pet gets a main elemental ingredient and a primary 'how-they-do-things' style, called a modality.
Your {pet_name}'s main elemental signature is {element_dominance_style_phrase}, which means their fundamental energy is ({element_modality_style_explanation}).

Then, there's their 'how-they-do-things' style, or modality, which is {dominant_modality}. This means they tend to ({element_modality_approach_explanation}).

So, when you put it all together, {pet_name} is essentially a {dominant_element} {dominant_modality} {species}! That's like being ({element_modality_combined_vibe_example}).
It's their core 'vibe'!
""", 
"pet_specific_examples": """
(Mika’s Voice: Playful and practical — show how this elemental/modality combo might appear in real life with 2-3 concrete, species-aware examples)
You’ve probably seen this unique {dominant_element}-{dominant_modality} blend in {pet_name} a thousand times! Like when:

    They ({element_modality_example_1})

    Or how about the way {pet_name} ({element_modality_example_2})

    And isn't it classic {pet_name} when they ({element_modality_example_3})

That’s their signature style – their elemental engine and their modality moves all rolled into one adorable package!
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Invite the guardian to observe their pet's core 'vibe' in action, encouraging a moment of appreciation)
Here’s a fun little observation game: Over the next day, try to spot {pet_name} in full {dominant_element}-{dominant_modality} mode. Is it their ({element_modality_short_dominant_element_behavior_example}) way of approaching snack time? Or their ({element_modality_short_dominant_modality_behavior_example}) reaction to a change in routine? Just noticing their innate style can be a lovely way to appreciate their unique operating system! No need to change a thing, just enjoy their natural flair.
""",
"light_reflection_question": """
(Mika’s Voice: Prompt a fond observation or an "aha!" moment about their pet's core way of being)
What's one classic {pet_name} move or quirk that, now that you think about it, perfectly captures their {dominant_element} energy combined with their {dominant_modality} approach to life?
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Sweet, empowering nickname that reflects their core energetic and behavioral style)
So, with that wonderful combo of {dominant_element} energy and a {dominant_modality} approach, {pet_name} is basically your own little '{element_modality_soul_archetype_nickname}'!
It’s what makes their engine purr (or woof, or chirp!).
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "11",
"section_title": "Elemental Drives & Instinctive Quirks"
},
"transition_connector": "Understanding their fundamental energy is like knowing their secret recipe! Now, let's see how the different 'flavors' in their cosmic makeup chat and play together."
},
{
"section_id": "aspects",
"header_template": " Celestial Playdates & Pawfect Alignments",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Excited, curious, like whispering a cosmic secret)
Okay, this part is super fun! Imagine your pet’s planets having a little paw-ty in the stars — some getting along like lifelong cuddle buddies, others maybe playfully stealing toys from each other. These little cosmic connections are called aspects, and they shape the quirky, sparkly mix of personality traits your pet shows every day.
""",
"astrological_heart": """
(Mika’s Voice: Friendly explainer, like a galactic tour guide)
In astrology, aspects are the angles between planets in the chart — they’re like conversations between different parts of your pet’s cosmic personality. Some aspects are smooth and supportive (like “You nap, I guard”), while others create a bit of tension (like “I want snacks now!” vs. “But also, chase that leaf!”).

These alignments explain your pet’s energetic balance — why they might be bold and cautious, clingy and independent, or silly and stoic. Think of them as the dynamic little dialogues that add delightful complexity to their soulprint!
""",
"pet_specific_examples": """
(Mika’s Voice: Observational, witty, based on aspect themes)
You might see these celestial combos in action if:

    {pet_name} {aspects_example_1}.

    They {aspects_example_2}.

    Or maybe they’re {aspects_example_3}.

These little interactions shape the delightful contradictions and superpowers that make your pet so lovable and so them.
""", 
"guardian_interaction": {
"try_this_for_fun": """
Next time your pet does something totally unexpectedly expected, ask yourself — “Which two parts of their personality just had a cosmic chat?” It’s a fun way to spot their inner alignment dance!
""",
"light_reflection_question": """
What’s a moment when your pet surprised you by being a perfect mix of two opposite qualities?
"""
},
"soul_archetype_nickname": """
With these powerful planetary alignments, your {species} is a true ‘{aspects_soul_archetype_nickname}’ —
part explorer, part sage, part sleepy muffin, part chaos gremlin. Every quirk is written in the stars!
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "12",
"section_title": "Celestial Playdates & Pawfect Alignments"
},
"transition_connector": "These cosmic conversations create such a unique blend! Next, we'll spotlight the main 'stars' of their personality show – their dominant zodiac signs."
},
{
"section_id": "dominant_combinations",
"header_template": " {pet_name}'s Star-Stamped Style: Dominant Signs & Standout Energy",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Playful, confident, like she’s letting the guardian in on a secret)
Okay, so every pet has a vibe, right? That thing you just know about them — like, “Yep, this little furball is clearly the boss of the house,” or “This sweetheart is basically made of marshmallows and moonlight.” That core personality flavor? That’s what we get from their dominant zodiac signs — the big, loud voices in their cosmic choir!
""",
"astrological_heart": """
(Mika’s Voice: Warm, informative, but with fun metaphors — spotlighting the top 1-2 most dominant signs from the chart)
Now, in {pet_name}’s birth chart, while all the zodiac signs play a part (yes, even mysterious Scorpio and party-loving Sagittarius), a couple of them really steal the show. These are their dominant signs — the signs with the most planetary action, energy, or weight in their chart. You could say they set the stage, write the script, and direct the zoomies.

For {pet_name}, the dominant flavor is clearly {dominant_sign_1}! This gives them a natural {dominant_sign_1_keyword_trait},
a tendency to {dominant_sign_1_short_behavioral_phrase},
and a vibe that’s often described as {dominant_sign_1_signature_feeling}.

And, sometimes, another sign likes to make a strong cameo! If {dominant_sign_2} is also playing a starring role, that adds a dash of {dominant_sign_2_keyword_trait},
especially when they’re {dominant_sign_2_contextual_behavior}.
It’s like their awesome backup personality comes online for special missions, like an extra-fluffy secret agent!
""", 
"pet_specific_examples": """
(Mika’s Voice: Grounded, observational — examples showing these dominant vibes in action)
You’ll spot this cosmic combo in action when:

    {pet_name} ({dominant_combo_example_1})

    Or when they ({dominant_combo_example_2})

    And don’t forget the time they ({dominant_combo_example_3})

These signs are like the headline acts in their personal zodiac concert, and oh boy, do they put on a show!
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Lighthearted invitation to spot these vibes in daily life)
Here’s a fun little game for your inner pet-ologist: Over the next day, keep an eye out for those signature {dominant_sign_1} (and maybe {dominant_sign_2}, if they're feeling showy!) moments. It could be the way {pet_name} demands dinner, masterminds a nap in the sunniest spot, or greets you like you've been gone for a year (even if it was just five minutes). Give 'em a little nod when you see it – 'Yep, that's your star-power shining!'
""",
"light_reflection_question": """
(Mika’s Voice: Heartfelt but casual — invites a smile of recognition)
What’s one hilariously adorable or undeniably powerful thing {pet_name} does that makes you go, “Oh, that is SO quintessentially {pet_name}!” Odds are, it’s one of those dominant signs taking center stage with fabulous flair.
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: A fun, nickname-y summary of their chart’s loudest traits — something brandable, memorable, adorable)
With their standout signs leading the cosmic parade, {pet_name} could easily be called your very own '{dominant_combo_soul_archetype_nickname}'.
It’s not just astrology — it’s their star-stamped, utterly unique signature style!
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "13",
"section_title": "Star-Stamped Style: Dominant Signs & Standout Energy"
},
"transition_connector": "That star-stamped style truly makes them shine! And speaking of stars, did you know they might have an extra sprinkle of ancient stardust in their chart? Let's find out!"
},
{
"section_id": "fixed_stars",
"header_template": " Starry Touches: A Bit of Extra Cosmic Sparkle",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Sparkly, clever, curious — this is a fun 'bonus fact')
Okay, this is one of my favorite parts to sniff out… Did you know {pet_name}'s chart has a little stardust sparkle from the ancient sky? That’s right — one of the brightest fixed stars was shining in just the right spot when they arrived (on {birth_date_formatted}, to be exact!), adding a dash of cosmic flair to their already delightful personality.
""", # --- PATCH 3: Example usage of birth_date_formatted ---
"astrological_heart": """
(Mika’s Voice: Brief, whimsical, mythic-tinged but grounded)
According to the star map, {pet_name} was born with {fixed_star_1_name} closely aligned to their {planet_or_point_fixed_star_1}. That star has a long-standing reputation for bringing traits like {fixed_star_1_traits}. In {pet_name}'s case, this might show up when they {fixed_star_1_brief_behavior_example},
like they’ve got a touch of celestial wisdom in their whiskers (or tail feathers).

{optional_fixed_star_2_prompt_text}
""", 
"optional_fixed_star_2_prompt_text": """
(Mika’s Voice: If there's a second one, keep it short and playful)
And as if that weren’t enough sparkle, {pet_name} also has a twinkle from {fixed_star_2_name} connected to their {planet_or_point_fixed_star_2}, suggesting a streak of {fixed_star_2_traits}. You might spot it when they {fixed_star_2_brief_behavior_example},
like a little superhero from the stars.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Fun, observational — a light stargazing moment)
Next time you're under a clear night sky, point up and whisper, 'You're literally made of stars, {pet_name}!' They may not understand, but trust me — they'll feel it. It’s a cosmic compliment!
""",
"light_reflection_question": """
(Mika’s Voice: Warm, prompting a smile)
Does {pet_name} ever do something that feels almost… mythic? Like a moment where you half expect theme music to swell? That might just be their starry signature shining through.
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Mythic sparkle with pet charm — short and fun)
With a fixed star like {fixed_star_1_name} in their corner, {pet_name} might just be your very own '{fixed_stars_soul_archetype_nickname}' —
a legendary companion in a lovable little body.
""" 
},
"meta": {
"tone_tier": "Tier 1.5: Pixar-Whimsy, Sparkle-Infused Bonus",
"section_number": "14",
"section_title": "Ancient Whispers: Starry Touches"
},
"transition_connector": "Those ancient starry whispers add such unique charm! Now, let’s zoom back in to see how the fundamental 'ingredients' of their personality pie are balanced."
},
{
"section_id": "element_balance",
"header_template": " Pawprint Pie: Your Elemental DNA",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Playful and bright, like she’s showing you a fun pie chart)
If {pet_name} were a cosmic pie (stick with me here), their personality would be baked with four magical ingredients: Fire, Earth, Air, and Water. Some pets have a balanced recipe, others are all-in on one flavor — like an all-cinnamon cookie with no chill! Either way, their elemental blend helps explain how they move, feel, think, and react in the world.
""",
"astrological_heart": """
(Mika’s Voice: Friendly, clear, with food or art metaphors for balance/imbalance)
In astrology, every sign belongs to one of the four elements:

    Fire = passion, energy, zoomies.

    Earth = groundedness, comfort, routines.

    Air = curiosity, communication, cleverness.

    Water = sensitivity, emotion, intuition.

In {pet_name}’s case, their elemental pie is {element_dominance_style_phrase}. That means they naturally lean toward a style that’s {element_1_description}, with hints of {element_2_description}.

If this were a recipe card, it might read:
Main Ingredient(s): {element_dominance_style_phrase}
Needs a dash of... {least_represented_element} (just for balance!)

This doesn’t mean anything’s missing — it just shows where they’re naturally strong and where they might act in funny, unexpected ways (like forgetting their tail exists until it moves and they panic).
""",
"pet_specific_examples": """
(Mika’s Voice: Grounded and humorous — connect elements to real behaviors)
You might spot this elemental flavor when:

    {pet_name} ({element_balance_example_dominant_fire})

    Or when they ({element_balance_example_earth_low_air})

    And that moment when they ({element_balance_example_mixed_low_water})

These elemental instincts shape how they interact with the world — and make them oh-so-them.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Light invitation to appreciate their elemental leanings)
Want to see their elemental balance in action? Watch how they react to a new thing this week — a toy, a noise, a guest. Is it full Fire enthusiasm? Earthy suspicion? Airy investigation? Watery emotion? Each reaction tells you something beautifully true about their elemental mix!
""",
"light_reflection_question": """
(Mika’s Voice: Reflective, but with a wink)
What’s one super typical {pet_name} move that makes you go, “Yep, that’s exactly their flavor!” — spicy? mellow? chatty? mysterious? It’s written in their elements.
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: A cute summary title that captures their flavor combo — ideal for fun display)
So with all this cosmic seasoning, {pet_name} is basically your '{element_balance_soul_archetype_nickname}' —
one-of-a-kind elemental recipe and all.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "15",
"section_title": "Pawprint Pie: Elemental Balance"
},
"transition_connector": "This blend of elemental energies makes them so unique! And as they navigate life with this special mix, they might also be munching on a few 'karma kibbles' – gentle life lessons from the stars."
},
{
"section_id": "karmic_lessons",
"header_template": " {pet_name}'s Karma Kibbles: Life Lessons from the Stars",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Thoughtful, warm, a little mischievous — sets up a gentle depth)
Okay, so stick with me for a sec — what if our pets aren’t just here for snacks, snuggles, and expert-level zoomies? What if they also come with a tiny backpack full of lessons, patterns, and soul-level 'stuff' they’re still figuring out? Nothing heavy or serious — just cosmic breadcrumbs they’re following. These are their karmic lessons, and believe it or not, they’re working on them right alongside you.
""",
"astrological_heart": """
(Mika’s Voice: Explains gently, using metaphors and lots of reassurance — karma = patterns, not punishment)
In astrology, we sometimes peek at certain chart placements to uncover a pet’s karmic patterns — traits or behaviors they may lean on a little too much, or lessons their spirit seems curious about learning in this lifetime (in their own goofy, snuggly way). It’s not about being 'wrong' — it’s more like a cosmic 'try this instead' nudge.

For {pet_name}, the chart suggests they’re here to explore some gentle growth around {karmic_theme_1} — which might show up as ({karmic_lessons_example_behavior_theme_1}).
They also seem to carry an old-soul familiarity with {karmic_pattern_2}, which sometimes turns into ({karmic_lessons_example_behavior_pattern_2}).
No judgment! These are just part of their beautiful pet-personality package, and they’re doing their best (usually with an adorable side-tilt).
""",
"pet_specific_examples": """
(Mika’s Voice: Insightful and compassionate — shows how the karmic themes might appear)
You might recognize these karmic themes when:

    {pet_name} ({karmic_lessons_example_1})

    Or perhaps they ({karmic_lessons_example_2})

    And don’t forget how they sometimes ({karmic_lessons_example_3})

These moments aren’t flaws — they’re just little cosmic clues about where they’re growing, healing, and shining in your shared life together.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Empathetic, light suggestion for how to support their growth)
Wanna be {pet_name}’s growth buddy? The next time they bump into one of these 'karma kibbles' moments — like needing a little extra help with patience, or comfort when they’re being clingy — just take a deep breath with them. Give them a smile, a touch, or a tiny 'you’re doing great' whisper. You’re not just training them — you’re soul-sidekicking.
""",
"light_reflection_question": """
(Mika’s Voice: Gentle nudge for the guardian to see the lesson with affection)
What’s one quirky thing {pet_name} does that sometimes drives you a bit bonkers… but also makes you love them even more? There’s probably a karmic thread hiding in there, wagging its tail.
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Sweet, empowering title that gives a loving nickname to their karmic path)
With their unique cosmic curriculum, {pet_name} is your very own '{karmic_lessons_soul_archetype_nickname}'.
Growing together is part of the magic.
""" 
},
"meta": {
"tone_tier": "Tier 1.5: Pixar-Reflective, Gentle Wisdom",
"section_number": "16",
"section_title": "Karma Kibbles: Soulful Growth & Starry Lessons"
},
"transition_connector": "Every little lesson is part of their journey. And speaking of life's essentials, let's explore how their cosmic wiring might influence their all-important snack and snooze preferences!"
},
{
"section_id": "snack_and_snooze",
"header_template": " {pet_name}'s Star-Powered Snack & Snooze Hacks",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Cozy, playful, like she’s revealing a comfy secret)
Let’s be real: snacks and naps are two of the great joys of life — especially for our furry (or feathered, or scaled) companions. But have you ever wondered why {pet_name} insists on napping in that one sunbeam at 2:14 PM sharp, or has such particular taste in treats? Turns out, the stars might have something to do with it!
""",
"astrological_heart": """
(Mika’s Voice: Friendly and practical — grounded in astrology but never preachy)
Depending on what’s dominant in {pet_name}’s chart, they might lean toward certain sensory preferences when it comes to food, rest, and comfort. Let’s break it down by elemental style:

    If they’ve got lots of Fire, they might need bursts of active play before truly relaxing — like zoomies before snoozies. They may love crunchy snacks that match their spicy energy!

    With a strong Earth vibe, comfort is king. Think soft textures, warm snuggle spots, and maybe a serious opinion on food presentation. These pets know their routines and expect excellence!

    Airy types? Always curious. They might graze, snack in stages, or snooze lightly in watchful spurts. They want variety and mental stimulation before full belly flops.

    Water babies are the moodiest napmasters. They might seek soothing sounds or hidey-holes to recharge and are often extra sensitive to how and where they eat.

We can’t promise they’ll stick to a meal plan (we see you, midnight fridge raiders), but their stars reveal a lot about their ideal snack-and-snooze environment.
""",
"pet_specific_examples": """
(Mika’s Voice: Witty and behavior-focused — give 2-3 fun species-aware examples)
You might notice this in action when:

    {pet_name} ({snack_snooze_example_fire})

    Or maybe they ({snack_snooze_example_earth})

    Or perhaps, ({snack_snooze_example_water})

Whatever their vibe, their chart helps explain these delightfully specific preferences.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Encourages a fun observation-based activity)
Want to treat {pet_name} like the star they are? Try tailoring their next snack or nap zone to match their chart flavor! Got a fiery goofball? Hide a treat and let them 'hunt' it first. More of a watery dreamer? Create a cozy, quiet den with a soft scent they love. It’s enrichment with cosmic flair!
""",
"light_reflection_question": """
(Mika’s Voice: Warm, quirky reflection question)
What’s one hilarious or oddly specific food or nap preference that makes you think {pet_name} might actually be running on a secret astrological meal plan?
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Sweet summary nickname reflecting their comfort style)
With their snack-and-snooze settings wired this way, {pet_name} is basically your own '{snack_snooze_soul_archetype_nickname}'.
Their preferences are part of their cosmic charm!
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "17",
"section_title": "Star-Powered Snack & Snooze Hacks"
},
"transition_connector": "Their cosmic comfort preferences are so telling! Now, let's see how their starry signature beautifully blends with the wonderful traits of their earthly heritage."
},
{
    "section_id": "breed_spotlight",
    "header_template": "{pet_name}'s Breed Spotlight: Quirks & Traits",
    "ai_prompt_parts": {
        "sparky_intro": "Every pet comes with their own charming quirks, but breed can sometimes offer clues to the traits written in their DNA. Whether it's the loyal woof of a Labrador or the clever chitter of a parrot, this is where we zoom in on what makes your companion unique.\n\nLet’s see what cosmic echoes shine through {pet_name}’s breed identity. [AI Expansion Point]",
        "astrological_heart": "This pet’s breed brings traits like {breed_behavior_keywords}, layered beautifully with their birth chart’s cosmic flavor. Celebrate their quirks without stereotyping — blend breed insight with astrological nuance.", # PATCH 9 Change
        "pet_specific_examples": "Include fun, personalized traits, e.g. “Mika’s breed is known for their gentle loyalty—but her chart reveals an extra dash of stubborn sparkle from that Moon in Taurus!”",
        "guardian_interaction": "Invite the reader to reflect on how these traits show up. Prompt: 'Do you recognize any of these traits in {pet_name}? Or has your pet surprised you with their own twist on cosmic tradition?'",
        "soul_archetype_nickname": "Nickname this section something like 'The Cosmic Breedprint' or 'Star-etched Species Sparkle'. Keep it warm and engaging."
    },
    "meta": {
        "section_number": "18",
        "section_title": "Breed Spotlight: Quirks & Traits",
        "divider_tag": "breed_spotlight",
        "voice_tone": "Pixar-Warm, Clever, Charming, Grounded"
    },
    "transition_connector": "What a fabulous blend of breed and stars! To wrap up our cosmic journey, let's gather some final loving tips on how to best support your unique little star."
},
{
"section_id": "companion_care",
"header_template": " {pet_name}'s Cosmic Companion Care & Paw-thority Settings",
"ai_prompt_parts": {
"sparky_intro": """
(Mika’s Voice: Warm and reassuring, like she’s putting a cozy blanket around the guardian’s shoulders)
Alright, {pet_name} has dazzled us with zodiac sparkle, planetary quirks, and a whole galaxy of personality. But now, let’s bring it down to earth — or better yet, into your lap. This section is your lovingly crafted ‘care and handling’ guide from the stars, based on {pet_name}’s chart. It’s all about the little things that make a big difference — how to help them shine, relax, and feel deeply understood in your shared life.
""",
"astrological_heart": """
(Mika’s Voice: Thoughtful, compassionate, and grounding — weaving together emotional care, environment, communication style, and pet-guardian bonding tips)
So, what makes {pet_name} tick and tock in harmony? Their chart tells us a lot! For instance, with a Moon in {moon_sign_name}, they might feel most at ease when {companion_care_moon_emotional_need}.
Their Rising Sign in {rising_sign_name} suggests they tend to approach life with a {companion_care_rising_expression_style} —
so letting them {companion_care_rising_social_tip} makes them feel respected.

Their dominant elemental nature, being {element_dominance_style_phrase}, means they might naturally gravitate toward {companion_care_elemental_style_care}.
And their Sun in {sun_sign_name}? That’s their joy-center — the place where they shine when celebrated for being {companion_care_sun_self_image_nurture}.

Think of this as their "paw-thority panel" — a gentle interface between their stardust wiring and your everyday care. Nothing fancy required — just tuning into their natural rhythms and honoring the little cosmic hints they offer.
""", 
"pet_specific_examples": """
(Mika’s Voice: Practical and grounded — showing what care really looks like for this pet)
So how does this cosmic care look in the real world?

    If you’ve noticed that {pet_name} ({companion_care_example_1}),
    it’s probably their {dominant_element} needs gently saying, ‘thank you for syncing with me!’

    Or maybe they ({companion_care_example_2}) —
    that’s their {moon_sign_name} Moon setting the mood menu!

    And have you seen the way they ({companion_care_example_3})?
    Their {sun_sign_name} Sun loves a gold star moment!

They’re giving you cues all the time — and just by noticing, you’re already speaking their cosmic language.
""", 
"guardian_interaction": {
"try_this_for_fun": """
(Mika’s Voice: Gentle call to observation and encouragement, reinforcing the relationship)
Try this: Pick one moment in the day — mealtime, walk-time, bedtime — and do it 5% more tuned into {pet_name}'s chart energy. Is it slower, cozier, sillier, or more focused? See how they respond. Sometimes a tiny shift makes a world of difference!
""",
"light_reflection_question": """
(Mika’s Voice: Sweet and reflective, inviting guardian warmth)
What’s one small ritual or habit you and {pet_name} already share that seems to ‘just work’ — a natural flow between you two that feels easy, loving, and right? That’s likely you syncing with their chart, even without knowing it!
"""
},
"soul_archetype_nickname": """
(Mika’s Voice: Affirming and appreciative — the final cosmic nickname celebrating their needs and the guardian’s role)
With all this in mind, {pet_name} isn’t just your furry (or feathered, or scaled!) friend — they’re your cosmic co-pilot, your '{companion_care_soul_archetype_nickname}'.
You’re not just giving care — you’re sharing stardust love.
""" 
},
"meta": {
"tone_tier": "Tier 1: Pixar-Warm, Clever, Charming, Grounded",
"section_number": "19", # Adjusted section number
"section_title": "Cosmic Companion Care & Paw-thority Settings"
},
"transition_connector": None
}
]

# Defines the standard report layout sequence.
SECTION_LAYOUT_PRESETS = PET_PROMPTS
# Source of all prompt definitions for report generation.
SECTIONS_FOR_PET_REPORT = PET_PROMPTS
#--- END OF FILE prompt_definitions_pet.py ---