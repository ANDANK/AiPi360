"""Grade 6 TEKS curriculum — monthly pacing guide for FISD Wortham Intermediate.

Standards sourced from Texas Education Agency (TEA) official TEKS documents:
  Math   §111.26  |  ELA §110.23  |  Science §112.18  |  Social Studies §113.18
School year: Aug 12, 2026 → May 28, 2027
"""

# ── Color scheme per subject ──────────────────────────────────────────────────
SUBJECT_STYLE = {
    "Math":           {"bg": "#eff6ff", "border": "#2563eb", "icon": "🔢", "tag_bg": "#dbeafe", "tag_color": "#1d4ed8"},
    "ELA":            {"bg": "#fdf4ff", "border": "#9333ea", "icon": "📖", "tag_bg": "#f3e8ff", "tag_color": "#7c3aed"},
    "Science":        {"bg": "#f0fdf4", "border": "#16a34a", "icon": "🔬", "tag_bg": "#dcfce7", "tag_color": "#15803d"},
    "Social Studies": {"bg": "#fff7ed", "border": "#ea580c", "icon": "🌍", "tag_bg": "#fed7aa", "tag_color": "#c2410c"},
}

# ── Monthly pacing: list of (month_label, [topics]) per subject ───────────────
# Ordered Aug → May (school year)
MONTHLY_PACING = {
    "Math": [
        ("Aug 12–Aug 31\nGetting Started", [
            "Review of 5th grade concepts",
            "Classify numbers: natural, whole, integer, rational",
            "Number line: ordering integers and rational numbers",
            "Absolute value and opposites",
            "Introduction to math tools & graphing calculator",
        ]),
        ("Sep\nRational Numbers & Operations", [
            "Multiply and divide integers",
            "Operations with fractions: multiply & divide",
            "Operations with decimals: multiply & divide",
            "Order of operations (PEMDAS) with rational numbers",
            "Real-world problems with rational numbers",
        ]),
        ("Oct\nRatios & Proportional Reasoning", [
            "Ratio concepts and notation (a:b, a/b, a to b)",
            "Unit rates and rate comparisons",
            "Equivalent ratios and ratio tables",
            "Proportional reasoning in real-world contexts",
            "Scale drawings and models",
            "⚠️ Fall Break: Oct 12–16",
        ]),
        ("Nov\nPercent", [
            "Percent as rate per 100",
            "Converting: fractions ↔ decimals ↔ percents",
            "Percent of a number (find the part, whole, or percent)",
            "Percent applications: tax, tip, discount, markup",
            "Simple interest introduction",
            "⚠️ Thanksgiving Break: Nov 23–27",
        ]),
        ("Dec\nExpressions & Variables", [
            "Independent vs. dependent quantities",
            "Writing algebraic expressions from words",
            "Evaluating expressions by substitution",
            "Equivalent expressions using properties",
            "Tables and graphs to represent relationships",
            "⚠️ Winter Break begins Dec 21",
        ]),
        ("Jan\nEquations & Inequalities", [
            "One-variable, one-step equations (all 4 operations)",
            "Solving equations using inverse operations",
            "Inequalities: writing, graphing on number line",
            "Real-world equation word problems",
            "⚠️ MLK Day: Jan 19",
        ]),
        ("Feb\nGeometry — Area & Surface Area", [
            "Area of triangles and quadrilaterals",
            "Area of composite figures",
            "Surface area of rectangular and triangular prisms",
            "Nets of 3-D figures",
            "⚠️ Presidents Day: Feb 15",
        ]),
        ("Mar\nGeometry — Volume & Coordinate Plane", [
            "Volume of rectangular prisms (fractional dimensions)",
            "Coordinate plane: all 4 quadrants",
            "Plotting ordered pairs (integers and fractions)",
            "Distance on coordinate plane (horizontal & vertical)",
            "Perimeter and area on coordinate plane",
            "⚠️ Spring Break: Mar 15–19",
        ]),
        ("Apr\nData Analysis & STAAR Prep", [
            "Statistical questions vs. non-statistical questions",
            "Mean, median, mode, range, IQR",
            "Dot plots and stem-and-leaf plots",
            "Box plots: quartiles, outliers",
            "Histograms: frequency tables",
            "Comparing data distributions",
            "★ STAAR Reading: ~Apr 6 | STAAR Math: ~Apr 8",
        ]),
        ("May\nFinancial Literacy & Review", [
            "Income: wages, salary, commission, tips",
            "Payroll deductions and income taxes (W-2 intro)",
            "Checking and savings accounts",
            "Credit scores and responsible credit use",
            "Year-end review and reinforcement",
            "⚠️ Last Day: May 28",
        ]),
    ],
    "ELA": [
        ("Aug 12–Aug 31\nGetting Started", [
            "Reading community building: routines, independent reading",
            "Literary elements review: plot, character, setting, theme, conflict",
            "Author's purpose: inform, entertain, persuade",
            "Writing process overview",
            "Grammar baseline: parts of speech review",
        ]),
        ("Sep\nNarrative Reading & Personal Writing", [
            "Point of view: first vs. third person",
            "Narrator's perspective and reliability",
            "Literary devices: simile, metaphor, imagery, hyperbole",
            "Personal narrative writing (small moment, sensory detail)",
            "Revising for voice and word choice",
            "Grammar: complete sentences, subject-verb agreement",
        ]),
        ("Oct\nInformational & Expository Texts", [
            "Main idea and key supporting details",
            "Text structures: cause/effect, compare/contrast, problem/solution",
            "Summarizing and paraphrasing non-fiction",
            "Informational essay writing (introduction, body, conclusion)",
            "Text features: headings, captions, diagrams",
            "Grammar: punctuation of complex sentences",
            "⚠️ Fall Break: Oct 12–16",
        ]),
        ("Nov\nResearch & Source Evaluation", [
            "Research process: topic selection, forming research questions",
            "Evaluating sources: credibility, relevance, accuracy",
            "Note-taking strategies: paraphrase vs. quote",
            "MLA citation basics (in-text citation and works cited)",
            "Avoiding plagiarism",
            "Research-based informational writing",
            "⚠️ Thanksgiving Break: Nov 23–27",
        ]),
        ("Dec\nArgumentative Texts & Writing Intro", [
            "Claims, reasons, and evidence in argument",
            "Counterclaims and rebuttals",
            "Evaluating an author's argument and logic",
            "Introduction to argumentative essay structure",
            "Vocabulary: connotation vs. denotation",
            "Grammar: conjunctions and transitions",
            "⚠️ Winter Break begins Dec 21",
        ]),
        ("Jan\nPoetry & Drama", [
            "Figurative language: personification, onomatopoeia, alliteration, allusion",
            "Poetic structure: stanza, line, rhyme scheme, free verse",
            "Analyzing mood and tone in poetry",
            "Drama elements: acts, scenes, stage directions, dialogue",
            "Comparing poem, drama, and prose versions of the same story",
            "⚠️ MLK Day: Jan 19",
        ]),
        ("Feb\nReading Comprehension & STAAR Focus", [
            "Making inferences from textual evidence",
            "Using context clues for unknown vocabulary",
            "Comparing multiple texts on the same topic",
            "Media literacy: analyzing visuals, charts, digital media",
            "Reading stamina: extended literary and informational passages",
            "Grammar: compound-complex sentences",
            "⚠️ Presidents Day: Feb 15",
        ]),
        ("Mar\nArgumentative Writing (Full Essay)", [
            "Developing a clear thesis/claim",
            "Integrating evidence with commentary (quote sandwich)",
            "Addressing counterclaims effectively",
            "Revision strategies: peer review, revision checklist",
            "Editing: grammar, spelling, comma rules",
            "⚠️ Spring Break: Mar 15–19",
        ]),
        ("Apr\nSTAAR Reading Preparation", [
            "STAAR format: paired literary + informational passages",
            "Cross-text synthesis questions",
            "Multiple-choice strategies: eliminating wrong answers",
            "Extended response (short constructed answer)",
            "Grammar review: verb tense, pronoun agreement, apostrophes",
            "★ STAAR Reading: ~Apr 6, 2027",
        ]),
        ("May\nIndependent Reading & Presentations", [
            "Student choice novel / independent reading project",
            "Book reviews and reader-response writing",
            "Oral presentations: organization, eye contact, voice",
            "Digital media project (optional)",
            "Portfolio reflection and goal-setting for Grade 7",
            "⚠️ Last Day: May 28",
        ]),
    ],
    "Science": [
        ("Aug 12–Aug 31\nLab Safety & Scientific Method", [
            "Lab safety rules, symbols, and equipment handling",
            "Scientific method: observation, hypothesis, experiment, analysis",
            "Independent vs. dependent variables; controlled variables",
            "SI units and metric conversions (length, mass, volume, temperature)",
            "Graphing: line graphs, bar graphs, scatter plots",
        ]),
        ("Sep\nMatter & Its Properties", [
            "Physical properties: mass, volume, density, melting/boiling point",
            "States of matter: solid, liquid, gas, plasma",
            "Phase changes: melting, freezing, evaporation, condensation, sublimation",
            "Mixtures vs. pure substances",
            "Elements, compounds, and mixtures",
        ]),
        ("Oct\nChemical & Physical Changes", [
            "Physical changes vs. chemical changes",
            "Evidence of chemical change (color change, gas production, precipitate, energy)",
            "Conservation of mass",
            "Common chemical reactions: combustion, oxidation (rust)",
            "⚠️ Fall Break: Oct 12–16",
        ]),
        ("Nov\nForce, Motion & Energy", [
            "Speed = distance ÷ time; velocity vs. speed",
            "Acceleration: change in speed or direction",
            "Newton's 1st Law: inertia",
            "Newton's 2nd Law: F = ma",
            "Newton's 3rd Law: action-reaction",
            "Balanced vs. unbalanced forces",
            "Simple machines: lever, pulley, inclined plane, wheel-and-axle",
            "⚠️ Thanksgiving Break: Nov 23–27",
        ]),
        ("Dec\nEarth's Structure & Plate Tectonics", [
            "Earth's layers: crust, mantle, outer core, inner core",
            "Continental drift theory: evidence (fossil records, fit of continents)",
            "Plate boundaries: divergent, convergent, transform",
            "Earthquakes: seismic waves, Richter scale, epicenter",
            "Volcanoes: hot spots, ring of fire, types of eruptions",
            "⚠️ Winter Break begins Dec 21",
        ]),
        ("Jan\nRock Cycle & Earth's Resources", [
            "Rock types: igneous, sedimentary, metamorphic — formation and examples",
            "Rock cycle: processes connecting rock types",
            "Weathering, erosion, and deposition",
            "Geologic time scale: eons, eras, periods",
            "Fossils: types, formation, relative vs. absolute dating",
            "Renewable vs. nonrenewable energy resources",
            "⚠️ MLK Day: Jan 19",
        ]),
        ("Feb\nOceans & Atmosphere", [
            "Ocean floor features: continental shelf, trench, mid-ocean ridge",
            "Ocean currents: surface and deep water (thermohaline)",
            "Tides: gravitational pull of moon",
            "Atmosphere layers: troposphere, stratosphere, mesosphere, thermosphere",
            "Weather vs. climate",
            "⚠️ Presidents Day: Feb 15",
        ]),
        ("Mar\nCells & Living Systems", [
            "Cell theory: three principles",
            "Cell organelles: nucleus, mitochondria, cell membrane, cell wall, chloroplast, vacuole",
            "Plant vs. animal cells: similarities and differences",
            "Cell processes: photosynthesis (intro), respiration (intro)",
            "Levels of organization: cell → tissue → organ → organ system → organism",
            "⚠️ Spring Break: Mar 15–19",
        ]),
        ("Apr\nEcosystems & STAAR Prep", [
            "Biotic vs. abiotic factors in an ecosystem",
            "Producers, consumers (primary/secondary/tertiary), decomposers",
            "Food chains and food webs — energy flow",
            "Energy pyramid: 10% rule",
            "Biogeochemical cycles: water cycle, carbon cycle, nitrogen cycle",
            "Population dynamics: limiting factors, carrying capacity",
            "★ Science benchmark assessment ~April",
        ]),
        ("May\nHuman Body & Year Review", [
            "Body systems overview: digestive, circulatory, respiratory, skeletal, muscular",
            "Body system interactions",
            "Human impact on ecosystems: pollution, habitat loss, invasive species",
            "Environmental stewardship and conservation",
            "Year-end review across all science units",
            "⚠️ Last Day: May 28",
        ]),
    ],
    "Social Studies": [
        ("Aug 12–Aug 31\nGeography Tools & Foundations", [
            "5 Themes of Geography: Location, Place, Human-Environment Interaction, Movement, Region",
            "Types of maps: physical, political, thematic, topographic",
            "Map elements: scale, legend, compass rose, latitude/longitude",
            "Time and chronology: BC/AD, BCE/CE; reading timelines",
            "Primary vs. secondary sources",
        ]),
        ("Sep\nMesopotamia & Ancient Near East", [
            "Tigris-Euphrates River Valley: geographic advantages",
            "Sumerians: first civilization, city-states, ziggurats, cuneiform writing",
            "Hammurabi's Code: rule of law and justice",
            "Babylonian, Assyrian, and Persian empires",
            "Cultural contributions: wheel, plow, number system (base-60)",
        ]),
        ("Oct\nAncient Egypt", [
            "Nile River: flooding, silt, and agriculture",
            "Social structure: pharaoh, priests, scribes, farmers, slaves",
            "Egyptian religion: polytheism, gods/goddesses, afterlife",
            "Mummification and the Book of the Dead",
            "Hieroglyphics, papyrus, and the Rosetta Stone",
            "Pyramids, sphinx, and monument architecture",
            "⚠️ Fall Break: Oct 12–16",
        ]),
        ("Nov\nAncient India & China", [
            "Indus Valley civilization: Harappa and Mohenjo-daro, urban planning",
            "Aryan migration and Vedic culture",
            "Hinduism: origins, Vedas, dharma, karma, caste system, reincarnation",
            "Buddhism: Siddhartha Gautama, Four Noble Truths, Eightfold Path",
            "Maurya Empire: Asoka's conversion and spread of Buddhism",
            "Yellow River (Huang He) civilization, Chinese dynasties: Shang, Zhou, Qin, Han",
            "Chinese inventions: paper, silk, gunpowder, compass",
            "Silk Road trade routes",
            "⚠️ Thanksgiving Break: Nov 23–27",
        ]),
        ("Dec\nWorld Religions Overview", [
            "Judaism: monotheism, Torah, Ten Commandments, covenant with God",
            "Christianity: Jesus of Nazareth, New Testament, spread through Roman Empire",
            "Islam: Muhammad, Quran, Five Pillars, spread across Middle East/Africa/Asia",
            "Hinduism & Buddhism (review and compare)",
            "Comparing world religions: origins, sacred texts, beliefs, practices",
            "Geographic distribution of world religions",
            "⚠️ Winter Break begins Dec 21",
        ]),
        ("Jan\nAncient Greece", [
            "Greek geography: peninsula, islands, city-states (polis)",
            "Athens vs. Sparta: government, culture, values",
            "Athenian democracy: citizens, assembly, direct democracy",
            "Persian Wars: Battle of Marathon, Thermopylae, Salamis",
            "Golden Age of Athens: Pericles, Parthenon, philosophy",
            "Greek philosophers: Socrates, Plato, Aristotle",
            "Alexander the Great and Hellenistic spread of Greek culture",
            "⚠️ MLK Day: Jan 19",
        ]),
        ("Feb\nAncient Rome", [
            "Roman geography: Italian peninsula, Mediterranean Sea advantages",
            "Roman Republic: Senate, consuls, patricians vs. plebeians",
            "Julius Caesar: rise and assassination",
            "Roman Empire: Augustus Caesar and Pax Romana",
            "Roman contributions: law (12 Tables), Latin language, aqueducts, roads",
            "Rise of Christianity within the Roman Empire",
            "Fall of Rome: internal conflict, barbarian invasions",
            "⚠️ Presidents Day: Feb 15",
        ]),
        ("Mar\nMedieval World & Byzantine Empire", [
            "Byzantine Empire: Eastern Roman Empire, Constantinople, Justinian Code",
            "Islamic Golden Age: advances in math, science, medicine, astronomy",
            "Medieval Europe: feudal system (king → lord → knight → serf)",
            "The Church in medieval life: monasteries, cathedrals, clergy",
            "The Crusades: causes, major events, effects on trade and culture",
            "Magna Carta: limits on royal power",
            "⚠️ Spring Break: Mar 15–19",
        ]),
        ("Apr\nExploration & Early Americas", [
            "Age of Exploration: motivations (God, Gold, Glory)",
            "Key explorers: Columbus, Vasco da Gama, Magellan",
            "Columbian Exchange: foods, plants, animals, diseases",
            "Early civilizations of the Americas: Maya, Aztec, Inca",
            "Spanish conquest and colonization impacts",
            "Document analysis: maps, treaties, primary sources",
        ]),
        ("May\nReview & Synthesis", [
            "Themes across civilizations: government, economy, culture, technology",
            "Comparing ancient and modern systems",
            "Current events connections to world history",
            "Social studies research project presentations",
            "Year-end review: geography, history, economics, culture",
            "⚠️ Last Day: May 28",
        ]),
    ],
}

# ── STAAR test subjects for Grade 6 ──────────────────────────────────────────
STAAR_INFO = {
    "Reading / ELA": {
        "estimated_date": "~April 6, 2027",
        "format": "Literary + Informational passages, multiple-choice + short written response",
        "key_readiness_standards": [
            "6.8 — Comprehension of literary text",
            "6.9 — Comprehension of informational text",
            "6.10 — Author's purpose and craft",
            "6.5 — Response skills (evidence-based answers)",
        ],
    },
    "Math": {
        "estimated_date": "~April 8, 2027",
        "format": "Multiple-choice + gridded response, calculator allowed for most sections",
        "key_readiness_standards": [
            "6.3 — Operations with integers and rational numbers",
            "6.4 — Proportionality (ratios, rates, percents)",
            "6.7 — Expressions, equations, inequalities",
            "6.8 — Geometry (area, volume)",
            "6.12 — Statistical measures and data representations",
        ],
    },
}

# ── Quick reference: subject → TEA standard code ─────────────────────────────
TEA_CODES = {
    "Math":           "§111.26 — Grade 6, Adopted 2012, Effective 2014",
    "ELA":            "§110.23 — Grade 6, Adopted 2017, Effective 2019",
    "Science":        "§112.18 — Grade 6, Adopted 2010 (revised 2018)",
    "Social Studies": "§113.18 — Grade 6, Adopted 2018",
}


def month_key(label: str) -> str:
    """Extract 3-letter month abbreviation from a month label string."""
    return label.split()[0][:3]


# ── STAAR strand / TEA TEKS mapping per month ─────────────────────────────────
# Math/ELA: STAAR readiness standard codes  |  Science/SS: TEA TEKS section refs
STAAR_STRAND_MAP: dict[str, dict[str, str]] = {
    "Math": {
        "Aug": "",
        "Sep": "6.3 — Integer & Rational Ops",
        "Oct": "6.4 — Proportionality",
        "Nov": "6.4 — Proportionality",
        "Dec": "6.7 — Expressions",
        "Jan": "6.7 — Equations & Inequalities",
        "Feb": "6.8 — Geometry",
        "Mar": "6.8 — Geometry",
        "Apr": "6.12 — Data Analysis",
        "May": "6.14 — Financial Literacy",
    },
    "ELA": {
        "Aug": "6.8 — Literary Text",
        "Sep": "6.8 — Literary Text",
        "Oct": "6.9 — Informational Text",
        "Nov": "6.9 — Info Text | 6.10 — Author's Craft",
        "Dec": "6.10 — Author's Craft",
        "Jan": "6.8 — Literary Text (Poetry/Drama)",
        "Feb": "6.8 + 6.9 | 6.5 — Response Skills",
        "Mar": "6.10 — Composition",
        "Apr": "6.8 + 6.9 + 6.10 + 6.5 — Full Review",
        "May": "6.8 — Literary Text",
    },
    "Science": {
        "Aug": "§112.18(b)(1-3) — Scientific Investigation",
        "Sep": "§112.18(b)(5) — Physical Properties",
        "Oct": "§112.18(b)(5) — Chemical Changes",
        "Nov": "§112.18(b)(6) — Force, Motion & Energy",
        "Dec": "§112.18(b)(8) — Earth's Structure",
        "Jan": "§112.18(b)(7) — Earth Materials",
        "Feb": "§112.18(b)(8) — Atmosphere & Oceans",
        "Mar": "§112.18(b)(11) — Cells & Organisms",
        "Apr": "§112.18(b)(12) — Ecosystems",
        "May": "§112.18(b)(11) — Human Body",
    },
    "Social Studies": {
        "Aug": "§113.18(b)(17-18) — Geography",
        "Sep": "§113.18(b)(1) — History",
        "Oct": "§113.18(b)(1) — History",
        "Nov": "§113.18(b)(1) — History | (b)(22) — Culture",
        "Dec": "§113.18(b)(22) — Culture & Religion",
        "Jan": "§113.18(b)(1) — History | (b)(14) — Govt",
        "Feb": "§113.18(b)(1) — History | (b)(14) — Govt",
        "Mar": "§113.18(b)(1-2) — History",
        "Apr": "§113.18(b)(3) — History | (b)(9) — Economics",
        "May": "All Strands — Review & Synthesis",
    },
}

# ── Curated monthly resources: Khan Academy, YouTube, other free sources ──────
# Keyed by subject → 3-letter month abbreviation → list of resource dicts
# Each resource: {"title": str, "url": str, "source": str}
_KA_MATH = "https://www.khanacademy.org/math/cc-sixth-grade-math"
_KA_HUM  = "https://www.khanacademy.org/humanities"
_KA_WH   = "https://www.khanacademy.org/humanities/world-history"
_YT      = "https://www.youtube.com/results?search_query="
_CK12    = "https://www.ck12.org"

MONTHLY_RESOURCES: dict[str, dict[str, list[dict]]] = {
    "Math": {
        "Aug": [
            {"title": "6th Grade Math — Full Hub", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "5th→6th Grade Math Review", "url": _YT + "6th+grade+math+review+rational+numbers", "source": "YouTube"},
        ],
        "Sep": [
            {"title": "Negative Numbers & Fractions", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Multiply & Divide Fractions", "url": _YT + "multiplying+dividing+fractions+6th+grade", "source": "YouTube"},
            {"title": "Rational Numbers Practice", "url": "https://www.ixl.com/math/grade-6", "source": "IXL"},
        ],
        "Oct": [
            {"title": "Ratios & Rates", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Unit Rates & Ratio Tables", "url": _YT + "unit+rates+ratio+tables+6th+grade", "source": "YouTube"},
            {"title": "Scale Drawings", "url": _YT + "scale+drawings+proportions+6th+grade", "source": "YouTube"},
        ],
        "Nov": [
            {"title": "Percentages", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Percent Word Problems (Tax, Tip, Discount)", "url": _YT + "percent+word+problems+tax+tip+discount+6th+grade", "source": "YouTube"},
            {"title": "Simple Interest", "url": _YT + "simple+interest+6th+grade+math", "source": "YouTube"},
        ],
        "Dec": [
            {"title": "Expressions & Variables", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Writing Algebraic Expressions", "url": _YT + "writing+algebraic+expressions+6th+grade", "source": "YouTube"},
            {"title": "Tables & Graphs — Relationships", "url": _YT + "independent+dependent+variables+6th+grade+math", "source": "YouTube"},
        ],
        "Jan": [
            {"title": "Equations & Inequalities", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "One-Step Equations (all operations)", "url": _YT + "one+step+equations+6th+grade+math", "source": "YouTube"},
            {"title": "Graphing Inequalities on Number Line", "url": _YT + "inequalities+number+line+6th+grade", "source": "YouTube"},
        ],
        "Feb": [
            {"title": "Geometry — Area & Surface Area", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Area of Composite Figures", "url": _YT + "area+composite+figures+6th+grade", "source": "YouTube"},
            {"title": "Surface Area & Nets", "url": _YT + "surface+area+nets+rectangular+triangular+prism", "source": "YouTube"},
        ],
        "Mar": [
            {"title": "Geometry — Volume & Coordinate Plane", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Coordinate Plane — All 4 Quadrants", "url": _YT + "coordinate+plane+4+quadrants+6th+grade", "source": "YouTube"},
            {"title": "Volume Fractional Dimensions", "url": _YT + "volume+rectangular+prism+fractions+6th+grade", "source": "YouTube"},
        ],
        "Apr": [
            {"title": "Statistics & Data Analysis", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Mean, Median, Mode, IQR, Box Plots", "url": _YT + "mean+median+mode+IQR+box+plot+6th+grade", "source": "YouTube"},
            {"title": "STAAR Math Practice Tests", "url": "https://tea.texas.gov/student-assessment/testing/staar/staar-released-test-questions", "source": "TEA.gov"},
        ],
        "May": [
            {"title": "Personal Finance — Grades 6-8", "url": _KA_MATH, "source": "Khan Academy"},
            {"title": "Payroll, Taxes & Savings — Kids", "url": _YT + "financial+literacy+6th+grade+payroll+taxes", "source": "YouTube"},
            {"title": "Credit Scores & Budgeting Basics", "url": _YT + "credit+scores+budgeting+middle+school", "source": "YouTube"},
        ],
    },
    "ELA": {
        "Aug": [
            {"title": "Grammar Foundations", "url": _KA_HUM + "/grammar", "source": "Khan Academy"},
            {"title": "Literary Elements — Plot, Character, Theme", "url": _YT + "literary+elements+grade+6+plot+character+theme", "source": "YouTube"},
            {"title": "Free Reading Passages", "url": "https://www.commonlit.org", "source": "CommonLit"},
        ],
        "Sep": [
            {"title": "Point of View — 1st vs. 3rd Person", "url": _YT + "point+of+view+first+third+person+6th+grade+ELA", "source": "YouTube"},
            {"title": "Figurative Language (Simile, Metaphor)", "url": _YT + "figurative+language+simile+metaphor+grade+6", "source": "YouTube"},
            {"title": "Personal Narrative Writing Tips", "url": _YT + "personal+narrative+writing+6th+grade", "source": "YouTube"},
        ],
        "Oct": [
            {"title": "Main Idea & Supporting Details", "url": _KA_HUM, "source": "Khan Academy"},
            {"title": "Text Structures (Cause/Effect, Compare)", "url": _YT + "text+structures+cause+effect+compare+contrast+6th+grade", "source": "YouTube"},
            {"title": "Informational Essay Writing", "url": _YT + "informational+essay+writing+6th+grade", "source": "YouTube"},
        ],
        "Nov": [
            {"title": "Evaluating Sources & MLA Citation", "url": _YT + "MLA+citation+grade+6+middle+school", "source": "YouTube"},
            {"title": "MLA Format Guide", "url": "https://owl.purdue.edu/owl/research_and_citation/mla_style/mla_formatting_and_style_guide/mla_general_format.html", "source": "Purdue OWL"},
            {"title": "Avoiding Plagiarism", "url": _YT + "avoiding+plagiarism+6th+grade", "source": "YouTube"},
        ],
        "Dec": [
            {"title": "Argument Writing — Claim, Evidence, Reasoning", "url": _YT + "argumentative+writing+claim+evidence+reasoning+middle+school", "source": "YouTube"},
            {"title": "Evaluating Arguments & Counterclaims", "url": _YT + "counterclaim+rebuttal+argumentative+essay+6th+grade", "source": "YouTube"},
            {"title": "Connotation vs. Denotation", "url": _YT + "connotation+denotation+6th+grade+ELA", "source": "YouTube"},
        ],
        "Jan": [
            {"title": "Figurative Language in Poetry", "url": _YT + "figurative+language+poetry+6th+grade+personification+alliteration", "source": "YouTube"},
            {"title": "Poetic Structure — Stanza, Rhyme, Free Verse", "url": _YT + "poetry+elements+stanza+rhyme+scheme+free+verse+grade+6", "source": "YouTube"},
            {"title": "Drama — Acts, Scenes, Stage Directions", "url": _YT + "drama+elements+acts+scenes+stage+directions+middle+school", "source": "YouTube"},
        ],
        "Feb": [
            {"title": "Making Inferences from Evidence", "url": _YT + "making+inferences+textual+evidence+6th+grade", "source": "YouTube"},
            {"title": "Context Clues Strategies", "url": _YT + "context+clues+vocabulary+6th+grade+ELA", "source": "YouTube"},
            {"title": "Reading Comprehension Practice", "url": "https://www.readworks.org", "source": "ReadWorks"},
        ],
        "Mar": [
            {"title": "Argumentative Essay — Full Draft", "url": _YT + "argumentative+essay+writing+full+draft+middle+school", "source": "YouTube"},
            {"title": "Quote Sandwich — Integrating Evidence", "url": _YT + "quote+sandwich+integrating+evidence+essay", "source": "YouTube"},
            {"title": "Peer Review & Revision Strategies", "url": _YT + "peer+review+revision+writing+middle+school", "source": "YouTube"},
        ],
        "Apr": [
            {"title": "STAAR Reading — Paired Passages Practice", "url": _YT + "STAAR+reading+paired+passages+6th+grade", "source": "YouTube"},
            {"title": "STAAR Released Tests (Official)", "url": "https://tea.texas.gov/student-assessment/testing/staar/staar-released-test-questions", "source": "TEA.gov"},
            {"title": "Multiple-Choice Test Strategies", "url": _YT + "STAAR+reading+test+taking+strategies+eliminate+wrong+answers", "source": "YouTube"},
        ],
        "May": [
            {"title": "Book Recommendations — Grade 6", "url": "https://www.goodreads.com/list/show/43.Best_Books_for_Middle_Schoolers_Grades_6_8_", "source": "Goodreads"},
            {"title": "Book Review Writing", "url": _YT + "how+to+write+a+book+review+middle+school", "source": "YouTube"},
            {"title": "Oral Presentation Tips", "url": _YT + "oral+presentation+tips+middle+school+students", "source": "YouTube"},
        ],
    },
    "Science": {
        "Aug": [
            {"title": "Scientific Method for Middle School", "url": _YT + "scientific+method+middle+school+hypothesis+variables", "source": "YouTube"},
            {"title": "Lab Safety Rules & Equipment", "url": _YT + "lab+safety+rules+middle+school+science", "source": "YouTube"},
            {"title": "Metric System & SI Units", "url": _YT + "metric+system+SI+units+middle+school", "source": "YouTube"},
        ],
        "Sep": [
            {"title": "Crash Course Chemistry — Matter", "url": _YT + "crash+course+chemistry+matter+states", "source": "YouTube (Crash Course)"},
            {"title": "Physical Properties & States of Matter", "url": _YT + "physical+properties+states+of+matter+6th+grade+science", "source": "YouTube"},
            {"title": "Matter & Properties", "url": _CK12 + "/physical-science/", "source": "CK-12"},
        ],
        "Oct": [
            {"title": "Physical vs. Chemical Changes", "url": _YT + "physical+vs+chemical+changes+evidence+middle+school", "source": "YouTube"},
            {"title": "Conservation of Mass", "url": _YT + "conservation+of+mass+law+middle+school+science", "source": "YouTube"},
            {"title": "Chemical Reactions — Evidence", "url": _YT + "evidence+of+chemical+reactions+combustion+oxidation", "source": "YouTube"},
        ],
        "Nov": [
            {"title": "Crash Course Physics — Newton's Laws", "url": _YT + "crash+course+physics+newton+laws+force+motion", "source": "YouTube (Crash Course)"},
            {"title": "Speed, Velocity & Acceleration", "url": _YT + "speed+velocity+acceleration+6th+grade+science", "source": "YouTube"},
            {"title": "Simple Machines", "url": _YT + "simple+machines+lever+pulley+inclined+plane+middle+school", "source": "YouTube"},
        ],
        "Dec": [
            {"title": "Crash Course Earth Science — Plate Tectonics", "url": _YT + "crash+course+earth+science+plate+tectonics", "source": "YouTube (Crash Course)"},
            {"title": "Earth's Layers & Continental Drift", "url": _YT + "earth+layers+continental+drift+evidence+middle+school", "source": "YouTube"},
            {"title": "Earthquakes & Volcanoes", "url": _YT + "earthquakes+volcanoes+plate+boundaries+middle+school", "source": "YouTube"},
        ],
        "Jan": [
            {"title": "Rock Cycle Explained", "url": _YT + "rock+cycle+igneous+sedimentary+metamorphic+middle+school", "source": "YouTube"},
            {"title": "Weathering, Erosion & Deposition", "url": _YT + "weathering+erosion+deposition+6th+grade+science", "source": "YouTube"},
            {"title": "Geologic Time Scale", "url": _YT + "geologic+time+scale+eons+eras+periods+middle+school", "source": "YouTube"},
        ],
        "Feb": [
            {"title": "Ocean Floor Features & Currents", "url": _YT + "ocean+floor+features+currents+thermohaline+middle+school", "source": "YouTube"},
            {"title": "Atmosphere Layers", "url": _YT + "atmosphere+layers+troposphere+stratosphere+middle+school", "source": "YouTube"},
            {"title": "Weather vs. Climate", "url": _YT + "weather+vs+climate+difference+middle+school+science", "source": "YouTube"},
        ],
        "Mar": [
            {"title": "Crash Course Biology — Cells", "url": _YT + "crash+course+biology+cells+organelles", "source": "YouTube (Crash Course)"},
            {"title": "Cell Organelles — Plant vs. Animal Cells", "url": _YT + "cell+organelles+plant+vs+animal+cell+middle+school", "source": "YouTube"},
            {"title": "Levels of Organization", "url": _YT + "levels+of+organization+cell+tissue+organ+system+organism", "source": "YouTube"},
        ],
        "Apr": [
            {"title": "Crash Course Ecology — Food Webs", "url": _YT + "crash+course+ecology+food+webs+energy+pyramid", "source": "YouTube (Crash Course)"},
            {"title": "Biogeochemical Cycles (Water, Carbon, Nitrogen)", "url": _YT + "biogeochemical+cycles+water+carbon+nitrogen+middle+school", "source": "YouTube"},
            {"title": "Population Dynamics & Carrying Capacity", "url": _YT + "population+dynamics+limiting+factors+carrying+capacity", "source": "YouTube"},
        ],
        "May": [
            {"title": "Human Body Systems Overview", "url": _YT + "human+body+systems+overview+6th+grade+science", "source": "YouTube"},
            {"title": "Human Impact on Ecosystems", "url": _YT + "human+impact+on+ecosystems+pollution+habitat+loss", "source": "YouTube"},
            {"title": "Environmental Conservation", "url": _YT + "environmental+conservation+stewardship+middle+school", "source": "YouTube"},
        ],
    },
    "Social Studies": {
        "Aug": [
            {"title": "5 Themes of Geography", "url": _YT + "5+themes+of+geography+location+place+region+movement", "source": "YouTube"},
            {"title": "Types of Maps & Map Elements", "url": _YT + "types+of+maps+physical+political+thematic+middle+school", "source": "YouTube"},
            {"title": "World History Hub", "url": _KA_WH, "source": "Khan Academy"},
        ],
        "Sep": [
            {"title": "Crash Course — Mesopotamia", "url": _YT + "crash+course+world+history+mesopotamia+sumerians", "source": "YouTube (Crash Course)"},
            {"title": "Hammurabi's Code & Rule of Law", "url": _YT + "hammurabi+code+rule+of+law+ancient+mesopotamia", "source": "YouTube"},
            {"title": "Ancient Mesopotamia", "url": _KA_WH + "/ancient-mesopotamia", "source": "Khan Academy"},
        ],
        "Oct": [
            {"title": "Crash Course — Ancient Egypt", "url": _YT + "crash+course+world+history+ancient+egypt", "source": "YouTube (Crash Course)"},
            {"title": "Ancient Egypt — Society & Religion", "url": _YT + "ancient+egypt+social+structure+pharaoh+religion+6th+grade", "source": "YouTube"},
            {"title": "Ancient Egypt", "url": _KA_WH + "/ancient-egypt", "source": "Khan Academy"},
        ],
        "Nov": [
            {"title": "Crash Course — Ancient India & China", "url": _YT + "crash+course+world+history+india+china+hinduism+buddhism", "source": "YouTube (Crash Course)"},
            {"title": "Silk Road Trade Routes", "url": _YT + "silk+road+trade+routes+ancient+china+world+history", "source": "YouTube"},
            {"title": "Ancient India & China", "url": _KA_WH, "source": "Khan Academy"},
        ],
        "Dec": [
            {"title": "Crash Course — World Religions", "url": _YT + "crash+course+world+history+world+religions+judaism+christianity+islam", "source": "YouTube (Crash Course)"},
            {"title": "Comparing World Religions", "url": _YT + "comparing+world+religions+origins+beliefs+practices+6th+grade", "source": "YouTube"},
            {"title": "World Religions Overview", "url": _KA_WH, "source": "Khan Academy"},
        ],
        "Jan": [
            {"title": "Crash Course — Ancient Greece", "url": _YT + "crash+course+world+history+ancient+greece+democracy", "source": "YouTube (Crash Course)"},
            {"title": "Athens vs. Sparta — Government & Culture", "url": _YT + "athens+vs+sparta+government+culture+6th+grade", "source": "YouTube"},
            {"title": "Ancient Greece", "url": _KA_WH + "/ancient-greece", "source": "Khan Academy"},
        ],
        "Feb": [
            {"title": "Crash Course — Ancient Rome", "url": _YT + "crash+course+world+history+ancient+rome+republic+empire", "source": "YouTube (Crash Course)"},
            {"title": "Roman Republic vs. Empire", "url": _YT + "roman+republic+empire+julius+caesar+augustus+6th+grade", "source": "YouTube"},
            {"title": "Ancient Rome", "url": _KA_WH + "/ancient-rome", "source": "Khan Academy"},
        ],
        "Mar": [
            {"title": "Crash Course — Middle Ages", "url": _YT + "crash+course+world+history+middle+ages+feudal+system", "source": "YouTube (Crash Course)"},
            {"title": "Byzantine Empire & Islamic Golden Age", "url": _YT + "byzantine+empire+islamic+golden+age+world+history", "source": "YouTube"},
            {"title": "Medieval Europe & the Crusades", "url": _YT + "medieval+europe+crusades+feudal+system+middle+school", "source": "YouTube"},
        ],
        "Apr": [
            {"title": "Crash Course — Age of Exploration", "url": _YT + "crash+course+world+history+age+of+exploration+columbus", "source": "YouTube (Crash Course)"},
            {"title": "Columbian Exchange", "url": _YT + "columbian+exchange+foods+diseases+plants+animals+6th+grade", "source": "YouTube"},
            {"title": "Maya, Aztec & Inca Civilizations", "url": _YT + "maya+aztec+inca+early+americas+civilization+6th+grade", "source": "YouTube"},
        ],
        "May": [
            {"title": "World History Review — Crash Course", "url": _YT + "crash+course+world+history+review+ancient+civilizations", "source": "YouTube (Crash Course)"},
            {"title": "Comparing Ancient Civilizations", "url": _YT + "comparing+ancient+civilizations+government+economy+culture", "source": "YouTube"},
            {"title": "Social Studies Review Games", "url": "https://quizlet.com/subject/ancient-civilizations/", "source": "Quizlet"},
        ],
    },
}
