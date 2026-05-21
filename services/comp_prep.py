"""Competition preparation guides — structured data + Streamlit renderer."""
import streamlit as st

# ── Data ──────────────────────────────────────────────────────────────────────
# Each entry: name, icon, subject, tagline, overview, format_rows, timeline,
#             topics, resources, seek, weekly_plan, grade_goal, tips

COMPS: dict[str, list[dict]] = {

    # ══════════════════════════════════════════════════════════════════════════
    "grade_6": [
        {
            "name": "MATHCOUNTS",
            "icon": "🔢",
            "subject": "Math",
            "color": "#1d4ed8",
            "bg": "#eff6ff",
            "border": "#bfdbfe",
            "tagline": "The premier US middle-school math competition — build your foundation now",
            "overview": (
                "MATHCOUNTS is the most prestigious middle-school math competition in the US. "
                "It runs School → Chapter → State → National. "
                "Four rounds test speed, accuracy and creative problem-solving across all core math topics. "
                "Strong performance at Chapter or State is a significant academic achievement that shows up "
                "through high school and into college applications."
            ),
            "format_rows": [
                ("Sprint Round",    "30 questions · 40 min · individual · no calculator",             "Tests speed and breadth across all topics"),
                ("Target Round",    "8 pairs of 2 questions · 6 min/pair · individual · no calculator","Tests depth — read carefully, show work"),
                ("Team Round",      "10 questions · 20 min · team of 4 · no calculator",              "Collaboration + division of labor"),
                ("Countdown Round", "Oral head-to-head · top 10 competitors",                         "Speed recall — bonus at nationals"),
            ],
            "timeline": [
                ("Sep",      "School signs up; math teacher registers team"),
                ("Oct–Nov",  "Work through official MATHCOUNTS School Handbook (free download)"),
                ("Dec–Jan",  "Full timed Sprint + Target practice; join or form a study group"),
                ("Jan–Feb",  "School Competition — top 4 advance to Chapter"),
                ("Feb–Mar",  "Chapter Competition — top ~30% advance to State"),
                ("Mar",      "State Competition — top 4 advance to National"),
                ("May",      "National Competition (Washington DC) — for the very elite"),
            ],
            "topics": [
                "Number Theory — divisibility, primes, LCM/GCF, modular arithmetic",
                "Algebra — linear equations, sequences, inequalities, word problems",
                "Geometry — area, perimeter, angles, Pythagorean theorem, coordinate geometry",
                "Counting & Probability — permutations, combinations, basic probability",
                "Proportional Reasoning — ratios, rates, percents, unit conversion",
            ],
            "resources": [
                {"name": "MATHCOUNTS School Handbook",     "url": "https://www.mathcounts.org/resources/find-problems",   "type": "Free",    "desc": "Official problem sets — download at the start of the year"},
                {"name": "Art of Problem Solving (AoPS)",  "url": "https://artofproblemsolving.com/alcumus",              "type": "Free",    "desc": "Alcumus adaptive practice platform — set to MATHCOUNTS level"},
                {"name": "AoPS MATHCOUNTS Prep Books",     "url": "https://artofproblemsolving.com/store",                "type": "Paid",    "desc": "Competition Math for Middle School + MATHCOUNTS prep volumes"},
                {"name": "Past MATHCOUNTS Tests",          "url": "https://www.mathcounts.org/resources/past-competitions","type": "Free",    "desc": "Official archive — practice under timed conditions"},
                {"name": "Khan Academy",                   "url": "https://www.khanacademy.org",                          "type": "Free",    "desc": "Fill gaps in algebra and geometry foundations"},
                {"name": "mathisvisual.com",               "url": "https://www.mathisvisual.com",                         "type": "Free",    "desc": "Visual number theory and counting — great for conceptual clarity"},
            ],
            "seek": [
                ("🏫 Math Teacher", "Ask them to register the school team and form a MATHCOUNTS club (meets weekly)"),
                ("📚 AoPS Forums",  "artofproblemsolving.com/community — post problems, read solutions, find study partners"),
                ("👦 Older Students", "High schoolers who competed in MATHCOUNTS are often happy to coach"),
                ("🏢 Local Math Circle", "Many cities have free weekend math circles — search 'Dallas Fort Worth math circle'"),
            ],
            "weekly_plan": [
                ("Mon",  "30 min Sprint practice — 15 problems timed"),
                ("Tue",  "2 Target pairs — focus on showing work clearly"),
                ("Wed",  "30 min Sprint practice — next 15 problems"),
                ("Thu",  "2 Target pairs + review errors from the week"),
                ("Fri",  "1 Team round with classmates (or solo, timed)"),
                ("Sat",  "1 hr AoPS Alcumus — focus on weakest topic area"),
                ("Sun",  "Rest or optional: read AoPS textbook (15–20 min)"),
            ],
            "grade_goal": "Score in the top 10 at your school competition. Qualify for Chapter round. "
                          "Aim for 20+ on Sprint round by end of the year.",
            "tips": [
                "Start with the official School Handbook in October — do every problem",
                "Review every wrong answer — understanding WHY is more valuable than drilling volume",
                "Learn the 'MATHCOUNTS shortcuts': quickly computing squares, cube roots, fractions",
                "In Sprint, skip hard problems and come back — don't lose time on one problem",
                "For Target: read both problems first, the second sometimes simplifies the first",
            ],
        },

        {
            "name": "AMC 8",
            "icon": "📐",
            "subject": "Math",
            "color": "#7c3aed",
            "bg": "#f5f3ff",
            "border": "#ddd6fe",
            "tagline": "The national math benchmark for middle schoolers — feeds into the AMC → AIME pipeline",
            "overview": (
                "The AMC 8 is a 25-question multiple-choice exam held every November. "
                "Hosted by the Mathematical Association of America (MAA), it's the entry point to "
                "the AMC 10 → AMC 12 → AIME → USAJMO competition ladder that top colleges watch closely. "
                "No penalty for wrong answers. Honor Roll = top 5%, Distinguished Honor Roll = top 1%."
            ),
            "format_rows": [
                ("Format",    "25 multiple-choice questions · 5 answer choices each",   "40 min total"),
                ("Scoring",   "1 pt per correct · 0 for blank or wrong",                 "Max score = 25"),
                ("Tiers",     "Distinguished Honor Roll = 21+ · Honor Roll = 18+",       "Certificate of Achievement = 15+"),
                ("Where",     "Taken at school — teacher registers",                     "Free to take"),
            ],
            "timeline": [
                ("Aug–Sep",  "Review fundamentals: fractions, percentages, basic geometry"),
                ("Oct",      "Solve 3 full past AMC 8 papers under timed conditions (40 min each)"),
                ("Oct",      "Review all wrong answers with solutions (MAA publishes official solutions)"),
                ("Nov",      "Take the actual AMC 8 exam at school"),
                ("Dec",      "Review results, identify weak areas for next year"),
            ],
            "topics": [
                "Arithmetic — fractions, decimals, percents, ratios, proportions",
                "Basic Algebra — simple equations, patterns, sequences",
                "Geometry — area, perimeter, angles, basic coordinate geometry",
                "Number Theory — factors, multiples, prime factorization, divisibility",
                "Statistics & Probability — mean/median/mode, simple probability",
                "Counting — basic combinations, pigeonhole, Venn diagrams",
            ],
            "resources": [
                {"name": "Official Past AMC 8 Tests",      "url": "https://maa.org/math-competitions",           "type": "Free",  "desc": "All past papers + official solutions — primary study material"},
                {"name": "AoPS AMC 8 Wiki",                "url": "https://artofproblemsolving.com/wiki/index.php/AMC_8","type": "Free", "desc": "Problem-by-problem solutions with multiple approaches"},
                {"name": "AoPS Alcumus",                   "url": "https://artofproblemsolving.com/alcumus",     "type": "Free",  "desc": "Set difficulty to AMC 8 — adaptive practice by topic"},
                {"name": "AMC 8 Problem Series (YouTube)", "url": "https://www.youtube.com/results?search_query=AMC+8+solutions", "type": "Free", "desc": "Search 'AMC 8 2023 solutions' — WhyMath and others explain step-by-step"},
            ],
            "seek": [
                ("🏫 Math Teacher", "Ask them to register the school for AMC 8 (free). Many FISD schools participate."),
                ("📚 AoPS Community", "Post specific problems you're stuck on — the forum is very welcoming to beginners"),
                ("🤝 Study Group",  "Form a 3–4 person group and review past tests together once a week"),
            ],
            "weekly_plan": [
                ("Mon",  "10 AMC 8 problems (choose from past papers by topic)"),
                ("Wed",  "10 AMC 8 problems from a different year"),
                ("Fri",  "Review all errors from Mon + Wed — understand each solution"),
                ("Oct",  "One full 40-min timed test per weekend"),
            ],
            "grade_goal": "Score 15–18 in Grade 6 (solid first-attempt benchmark). "
                          "Focus on learning the format and identifying your weak topics rather than score.",
            "tips": [
                "Do problems 1–15 carefully first — they are progressively harder; 16–25 can be tricky",
                "Draw diagrams for every geometry problem — even rough sketches help enormously",
                "Learn 'elimination': for some problems, ruling out 3 choices is faster than solving",
                "Review official MAA solutions even for problems you got right — there are often shortcuts",
                "The last 5 problems (21–25) often need a creative insight — don't guess wildly; skip and return",
            ],
        },

        {
            "name": "MOEMS",
            "icon": "🧮",
            "subject": "Math",
            "color": "#059669",
            "bg": "#f0fdf4",
            "border": "#bbf7d0",
            "tagline": "Monthly open-ended math contests — perfect low-pressure entry for Grade 6",
            "overview": (
                "MOEMS (Math Olympiad for Elementary and Middle Schools) runs 5 monthly contests "
                "from November through March. Each contest has 5 open-ended (non-multiple-choice) "
                "problems to be solved in 30 minutes. "
                "It's a school-based program — the math teacher registers the team (up to 35 students). "
                "Awards: Gold, Silver, Bronze patches. Great habit-builder for AMC/MATHCOUNTS."
            ),
            "format_rows": [
                ("Contests",   "5 monthly contests: Nov, Dec, Jan, Feb, Mar",             "30 min · 5 problems each"),
                ("Format",     "Open-ended answers — no multiple choice",                  "No calculator"),
                ("Scoring",    "1 pt per correct answer · max 25 for the year",            "Patches: Gold 18+, Silver 15+, Bronze 10+"),
                ("Team size",  "Up to 35 students per school",                             "Individual scores + team total"),
            ],
            "timeline": [
                ("Oct",      "Math teacher registers school team at moems.org"),
                ("Nov–Mar",  "One contest per month — held in class, 30 min"),
                ("Apr",      "Awards announced — Gold/Silver/Bronze patches mailed"),
            ],
            "topics": [
                "Arithmetic and number sense at above-grade level",
                "Basic algebra and equation solving",
                "Geometry — area, perimeter, angles",
                "Counting and simple combinatorics",
                "Logic and pattern recognition",
            ],
            "resources": [
                {"name": "MOEMS Official Books",         "url": "https://www.moems.org/books.htm",          "type": "Paid",  "desc": "'Olympiad Problems for Elementary and Middle Schools' Vol 1 & 2 — core prep books"},
                {"name": "Past MOEMS Problems",          "url": "https://www.moems.org/sample.htm",         "type": "Free",  "desc": "Sample problems on official site"},
                {"name": "AoPS MOEMS Forum",             "url": "https://artofproblemsolving.com/community","type": "Free",  "desc": "Search for MOEMS problems and solutions in the forum"},
            ],
            "seek": [
                ("🏫 Math Teacher", "Ask them to register the school — it's easy and free for the students"),
                ("📖 Buy the Books","MOEMS Vol 1 & 2 are the best prep material; available on Amazon (~$20 each)"),
            ],
            "weekly_plan": [
                ("Twice/week", "Solve 3–5 MOEMS-level problems from past years or the official books"),
                ("Contest day","30 min, pencil only, show all work — practice good habits from the start"),
            ],
            "grade_goal": "Score 15+/25 across the year (average 3/5 per contest). "
                          "Gold patch is achievable with consistent practice.",
            "tips": [
                "Show all work — open-ended format means partial credit exists for some problems",
                "Read each problem twice before writing anything",
                "MOEMS problems are harder than school math but easier than MATHCOUNTS — great stepping stone",
            ],
        },

        {
            "name": "Science Olympiad",
            "icon": "🔬",
            "subject": "Science",
            "color": "#0891b2",
            "bg": "#ecfeff",
            "border": "#a5f3fc",
            "tagline": "The premier team science competition — join as a trial in Grade 6",
            "overview": (
                "Science Olympiad is a team competition with 23 events spanning biology, chemistry, "
                "physics, earth science and engineering. A team of 15 competes together. "
                "Each student specializes in 5–7 events, studying deeply over several months. "
                "It's one of the most recognized STEM competitions in the US — "
                "colleges view consistent Science Olympiad participation as a strong signal. "
                "Grade 6 goal: join the school team (or an invitational team) and try it out."
            ),
            "format_rows": [
                ("Team",      "15 members per team",                                        "Each member does 5–7 events"),
                ("Events",    "23 events per tournament across all science disciplines",    "Usually 2 members per event"),
                ("Levels",    "Invitational (practice) → Regional → State → National",     "Invitationals are open and unofficial"),
                ("Format",    "Mix of: written test, lab practicum, build event (engineering)", "Time-limited per event (20–30 min)"),
            ],
            "timeline": [
                ("Sep",      "Try out for school team — talk to science teacher/team coach"),
                ("Sep–Nov",  "Study your 5–7 events; attend team practice sessions"),
                ("Nov–Jan",  "Invitational tournaments — great low-stakes practice"),
                ("Feb–Mar",  "Regional competition — counts for State qualification"),
                ("Mar–Apr",  "State competition"),
                ("May",      "National tournament (top teams from each state)"),
            ],
            "topics": [
                "Life Science — Anatomy & Physiology, Disease Detectives, Experimental Design",
                "Earth & Space — Dynamic Planet, Fossils, Astronomy, Meteorology",
                "Physical Science — Chemistry Lab, Optics, Circuit Lab, Sounds of Music",
                "Engineering — Bridge Building, Boomilever, Wright Stuff (balsa plane), Scrambler",
                "Technology — Science Concepts, Codebusters (cryptography)",
            ],
            "resources": [
                {"name": "scioly.org Tests Database",        "url": "https://scioly.org/tests",                    "type": "Free",  "desc": "Huge archive of past invitational + official tests for every event"},
                {"name": "scioly.org Wiki",                  "url": "https://scioly.org/wiki",                     "type": "Free",  "desc": "Event-by-event study guides with recommended resources"},
                {"name": "Science Olympiad Official Site",   "url": "https://www.soinc.org",                       "type": "Free",  "desc": "Official rules, event descriptions, and resources"},
                {"name": "Scioly Exchange Discord",          "url": "https://discord.gg/scioly",                   "type": "Free",  "desc": "Active community — ask questions, find invitational schedules"},
            ],
            "seek": [
                ("🏫 Science Teacher", "Ask about the school Science Olympiad team and how to try out"),
                ("👩‍🔬 Team Captain",  "Senior team members usually mentor new students on their events"),
                ("💬 scioly.org Forum","Event-specific questions answered by experienced competitors nationwide"),
            ],
            "weekly_plan": [
                ("Mon",  "Study Event 1 (30 min) — read notes + flashcards"),
                ("Tue",  "Study Event 2 (30 min)"),
                ("Wed",  "Practice past test for Event 1 (timed)"),
                ("Thu",  "Practice past test for Event 2 (timed)"),
                ("Fri",  "Team practice at school"),
                ("Sat",  "Engineering build event (bridge, plane) — hands-on"),
            ],
            "grade_goal": "Join the school team. Participate in 1–2 invitationals. "
                          "Choose 2–3 events you enjoy and start building depth for Grade 7.",
            "tips": [
                "Pick events that match your strengths: love biology? → Anatomy/Disease Detectives; love building? → Bridge/Wright Stuff",
                "Invitationals in Jan–Feb are your best learning ground — treat them as free practice",
                "Study in pairs for your events — teaching your partner cements your own knowledge",
                "scioly.org/tests has past tests for every event — the single best prep resource",
            ],
        },

        {
            "name": "Gavel Club Speech Contests",
            "icon": "🎤",
            "subject": "Speech",
            "color": "#dc2626",
            "bg": "#fef2f2",
            "border": "#fecaca",
            "tagline": "Turn Gavel Club meetings into contest wins — Club → Area → Division → District",
            "overview": (
                "You're already a Gavel Club member — Toastmasters' youth program for ages 12–17. "
                "Gavel Club runs formal speech contests at 4 levels: Club, Area, Division, and District. "
                "Events include: Prepared Speech (5–7 min), Table Topics (2 min impromptu), "
                "Evaluation Contest, and Humorous Speech Contest. "
                "Grade 6 goal: deliver your first 2 Pathways speeches and enter the Club Table Topics contest."
            ),
            "format_rows": [
                ("Prepared Speech",    "Memorized speech, 5–7 min, from Pathways program",  "Evaluated on structure, delivery, language"),
                ("Table Topics",       "Impromptu response, 1–2 min, on a random topic",    "Evaluated on coherence, confidence, content"),
                ("Evaluation Contest", "Evaluate another speaker's prepared speech in 2 min","Tests listening + constructive feedback skills"),
                ("Humorous Speech",    "Original funny speech, 5–7 min",                    "Evaluated on comedic timing + message"),
            ],
            "timeline": [
                ("Sep",      "Re-join club at school year start; pick your first Pathways project"),
                ("Oct–Nov",  "Deliver 2 prepared speeches at club meetings"),
                ("Nov–Jan",  "Club Table Topics contest — enter and compete"),
                ("Feb–Mar",  "Club Prepared Speech contest — enter if eligible"),
                ("Apr",      "Area contest (if won at club level)"),
            ],
            "topics": [
                "Speech structure — opening hook, 3 main points, strong close",
                "Vocal variety — volume, pitch, pace, pause",
                "Body language — eye contact, gestures, posture, movement",
                "Impromptu speaking — PREP (Point, Reason, Example, Point) framework",
                "Storytelling — setting scene, conflict, resolution, emotional connection",
            ],
            "resources": [
                {"name": "Toastmasters Pathways (Online)",  "url": "https://www.toastmasters.org/pathways",            "type": "Free*","desc": "The structured project-based speaking curriculum — your roadmap"},
                {"name": "Toastmasters YouTube Channel",    "url": "https://www.youtube.com/toastmasters",             "type": "Free", "desc": "Watch World Champion speeches for inspiration and technique"},
                {"name": "TED Talks for Teens",             "url": "https://www.ted.com/playlists/86/talks_for_when_you_re_a_te", "type": "Free", "desc": "Study how great speakers structure and deliver ideas"},
                {"name": "Gavel Club Manual",               "url": "https://www.toastmasters.org/Resources/Gavel-Clubs","type": "Free", "desc": "Youth-specific resources and competition rules"},
            ],
            "seek": [
                ("🏫 Faculty Advisor",  "Your Gavel Club advisor runs the meetings and can nominate you for contests"),
                ("🗣️ Club Mentor",      "Every Gavel Club pairs new members with a mentor — leverage them"),
                ("📺 Video Study",      "Record yourself speaking on your phone — watch it back to identify habits"),
            ],
            "weekly_plan": [
                ("Daily",  "Practice Table Topics: pick a random topic from a jar and speak for 90 sec in front of a mirror"),
                ("Weekly", "Attend Gavel Club meeting — listen actively, evaluate one speaker"),
                ("Monthly","Prepare + deliver one full Pathways speech project"),
            ],
            "grade_goal": "Complete 3 Pathways speech projects. Place in Club-level Table Topics or Prepared Speech contest.",
            "tips": [
                "Strong openings win contests — memorize your first 30 seconds perfectly",
                "For Table Topics: don't start with 'Um'. Take one breath, begin with your point",
                "Record every speech on your phone — watching yourself is the fastest improvement tool",
                "Study the World Champion speeches on YouTube — notice how they use pauses and storytelling",
                "You already have an advantage: regular club practice builds confidence that solo studiers lack",
            ],
        },

        {
            "name": "UIL Academic Events",
            "icon": "🏅",
            "subject": "Multiple",
            "color": "#b45309",
            "bg": "#fffbeb",
            "border": "#fde68a",
            "tagline": "Texas-wide academic competitions in 10+ subjects — every FISD school participates",
            "overview": (
                "UIL (University Interscholastic League) runs academic competitions for Texas students "
                "at School → District → Regional → State level every spring. "
                "FISD middle schools participate in most events. "
                "Grade 6 focus: Number Sense, Spelling & Vocabulary, and Oral Reading — "
                "these align best with current skills and are good entry points."
            ),
            "format_rows": [
                ("Number Sense",      "80 mental-math problems · 10 min · no calculator",         "Speed + trick shortcuts are key"),
                ("Spelling & Vocab",  "Written spelling + oral bee rounds",                        "300-word study list + vocabulary in context"),
                ("Oral Reading",      "Sight-read an unfamiliar passage aloud · expression judged","Natural phrasing + voice control"),
                ("Maps/Graphs/Charts","Interpret maps, charts, and data · 45 questions · 30 min", "Strong overlap with math and geography"),
            ],
            "timeline": [
                ("Sep–Jan",  "Study and practice independently or with UIL coordinator at school"),
                ("Jan–Feb",  "School practice meet (informal)"),
                ("Feb–Mar",  "District competition — top 3 advance to Regional"),
                ("Apr",      "Regional competition — top 3 advance to State"),
                ("May",      "State competition (University of Texas, Austin)"),
            ],
            "topics": [
                "Number Sense: multiplication tricks (11s, 12s, squares), fraction ↔ decimal shortcuts, divisibility rules",
                "Spelling: UIL official word list (posted annually), Latin/Greek roots for vocabulary section",
                "Oral Reading: phrasing at punctuation, expression for emotion, maintain pace",
                "Maps/Charts: map scales, legend reading, bar/line/pie chart interpretation, latitude/longitude",
            ],
            "resources": [
                {"name": "UIL Academics Official Site",    "url": "https://www.uiltexas.org/academics",              "type": "Free", "desc": "Official practice materials, past tests, and rules for every event"},
                {"name": "UIL Number Sense Tricks",        "url": "https://www.uiltexas.org/academics/math",          "type": "Free", "desc": "Official Number Sense study tips and past tests"},
                {"name": "UIL Spelling Word List",         "url": "https://www.uiltexas.org/academics/language",      "type": "Free", "desc": "Official annual word list + vocabulary study guide"},
            ],
            "seek": [
                ("🏫 UIL Coordinator",  "Every FISD school has a UIL Academic Coordinator — ask in the main office"),
                ("📋 Subject Teacher",  "Math teacher for Number Sense, ELA teacher for Spelling/Oral Reading"),
                ("👥 Practice Group",   "Form a small group with classmates — quiz each other on spelling and Number Sense"),
            ],
            "weekly_plan": [
                ("Daily 10 min",  "Number Sense: speed drills (multiplication tables, squares, fraction conversions)"),
                ("Mon/Wed",       "Spelling: review 20 words from UIL list, write each 3 times"),
                ("Tue/Thu",       "Oral Reading: read 2 paragraphs from a book aloud, record and playback"),
                ("Fri",           "Full practice test for one UIL event under timed conditions"),
            ],
            "grade_goal": "Participate in 2–3 events. Qualify for District in at least one. "
                          "Number Sense is the highest-impact event to build early.",
            "tips": [
                "Number Sense shortcuts are learnable — the UIL Number Sense manual has all the tricks",
                "For Spelling: focus on Latin/Greek roots (port = carry, dict = speak) — unlocks dozens of words",
                "Oral Reading judges reward natural expression over performance — read like you're telling a story",
                "UIL State participants from Grade 6 are very rare — District qualifier is an excellent target",
            ],
        },

        {
            "name": "Scholastic Art & Writing Awards",
            "icon": "✍️",
            "subject": "Writing",
            "color": "#9333ea",
            "bg": "#fdf4ff",
            "border": "#e9d5ff",
            "tagline": "The most prestigious national writing recognition for students — start in Grade 6",
            "overview": (
                "The Scholastic Art & Writing Awards is the nation's longest-running and most prestigious "
                "recognition program for creative students (since 1923). "
                "Students submit original work to regional judges; Gold Key winners advance to national review. "
                "Past alumni include Truman Capote, Sylvia Plath, Stephen King, Joyce Carol Oates. "
                "Grade 6 goal: complete one strong piece and submit — the habit of writing for an audience starts here."
            ),
            "format_rows": [
                ("Submission",  "Submit via regional affiliate (Texas: scholastic.com/artandwriting)",  "Online submission portal"),
                ("Categories",  "Short Story, Flash Fiction, Personal Essay, Poetry, Journalism, Humor", "Choose your strongest format"),
                ("Awards",      "Gold Key → National review · Silver Key · Honorable Mention",           "Regional results in Feb"),
                ("Limits",      "Short Story ≤ 2500 words · Flash Fiction ≤ 1000 words · Poetry ≤ 60 lines", "Personal Essay ≤ 1000 words"),
            ],
            "timeline": [
                ("Jun–Aug",  "Write a first draft of your piece over the summer — longer timeline = better work"),
                ("Sep–Oct",  "Revise with teacher or writing group feedback"),
                ("Nov",      "Final polish — proofread at least 3 times"),
                ("Dec",      "Submit via regional portal (typical deadline: Dec–Jan, confirm annually)"),
                ("Feb",      "Results announced — Gold/Silver Key or Honorable Mention"),
                ("Mar–Apr",  "Gold Key pieces sent to National judges"),
            ],
            "topics": [
                "Personal Essay: a specific moment that changed how you see the world — concrete + reflective",
                "Short Story: character + conflict + resolution — avoid clichés (dragons, chosen one)",
                "Flash Fiction: one sharp scene with a surprising turn or image",
                "Poetry: specific imagery over abstract feelings — show don't tell",
            ],
            "resources": [
                {"name": "Scholastic Art & Writing Submission Portal", "url": "https://www.artandwriting.org", "type": "Free", "desc": "Main submission site — also browse award-winning past work for inspiration"},
                {"name": "The Best American Short Stories (library)", "url": "https://www.amazon.com",         "type": "Library","desc": "Read 3–5 award-winning short stories to study structure and voice"},
                {"name": "Reedsy Short Story Writing Guide",          "url": "https://blog.reedsy.com/how-to-write-a-short-story/", "type": "Free", "desc": "Practical breakdown of story structure for beginners"},
            ],
            "seek": [
                ("🏫 ELA Teacher",        "Ask your English teacher to read your draft and give feedback — they've often seen winners"),
                ("📚 School Library",     "Ask librarian for past Scholastic award collections — reading winners is the best prep"),
                ("✏️ Writing Club",       "If the school has a creative writing club, join — peer feedback is invaluable"),
            ],
            "weekly_plan": [
                ("Summer",    "Write 500 words / day for 2 weeks — quantity first, quality later"),
                ("Sep–Oct",   "One revision session per week with a specific focus (dialogue, opening, ending)"),
                ("Nov",       "Final proofreading pass — read aloud to catch awkward sentences"),
            ],
            "grade_goal": "Submit one polished piece. Aim for Honorable Mention or Silver Key in your first year. "
                          "Gold Key is achievable — hundreds of Grade 6 students win nationally each year.",
            "tips": [
                "Specific details beat vague descriptions every time: 'a chipped blue mug' beats 'a cup'",
                "Read the award-winning pieces on artandwriting.org — notice what they have in common",
                "Your personal essay topic does NOT need to be dramatic — small moments written beautifully win",
                "Start writing in June — rushed November pieces rarely win",
                "Proofread by reading your piece backwards (last sentence first) to catch grammar errors",
            ],
        },
    ],

    # ══════════════════════════════════════════════════════════════════════════
    "grade_7": [
        {
            "name": "MATHCOUNTS",
            "icon": "🔢",
            "subject": "Math",
            "color": "#1d4ed8",
            "bg": "#eff6ff",
            "border": "#bfdbfe",
            "tagline": "Grade 7: serious training year — target Chapter qualification and top Chapter placement",
            "overview": (
                "Grade 7 is when MATHCOUNTS preparation becomes serious. "
                "Your Grade 6 experience gave you the format and foundation. "
                "Now the goal shifts to deep topic mastery, Sprint speed, and Target accuracy "
                "to qualify for State via Chapter. "
                "AoPS textbooks and Alcumus are your primary tools this year."
            ),
            "format_rows": [
                ("School",    "Top 4 individuals + 1 team advance to Chapter",       "Usually January–February"),
                ("Chapter",   "Top ~30% of individuals advance to State",            "Usually February"),
                ("State",     "Top 4 individuals advance to National",               "Usually March"),
                ("National",  "Top ~224 students nationwide — invitation only",      "Washington DC · May"),
            ],
            "timeline": [
                ("Jun–Aug",  "Summer prep: AoPS Introduction to Counting & Probability + Number Theory books"),
                ("Sep",      "School team formation + daily problem habit"),
                ("Oct–Dec",  "2 full Sprint + Target rounds per week, timed"),
                ("Jan",      "School competition — aim for top 4"),
                ("Feb",      "Chapter competition — aim for State qualification"),
                ("Mar",      "State competition — celebrate qualifying; aim for top 30 individually"),
            ],
            "topics": [
                "Number Theory (deep) — modular arithmetic, Euclidean algorithm, Euler's theorem intro",
                "Counting & Probability — combinations, permutations, expected value, complementary counting",
                "Algebra (advanced) — quadratics, systems of equations, sequences and series",
                "Geometry (advanced) — similar triangles, circle theorems, 3D geometry",
                "Competition Strategies — working backwards, casework, symmetry arguments",
            ],
            "resources": [
                {"name": "AoPS Introduction to Counting & Probability", "url": "https://artofproblemsolving.com/store", "type": "Paid", "desc": "Core G7 book — chapters 1–10 cover all MATHCOUNTS probability topics"},
                {"name": "AoPS Introduction to Number Theory",          "url": "https://artofproblemsolving.com/store", "type": "Paid", "desc": "Divisibility, primes, modular arithmetic — frequently tested"},
                {"name": "AoPS Alcumus (MATHCOUNTS level)",             "url": "https://artofproblemsolving.com/alcumus","type": "Free", "desc": "Set to MATHCOUNTS difficulty — aim for rating 75+ by Nov"},
                {"name": "Past Chapter & State Tests",                  "url": "https://www.mathcounts.org/resources/past-competitions", "type": "Free", "desc": "Essential — practice with real competition difficulty"},
                {"name": "MATHCOUNTS Trainer (Alcumus sprint)",         "url": "https://artofproblemsolving.com/mathcounts/trainer", "type": "Free", "desc": "Timed Sprint practice with real MATHCOUNTS problems"},
            ],
            "seek": [
                ("🏫 MATHCOUNTS Coach", "Your school coach submits Chapter entries — make sure they know your target"),
                ("📖 AoPS Online School","Consider enrolling in AoPS MATHCOUNTS prep course for fall semester"),
                ("🧑 Math Circle",       "DFW-area math circles run on weekends — great for meeting other competitors"),
                ("👦 8th Graders",       "Ask 8th graders who competed at Chapter to explain which problem types appear most"),
            ],
            "weekly_plan": [
                ("Mon",  "Sprint: 30 problems timed (40 min) — track score weekly"),
                ("Tue",  "AoPS Alcumus: 45 min, weakest topic"),
                ("Wed",  "Target: 4 pairs, 6 min each — show all work"),
                ("Thu",  "AoPS textbook: 1 chapter section + all exercises"),
                ("Fri",  "Team round or Countdown practice with classmates"),
                ("Sat",  "1.5 hr: 1 full past Chapter-level Sprint + review all errors"),
                ("Sun",  "Rest or optional: 20 min AMC 8 problem set"),
            ],
            "grade_goal": "Qualify for State. Top 30 placement at State is an exceptional Grade 7 result.",
            "tips": [
                "Track your Sprint score every week — consistent improvement matters more than single high scores",
                "Master the Countdown format — practice calling out answers within 3 seconds",
                "Algebra speed matters: practice solving linear equations in 10 seconds mentally",
                "Number theory is the most commonly undertrained area — the AoPS Number Theory book pays off",
                "Grade 7 State qualifiers frequently become Grade 8 MATHCOUNTS National competitors",
            ],
        },

        {
            "name": "AMC 8",
            "icon": "📐",
            "subject": "Math",
            "color": "#7c3aed",
            "bg": "#f5f3ff",
            "border": "#ddd6fe",
            "tagline": "Grade 7: target Honor Roll (18+) — one more year before AMC 8 eligibility ends",
            "overview": (
                "AMC 8 eligibility ends after Grade 8, so Grade 7 is a key year to push your score. "
                "Honor Roll (top 5%, score 18+) is a realistic and impressive target. "
                "MATHCOUNTS preparation significantly boosts AMC 8 performance — the topics overlap heavily. "
                "Distinguished Honor Roll (21+) in Grade 7 signals exceptional mathematical ability."
            ),
            "format_rows": [
                ("Target G7",  "Honor Roll = 18+ · Distinguished Honor Roll = 21+",   "November exam"),
                ("Overlap",    "MATHCOUNTS prep = direct AMC 8 prep",                  "Same topics, different format"),
            ],
            "timeline": [
                ("Aug–Sep",  "Solve 5 past AMC 8 papers under timed conditions — establish your baseline"),
                ("Oct",      "Drill your 3 weakest problem types (geometry, counting, or number theory)"),
                ("Nov",      "Take AMC 8 at school"),
            ],
            "topics": [
                "All Grade 6 topics — deepen and speed up",
                "Focus: geometry (circle area, composite figures) and counting (systematic listing)",
                "Hard problems (21–25): usually require a creative trick or combination of two concepts",
            ],
            "resources": [
                {"name": "AMC 8 Past Papers 2010–2024",   "url": "https://maa.org/math-competitions",           "type": "Free",  "desc": "Solve the 5 most recent years under timed conditions"},
                {"name": "AoPS AMC 8 Problem Wiki",        "url": "https://artofproblemsolving.com/wiki/index.php/AMC_8", "type": "Free", "desc": "Every problem from every year with multiple solution methods"},
            ],
            "seek": [
                ("🏫 Math Teacher", "Register school for AMC 8 — FISD participation is standard"),
                ("📊 Self-Assessment", "After each practice test, categorize errors: careless vs. knowledge gap vs. unfamiliar type"),
            ],
            "weekly_plan": [
                ("2x/week", "20 AMC 8 problems by type (e.g., all geometry from 2010–2020)"),
                ("Monthly", "One full 40-min timed test; review every error"),
            ],
            "grade_goal": "Score 18–21 (Honor Roll). Distinguished Honor Roll (21+) is an exceptional achievement.",
            "tips": [
                "Problems 1–15 should be automatic by Grade 7 — drill until they take under 1 min each",
                "Problems 21–25 each require a specific insight — study solution approaches, not just answers",
                "Sleep well the night before — AMC 8 rewards clear thinking over speed memorization",
            ],
        },

        {
            "name": "Science Olympiad",
            "icon": "🔬",
            "subject": "Science",
            "color": "#0891b2",
            "bg": "#ecfeff",
            "border": "#a5f3fc",
            "tagline": "Grade 7: specialize in 3–4 events and target Regional qualification",
            "overview": (
                "After your Grade 6 trial, Grade 7 is when Science Olympiad becomes serious. "
                "Pick 3–4 events where you have the strongest interest or aptitude and study them deeply. "
                "Target: finish in the top half at Regional. "
                "Colleges consistently note multi-year Science Olympiad participation — "
                "the deeper your specialization, the more impressive."
            ),
            "format_rows": [
                ("Events",         "Pick 3–4 primary events to specialize in",           "Plus 2–3 backup events"),
                ("Invitational",   "Unofficial practice tournaments — attend 2–3",       "Best learning opportunities"),
                ("Regional",       "Official qualifying tournament for State",            "Top ~10–20 teams advance"),
            ],
            "timeline": [
                ("Aug–Sep",  "Confirm team spot, pick your 3–4 events for the year"),
                ("Sep–Nov",  "Deep study of each event — read the rules carefully"),
                ("Nov–Jan",  "Invitationals — measure your progress, adjust study plan"),
                ("Feb–Mar",  "Regional — focus performance"),
                ("Mar–Apr",  "State (if qualified)"),
            ],
            "topics": [
                "Choose based on interest: Anatomy (body systems), Fossils (ID + evolution), Astronomy (deep sky objects)",
                "Chemistry Lab (lab skills, reactions, titration), Optics (reflection, refraction, lenses)",
                "Dynamic Planet (geologic processes, plate tectonics), Disease Detectives (epidemiology)",
                "Engineering builds: Bridge (balsa wood, maximize strength/weight), Wright Stuff (rubber band plane)",
            ],
            "resources": [
                {"name": "scioly.org Test Exchange",  "url": "https://scioly.org/tests",   "type": "Free", "desc": "Hundreds of past invitational tests for every event — primary prep resource"},
                {"name": "scioly.org Wiki per event", "url": "https://scioly.org/wiki",    "type": "Free", "desc": "Each event page has curated study resources, notes, and recommended reading"},
                {"name": "CrashCourse YouTube",       "url": "https://www.youtube.com/crashcourse", "type": "Free", "desc": "Biology, Chemistry, and Astronomy series — excellent foundation for event study"},
            ],
            "seek": [
                ("🏫 Team Coach",    "Work with coach to get feedback after each invitational test"),
                ("👥 Event Partner", "Every event has 2 members — practice together; explain concepts to each other"),
                ("🌐 Online Groups", "scioly.org Discord and forums have subject matter experts for each event"),
            ],
            "weekly_plan": [
                ("Mon",  "Event 1: 40 min study (notes + flashcards)"),
                ("Tue",  "Event 2: 40 min study"),
                ("Wed",  "Event 1: practice past test timed"),
                ("Thu",  "Event 2: practice past test timed"),
                ("Fri",  "Team practice + build event work"),
                ("Sat",  "1 hr: Event 3 study + build event construction"),
            ],
            "grade_goal": "Finish in top half at Regional. Qualify for State in at least one event pairing.",
            "tips": [
                "Make a cheat sheet (reference sheet) for each study event — many allow one page of notes",
                "Practice the exact format of each event: if it's a 20-min test, practice 20-min timed",
                "Engineering build events (bridge, plane) need iteration — start building in October, not January",
                "After each invitational, note every question you got wrong and study that specific topic the next week",
            ],
        },

        {
            "name": "NSDA Middle School Speech",
            "icon": "🎙️",
            "subject": "Speech",
            "color": "#dc2626",
            "bg": "#fef2f2",
            "border": "#fecaca",
            "tagline": "Formalize your speech skills with NSDA — Original Oratory is your strongest event",
            "overview": (
                "The National Speech & Debate Association (NSDA) runs a middle school program with "
                "tournaments throughout the year. Events include Original Oratory, Expository Speaking, "
                "Storytelling, and introductory Debate formats. "
                "Your Gavel Club background gives you a structural advantage in Oratory and Expository. "
                "Grade 7 goal: compete in 2–3 tournaments and earn NSDA points toward recognition."
            ),
            "format_rows": [
                ("Original Oratory",     "Original speech, 10 min max, memorized, any persuasive topic",        "Gavel Club Prepared Speech experience applies directly"),
                ("Expository Speaking",  "Informative speech with visual aid, 10 min max, memorized",           "Like an extended Gavel Club informative speech"),
                ("Storytelling",         "Read or tell a story, 5 min max",                                     "Great for creative and dramatic speakers"),
                ("Debate (Intro LD)",    "Lincoln-Douglas debate with simple value resolution",                  "Good if you enjoy argumentation"),
            ],
            "timeline": [
                ("Sep",      "Register with school debate team or independently at speechanddebate.org"),
                ("Sep–Oct",  "Write Original Oratory speech (10 min) — research + outline + draft"),
                ("Nov–Jan",  "Compete in 2–3 local/regional tournaments"),
                ("Mar–Apr",  "Regional qualifier tournament"),
                ("Jun",      "NSDA National Tournament (if qualified)"),
            ],
            "topics": [
                "Oratory topic selection: social issues, science topics, community problems — pick something you care about",
                "Structure: Attention → Background → 3 main points → Call to action (all within 10 min)",
                "Delivery: memorization, natural movement, vocal variety — same as Gavel Club",
                "Research: credible sources, statistics, personal anecdote + expert quote combination",
            ],
            "resources": [
                {"name": "NSDA Middle School Unified Manual", "url": "https://www.speechanddebate.org/middle-school-unified-manual/", "type": "Free", "desc": "Official rules for all middle school events — read the event description carefully"},
                {"name": "NSDA Campus (practice videos)",    "url": "https://www.nsda.org/students/resources/",                     "type": "Free", "desc": "Video examples of top-placing speeches at national level"},
                {"name": "TED Talks",                        "url": "https://www.ted.com",                                           "type": "Free", "desc": "Study great speakers' openings, transitions, and closings"},
            ],
            "seek": [
                ("🏫 Speech Coach",   "Ask school if there is a speech or debate team — a coach will significantly accelerate progress"),
                ("🗣️ Gavel Advisor",  "Your Gavel Club faculty advisor can give feedback on Oratory speeches too"),
                ("📺 YouTube",        "Search 'NSDA Original Oratory national winner' to study top examples"),
            ],
            "weekly_plan": [
                ("Mon",    "Research oratory topic: read 2 articles, take notes"),
                ("Tue",    "Drafting: write one section of the speech"),
                ("Wed",    "Deliver full speech aloud — phone recording"),
                ("Thu",    "Review recording: note 2 things to improve"),
                ("Fri",    "Gavel Club meeting (reinforces all oratory skills)"),
            ],
            "grade_goal": "Complete 1 Original Oratory speech. Compete in 2+ tournaments. Earn NSDA points.",
            "tips": [
                "Your Gavel Club experience is a genuine advantage — use the same preparation approach",
                "Original Oratory topics that are specific and personal tend to score higher than broad social topics",
                "Memorize in chunks: perfect paragraph 1, then 2, then connect them — don't try to memorize all at once",
                "At tournaments, watch other competitors in your round — you'll learn as much from watching as competing",
            ],
        },

        {
            "name": "National History Day",
            "icon": "📜",
            "subject": "Social Studies",
            "color": "#065f46",
            "bg": "#ecfdf5",
            "border": "#a7f3d0",
            "tagline": "Research-based competition with real national reach — start early, go deep",
            "overview": (
                "National History Day (NHD) is an annual theme-based research competition open to Grades 6–12. "
                "Students choose a historical topic related to the annual theme, research deeply, "
                "and present in one of five formats: Paper, Exhibit, Documentary, Performance, or Website. "
                "School → District → State → National. National finalists present at the University of Maryland. "
                "Top college admissions officers recognize NHD National as equivalent to science fair in impact."
            ),
            "format_rows": [
                ("Paper",       "Individual only · 2500–7500 words · annotated bibliography required",     "Best for strong writers"),
                ("Exhibit",     "1–2 students · display board 40x30 inches with images + text",           "Visual + research balance"),
                ("Documentary", "1–2 students · 10 min video · historical footage + narration",           "Great for tech-comfortable students"),
                ("Website",     "1–5 students · multimedia site, 1200 words + media",                     "Collaborative + flexible"),
                ("Performance", "1–3 students · 10 min live performance",                                 "For dramatic + theatrical students"),
            ],
            "timeline": [
                ("Apr–May",  "Theme announced for following year — brainstorm topic ideas"),
                ("Jun–Aug",  "Topic research + primary source collection (library, online archives)"),
                ("Sep–Oct",  "Create/write project; write process paper + annotated bibliography"),
                ("Nov",      "School competition"),
                ("Dec–Jan",  "Revise based on feedback"),
                ("Feb–Mar",  "District competition"),
                ("Mar–Apr",  "State competition"),
                ("Jun",      "National competition, University of Maryland"),
            ],
            "topics": [
                "Consult the annual NHD theme — connect your topic to the theme's historical significance",
                "Primary sources: original documents, letters, photos, newspaper archives (Chronicling America at loc.gov)",
                "Secondary sources: books, academic articles, encyclopedia entries",
                "Process Paper (500 words max): explain why you chose the topic and how you researched it",
                "Annotated Bibliography: every source with 2–3 sentence annotation",
            ],
            "resources": [
                {"name": "NHD Official Website",           "url": "https://www.nhd.org",                              "type": "Free", "desc": "Annual theme, rules, past project examples, and judging criteria"},
                {"name": "Texas NHD (TxNHD)",              "url": "https://www.txnhd.org",                            "type": "Free", "desc": "Texas state organization — District schedules, coordinator contacts"},
                {"name": "Library of Congress",            "url": "https://www.loc.gov/collections/",                  "type": "Free", "desc": "Primary source archive — digitized newspapers, photos, government documents"},
                {"name": "JSTOR (via school login)",       "url": "https://www.jstor.org",                            "type": "Free*","desc": "Academic articles — check if FISD provides access"},
                {"name": "NHD Project Examples",           "url": "https://www.nhd.org/best-of-nhd",                   "type": "Free", "desc": "Watch/read winning projects from national level for format inspiration"},
            ],
            "seek": [
                ("🏫 Social Studies Teacher", "NHD is often run through the SS or History department — ask your teacher"),
                ("📚 School Librarian",       "Research assistance with databases and citation formats"),
                ("🏛️ Local Library",          "Interlibrary loan for rare books; many have NHD coaching programs"),
            ],
            "weekly_plan": [
                ("Jun–Aug",  "2 research sessions/week: read sources, take organized notes by topic"),
                ("Sep–Oct",  "Production: 2 hrs/week creating exhibit/documentary/website"),
                ("Oct–Nov",  "Write process paper + bibliography; practice presenting to parents"),
            ],
            "grade_goal": "District qualifier. If you do strong research on a compelling topic, State is achievable.",
            "tips": [
                "Pick a topic YOU find genuinely interesting — you'll spend 6+ months on it",
                "Primary sources win contests — find ONE original document that no other project uses",
                "Start the annotated bibliography from Day 1 — compiling it at the end is painful",
                "Documentary and Website formats allow more creativity and visual storytelling than Paper",
                "Judges ask 5–10 min of questions — know your topic deeply, not just your project",
            ],
        },
    ],

    # ══════════════════════════════════════════════════════════════════════════
    "grade_8": [
        {
            "name": "MATHCOUNTS — Chapter to State Push",
            "icon": "🔢",
            "subject": "Math",
            "color": "#1d4ed8",
            "bg": "#eff6ff",
            "border": "#bfdbfe",
            "tagline": "Grade 8: your final MATHCOUNTS year — Chapter qualifier → State → National is the dream",
            "overview": (
                "Grade 8 is your last year of MATHCOUNTS eligibility. "
                "This is the year to go all-in: intensive daily practice, Chapter qualification, "
                "strong State placement, and potentially National. "
                "MATHCOUNTS National competitor on a high school application is a top-tier academic signal. "
                "Even Chapter/State qualification at Grade 8 is impressive for selective high schools and magnet programs."
            ),
            "format_rows": [
                ("School",    "Top 4 advance to Chapter",                              "January–February"),
                ("Chapter",   "Top ~10–12 individuals advance to State",               "February"),
                ("State",     "Top 4 advance to National — the elite goal",            "March"),
                ("National",  "~224 students total — top math students in the US",     "Washington DC · May"),
            ],
            "timeline": [
                ("Jun–Aug",  "Summer: Intermediate Algebra + AoPS Countdown practice"),
                ("Sep",      "6-day weekly practice schedule begins"),
                ("Oct",      "Full Sprint + Target rounds weekly; Alcumus rating target: 85+"),
                ("Nov",      "AMC 8 in November — warm-up for competition season"),
                ("Jan",      "School competition — take the top 4 spot"),
                ("Feb",      "Chapter competition — target top 12 for State qualification"),
                ("Mar",      "State competition — top 4 to National"),
                ("May",      "National tournament (if qualified)"),
            ],
            "topics": [
                "Advanced Algebra — quadratic formula, Vieta's formulas, polynomial factoring",
                "Geometry — advanced circle theorems, 3D solid geometry, trigonometry intro",
                "Number Theory — Euler's theorem, Chinese Remainder Theorem intro, number bases",
                "Combinatorics — PIE (Principle of Inclusion-Exclusion), generating functions intro",
                "Countdown speed — mental computation, pattern recognition under pressure",
            ],
            "resources": [
                {"name": "AoPS Intermediate Algebra",      "url": "https://artofproblemsolving.com/store",               "type": "Paid", "desc": "Advanced algebra concepts that appear at State/National level"},
                {"name": "MATHCOUNTS National Archive",    "url": "https://www.mathcounts.org/resources/past-competitions","type": "Free", "desc": "Past State and National tests — practice at the hardest level"},
                {"name": "AoPS Alcumus (target 85+)",      "url": "https://artofproblemsolving.com/alcumus",              "type": "Free", "desc": "Push your rating to 85+ — correlates with State-level performance"},
                {"name": "AoPS MATHCOUNTS Trainer",        "url": "https://artofproblemsolving.com/mathcounts/trainer",   "type": "Free", "desc": "Sprint/Countdown practice with real competition problems"},
            ],
            "seek": [
                ("📖 AoPS Online Course",  "Consider the 'MATHCOUNTS' or 'AMC 10' course — structured weekly with instructor feedback"),
                ("🏫 Coach",               "Communicate your Chapter/State goal directly — coaches can prioritize your preparation"),
                ("🧑 National Competitors","Search AoPS forums for MATHCOUNTS Nationals solutions explained by former competitors"),
            ],
            "weekly_plan": [
                ("Mon",  "Full Sprint timed (30 q, 40 min) — track score"),
                ("Tue",  "AoPS Alcumus 1 hr: advanced topic"),
                ("Wed",  "4 Target pairs timed + Countdown practice (15 min)"),
                ("Thu",  "AoPS Intermediate Algebra: 1 section + all exercises"),
                ("Fri",  "Team round + Countdown with classmates"),
                ("Sat",  "2 hrs: 1 past Chapter/State test full simulation"),
                ("Sun",  "AMC 10 problems (25 min) — builds advanced problem instincts"),
            ],
            "grade_goal": "Chapter qualifier → State. National is the stretch goal. "
                          "Any State qualification in Grade 8 is an impressive HS application achievement.",
            "tips": [
                "The difference between Chapter and State competitors is usually the hard problems (Sprint 25–30)",
                "Countdown format: practice saying answers aloud in 3 seconds — the oral pressure is different from written",
                "Study State-level past tests from 3–4 years ago — patterns repeat",
                "Physical preparation matters: sleep 8+ hrs and eat well the week before competitions",
                "Even if you don't reach National, Chapter/State experience builds AMC 10/AIME skills for HS",
            ],
        },

        {
            "name": "AMC 8 & AMC 10 Prep",
            "icon": "📐",
            "subject": "Math",
            "color": "#7c3aed",
            "bg": "#f5f3ff",
            "border": "#ddd6fe",
            "tagline": "AMC 8 final year — target Distinguished Honor Roll · Begin AMC 10 preparation",
            "overview": (
                "Grade 8 is your final year of AMC 8 eligibility. "
                "Target: Distinguished Honor Roll (21+/25). "
                "More importantly, begin serious AMC 10 preparation — the high school competition "
                "where AIME qualification (score ~107+) is a meaningful college admissions signal. "
                "Your MATHCOUNTS preparation already covers 80% of AMC 10 Grade 9 content."
            ),
            "format_rows": [
                ("AMC 8 target",   "Distinguished Honor Roll = 21+/25",             "November exam — final year"),
                ("AMC 10 prep",    "25 MC · 75 min · harder than AMC 8",            "Taken in 9th grade — prep begins now"),
                ("AIME qualifier", "AMC 10 score ≥ 107 → AIME invitation",          "AIME qualification = strong HS signal"),
            ],
            "timeline": [
                ("Jun–Aug",  "Solve 10 past AMC 10A/10B papers from 2015–2020 (untimed first, then timed)"),
                ("Sep–Oct",  "AMC 8 final prep + continue AMC 10 problem exposure"),
                ("Nov",      "Take AMC 8 — aim for 21+"),
                ("Nov–May",  "AMC 10 problems 3x/week — build toward Grade 9 attempt"),
            ],
            "topics": [
                "AMC 8 (final review): ensure mastery of all 25 problem types from past years",
                "AMC 10 new topics: logarithms (intro), geometric series, complex numbers intro",
                "AMC 10 geometry: advanced angle chasing, trigonometry basics, 3D coordinates",
                "AMC 10 counting: binomial theorem, stars and bars, expected value",
            ],
            "resources": [
                {"name": "AMC 10 Past Papers",        "url": "https://maa.org/math-competitions",           "type": "Free", "desc": "Solve 2015–2023 AMC 10A papers under timed conditions"},
                {"name": "AoPS AMC 10 Prep",          "url": "https://artofproblemsolving.com/wiki/index.php/AMC_10_Preparation", "type": "Free", "desc": "Topic list and strategy guide for AMC 10"},
                {"name": "AoPS Precalculus",          "url": "https://artofproblemsolving.com/store",        "type": "Paid", "desc": "Covers trig and logs that appear on AMC 10 — start if time allows"},
            ],
            "seek": [
                ("🏫 8th Grade Math Teacher",  "Ask for pre-algebra or algebra II enrichment beyond school curriculum"),
                ("📖 AoPS AMC 10 Course",      "Structured course designed for Grade 8–9 AMC 10 preparation"),
            ],
            "weekly_plan": [
                ("Mon/Wed/Fri", "5 AMC 10 problems (problems 1–15 first; build up to 16–25)"),
                ("Tue/Thu",     "AoPS Alcumus: advanced topics (logarithms, trig intro, combinatorics)"),
                ("Oct weekend", "2 full timed AMC 8 practice tests"),
            ],
            "grade_goal": "AMC 8 Distinguished Honor Roll (21+). Solve AMC 10 problems 1–15 consistently. "
                          "AIME qualification is a HS goal but prep starts now.",
            "tips": [
                "AMC 10 problems 1–10 overlap heavily with hard AMC 8 — you're already 40% prepared",
                "AIME is a proof that you can do hard math under pressure — colleges take note",
                "Don't neglect AMC 8 trying to prep for AMC 10 — finish strong on your final AMC 8",
            ],
        },

        {
            "name": "Science Olympiad — State Push",
            "icon": "🔬",
            "subject": "Science",
            "color": "#0891b2",
            "bg": "#ecfeff",
            "border": "#a5f3fc",
            "tagline": "Grade 8: State is the target — specialize deeply in 3–4 events",
            "overview": (
                "Grade 8 is when Science Olympiad experience translates into State results. "
                "With 2 years of event experience, you know your strongest events. "
                "Go deep on 3–4 events, aim for top scores at Regional, and push for State. "
                "Science Olympiad State placements in middle school transition directly to high school team spots "
                "and are a consistent signal in selective high school and college admissions."
            ),
            "format_rows": [
                ("Regional",  "Qualifying tournament for State — top 10–20 teams advance",   "February–March"),
                ("State",     "Top teams from state — very competitive",                       "March–April"),
                ("National",  "Invitation only — top teams from State",                        "May"),
            ],
            "timeline": [
                ("Aug–Sep",  "Lock in 4 events; read full event rules document for each"),
                ("Sep–Nov",  "Deep study phase + invitational testing"),
                ("Dec–Jan",  "Build events: complete 2–3 iterations of your device"),
                ("Feb",      "Regional — perform at full effort"),
                ("Mar–Apr",  "State (if qualified) — review every mistake from Regional"),
            ],
            "topics": [
                "Specialize: become the school's best at your events — depth > breadth in Grade 8",
                "Study events: create a comprehensive reference sheet (1 page) for each",
                "Build events: document every test flight/test load with measurements",
                "Test strategy: allocate time carefully — hard questions count same as easy ones",
            ],
            "resources": [
                {"name": "scioly.org Test Archive",   "url": "https://scioly.org/tests",      "type": "Free", "desc": "Solve every available past test for your specific events — track your scores"},
                {"name": "scioly.org Wiki (per event)","url": "https://scioly.org/wiki",       "type": "Free", "desc": "Advanced study guides + resource recommendations for State-level competition"},
                {"name": "Physics/Chemistry textbooks", "url": "https://openstax.org",          "type": "Free", "desc": "OpenStax free textbooks for deeper science foundation"},
            ],
            "seek": [
                ("🏫 Team Coach",       "Ask for event-specific mentoring — coaches can pair you with strong alumni"),
                ("🌐 scioly.org Discord","Find expert advice for specific events from national-level competitors"),
                ("👩‍🏫 Subject Teacher", "Physics teacher for optics/circuits; bio teacher for anatomy — ask for extra depth"),
            ],
            "weekly_plan": [
                ("Mon",  "Event A: 1 hr deep study (new content)"),
                ("Tue",  "Event B: 1 hr deep study"),
                ("Wed",  "Event A: timed past test + review"),
                ("Thu",  "Event B: timed past test + review"),
                ("Fri",  "Team practice + build event work"),
                ("Sat",  "Build event: construction + testing + documentation"),
                ("Sun",  "Event C/D: 45 min study"),
            ],
            "grade_goal": "Top 20% placement at Regional. State qualification for at least one event pairing. "
                          "State appearance on a HS application is a strong academic signal.",
            "tips": [
                "Your reference sheets are your weapon — build them carefully over October-November",
                "For build events: test early, iterate often, and document every trial",
                "Regional day nerves are real — practice your test routine the week before under time pressure",
                "Multi-year Science Olympiad is more impressive than one year — emphasize your progression",
            ],
        },

        {
            "name": "NSDA & Gavel Club — District Push",
            "icon": "🎤",
            "subject": "Speech",
            "color": "#dc2626",
            "bg": "#fef2f2",
            "border": "#fecaca",
            "tagline": "Grade 8: District-level title in Gavel + NSDA National qualifier — your biggest speech year",
            "overview": (
                "Grade 8 is the year to put your speech work on the map. "
                "Two parallel goals: District-level Gavel Club title (Club → Area → Division → District ladder) "
                "and NSDA National qualifier in Original Oratory or another event. "
                "A District-level Gavel Club title or NSDA National appearance at the middle school level "
                "is a standout item on a high school application — very few students achieve it."
            ),
            "format_rows": [
                ("Gavel Club contest", "Club → Area → Division → District",           "Year-round — starts fall"),
                ("NSDA Oratory",       "10 min memorized speech · tournament circuit", "Earn points toward national"),
                ("NSDA National",      "Qualifier via point threshold or tournament",  "June tournament"),
                ("TFA circuit",        "Texas Forensic Association tournaments",       "Sep–May for debate/speech"),
            ],
            "timeline": [
                ("Aug–Sep",  "Finalize Oratory speech topic; write first draft"),
                ("Sep–Oct",  "Deliver to Gavel Club and school coach for feedback; revise"),
                ("Oct–Nov",  "Club-level Gavel Contest — compete and advance"),
                ("Nov–Feb",  "Compete in 3–4 NSDA tournaments — earn points"),
                ("Feb–Mar",  "Gavel Area and Division contests"),
                ("Mar–Apr",  "Gavel District contest + NSDA Regional qualifier"),
                ("May–Jun",  "NSDA National Tournament (if qualified)"),
            ],
            "topics": [
                "Original Oratory polish: is your opening unforgettable? Does every sentence earn its place?",
                "Gavel Club: master vocal variety (rate, pitch, volume, pause) and purposeful movement",
                "Storytelling technique: sensory details, dialogue, specific scene-setting",
                "Argument structure for debate events: claim, warrant, impact model",
            ],
            "resources": [
                {"name": "NSDA National Award Videos",     "url": "https://www.speechanddebate.org/students/resources/", "type": "Free", "desc": "Watch National-level Oratory performances — study pacing and storytelling"},
                {"name": "World Championship Toastmasters","url": "https://www.youtube.com/results?search_query=toastmasters+world+champion+speech", "type": "Free", "desc": "Annual World Championship speeches — the gold standard of prepared speaking"},
                {"name": "TFA Official Site",              "url": "https://www.texasforensics.org",                      "type": "Free", "desc": "Texas Forensic Association tournament schedule — attend 2–3 fall events"},
            ],
            "seek": [
                ("🏫 Gavel Advisor",     "Tell them your District goal — they'll nominate you and guide you through each level"),
                ("🗣️ Speech Coach",      "A school speech/debate coach is invaluable for Oratory feedback"),
                ("📺 Video Review",      "Record every practice delivery — watch back critically each time"),
                ("🤝 Gavel Mentor",      "Find a past District titleholder to mentor your contest speeches"),
            ],
            "weekly_plan": [
                ("Mon",  "Deliver full Oratory once — record on phone"),
                ("Tue",  "Watch recording: identify 1 specific thing to improve"),
                ("Wed",  "Rework that specific section; practice 3 times"),
                ("Thu",  "Table Topics: 3 impromptu speeches (2 min each) on random topics"),
                ("Fri",  "Gavel Club meeting — active participation, evaluate 1 speaker"),
                ("Sat",  "Full speech delivery to a family audience + Q&A practice"),
            ],
            "grade_goal": "Gavel Club Area or Division title. NSDA National qualification or strong regional placement. "
                          "Either alone on an HS application is impressive; both is exceptional.",
            "tips": [
                "Your opening line must be rehearsed 50+ times until it's completely natural under pressure",
                "Contest judges see 6–8 speakers in a round — be memorable in the first 30 seconds",
                "For District: study your competition. Watch who advances at Area and adjust your style",
                "NSDA points accumulate — even 5th place at a tournament earns points toward recognition",
                "Your Gavel Club years are the foundation — reference your growth arc in your opening",
            ],
        },

        {
            "name": "Scholastic — Gold Key Target",
            "icon": "✍️",
            "subject": "Writing",
            "color": "#9333ea",
            "bg": "#fdf4ff",
            "border": "#e9d5ff",
            "tagline": "Grade 8: submit your strongest piece ever — Gold Key is within reach",
            "overview": (
                "By Grade 8, you've had 2 previous Scholastic submission cycles to learn from. "
                "This year, the goal is Gold Key — the highest regional award that advances to national review. "
                "Gold Key winners are featured in the Scholastic national gallery and on college applications. "
                "Your writing has had 2 years to mature — submit your single best piece with maximum polish."
            ),
            "format_rows": [
                ("Gold Key",    "Top award at regional level → National review",        "~10–15% of submissions"),
                ("Silver Key",  "Second tier — strong recognition",                     "Featured in regional exhibit"),
                ("Portfolio",   "Seniors can submit a writing portfolio (8 pieces)",     "Not applicable in G8 but build toward it"),
            ],
            "timeline": [
                ("Jun–Jul",  "Write your best piece — use summer for first drafts"),
                ("Aug–Sep",  "Revise with English teacher feedback"),
                ("Oct",      "Beta readers (classmates, family) — focus on clarity + emotional impact"),
                ("Nov",      "Final revision + proofread"),
                ("Dec",      "Submit (regional deadlines vary: typically Dec–Jan)"),
                ("Feb",      "Regional results — Gold/Silver Key announced"),
                ("Mar–Apr",  "Gold Key pieces advance to National"),
            ],
            "topics": [
                "Short Story: your strongest writing — unforgettable characters + specific conflict + resonant ending",
                "Personal Essay: a moment that changed you — judges value honesty and specificity over drama",
                "Flash Fiction: the hardest to do well — one perfect scene with an unexpected turn",
                "Science Fiction/Fantasy: allowed, but usually judged harder — use the genre to explore a real idea",
            ],
            "resources": [
                {"name": "artandwriting.org Gallery",      "url": "https://www.artandwriting.org/galleries/",  "type": "Free", "desc": "Browse Gold Key and national award-winning pieces from past years — essential reading"},
                {"name": "Best American Short Stories",    "url": "https://www.amazon.com",                    "type": "Library", "desc": "Read 5+ stories; study how published authors open and close their work"},
                {"name": "Writing Excuses Podcast",        "url": "https://writingexcuses.com",                "type": "Free", "desc": "15-min episodes on craft by published authors — focused and practical"},
            ],
            "seek": [
                ("🏫 ELA Teacher",     "Ask directly: 'Will you help me revise this for Scholastic submission?' — most will say yes"),
                ("📚 Writing Workshop","If your school offers creative writing club or workshop, participate all year"),
                ("🏅 Past Winners",    "Find past Scholastic winners (many published in yearbooks) and study their technique"),
            ],
            "weekly_plan": [
                ("Jun–Jul",  "Write 500 words/day for 2 weeks (quantity, not quality) — discover your best idea"),
                ("Aug–Oct",  "Weekly revision session (2 hrs): focus on one element per session — dialogue, pacing, opening"),
                ("Nov",      "Three separate proofreading passes: grammar, word choice, flow"),
            ],
            "grade_goal": "Submit 1–2 polished pieces. Target Gold Key regionally. "
                          "Even Silver Key in Grade 8 is impressive — write with full effort.",
            "tips": [
                "Read Gold Key examples on artandwriting.org before writing — understand the bar",
                "Cut your weakest sentences ruthlessly — strong writing is often editing, not just drafting",
                "Your personal essay voice should sound like you, not like a textbook",
                "Submit early — rushed last-minute submissions rarely win",
                "A story you wrote in Grade 6 and have revised twice is often stronger than a fresh Grade 8 draft",
            ],
        },
    ],
}


# ── Renderer ──────────────────────────────────────────────────────────────────

def render_comp_prep(grade_key: str) -> None:
    """Render competition prep guides for the given grade (grade_6, grade_7, grade_8)."""
    comps = COMPS.get(grade_key, [])
    if not comps:
        st.info("Competition prep guides coming soon.")
        return

    subject_order = ["Math", "Science", "Speech", "Writing", "Social Studies", "Multiple"]
    comps_sorted  = sorted(comps, key=lambda c: (subject_order.index(c["subject"]) if c["subject"] in subject_order else 99, c["name"]))

    for comp in comps_sorted:
        icon      = comp["icon"]
        name      = comp["name"]
        color     = comp["color"]
        bg        = comp["bg"]
        border    = comp["border"]
        tagline   = comp["tagline"]
        subject   = comp["subject"]

        with st.expander(f"{icon} {name}  ·  {subject}", expanded=False):
            # Header strip
            st.markdown(
                f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
                f'padding:12px 16px;margin-bottom:14px">'
                f'<div style="font-size:15px;font-weight:700;color:{color};margin-bottom:4px">'
                f'{icon} {name}</div>'
                f'<div style="font-size:12px;color:#475569">{tagline}</div></div>',
                unsafe_allow_html=True,
            )

            # Overview
            st.markdown(f"**Overview**")
            st.markdown(comp["overview"])

            c_left, c_right = st.columns(2)

            with c_left:
                # Format
                st.markdown("**📋 Competition Format**")
                fmt_rows = [{"Round / Aspect": r, "Details": d, "Notes": n} for r, d, n in comp["format_rows"]]
                st.dataframe(fmt_rows, hide_index=True, use_container_width=True,
                             column_config={
                                 "Round / Aspect": st.column_config.TextColumn(width="medium"),
                                 "Details":        st.column_config.TextColumn(width="large"),
                                 "Notes":          st.column_config.TextColumn(width="large"),
                             })

                # Topics
                st.markdown("**📚 Topics / Skills to Master**")
                for t in comp["topics"]:
                    st.markdown(f"- {t}")

            with c_right:
                # Timeline
                st.markdown("**🗓️ Timeline — When to Start**")
                for month, action in comp["timeline"]:
                    st.markdown(
                        f'<div style="display:flex;gap:10px;margin-bottom:6px;font-size:13px">'
                        f'<span style="min-width:70px;font-weight:600;color:{color}">{month}</span>'
                        f'<span style="color:#334155">{action}</span></div>',
                        unsafe_allow_html=True,
                    )

                # Weekly plan
                st.markdown("**📅 Weekly Prep Schedule**")
                for day, task in comp["weekly_plan"]:
                    st.markdown(
                        f'<div style="display:flex;gap:10px;margin-bottom:5px;font-size:13px">'
                        f'<span style="min-width:80px;font-weight:600;color:#475569">{day}</span>'
                        f'<span style="color:#334155">{task}</span></div>',
                        unsafe_allow_html=True,
                    )

            st.divider()

            r2_left, r2_right = st.columns(2)

            with r2_left:
                # Resources
                st.markdown("**🌐 Resources**")
                for res in comp["resources"]:
                    badge_color = "#059669" if res["type"] == "Free" else ("#b45309" if res["type"] == "Paid" else "#0369a1")
                    st.markdown(
                        f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;'
                        f'padding:8px 12px;margin-bottom:6px">'
                        f'<a href="{res["url"]}" target="_blank" style="font-weight:600;color:{color};'
                        f'text-decoration:none;font-size:13px">{res["name"]}</a> '
                        f'<span style="font-size:10px;font-weight:600;color:{badge_color};'
                        f'background:{"#dcfce7" if res["type"]=="Free" else ("#fef3c7" if res["type"]=="Paid" else "#e0f2fe")};'
                        f'border-radius:4px;padding:1px 6px">{res["type"]}</span>'
                        f'<div style="font-size:11px;color:#64748b;margin-top:2px">{res["desc"]}</div></div>',
                        unsafe_allow_html=True,
                    )

            with r2_right:
                # Seek help
                st.markdown("**🤝 Who to Seek Help From**")
                for role, detail in comp["seek"]:
                    st.markdown(
                        f'<div style="background:#f0fdf4;border-left:3px solid #22c55e;border-radius:0 8px 8px 0;'
                        f'padding:8px 12px;margin-bottom:6px;font-size:13px">'
                        f'<b>{role}</b><br><span style="color:#334155">{detail}</span></div>',
                        unsafe_allow_html=True,
                    )

                # Grade goal
                st.markdown("**🎯 Goal for This Grade**")
                st.success(comp["grade_goal"])

                # Tips
                if comp.get("tips"):
                    with st.expander("💡 Pro Tips", expanded=False):
                        for tip in comp["tips"]:
                            st.markdown(f"✅ {tip}")
