"""
Humanities curriculum questions (Literature, History, Philosophy)
"""

LITERATURE_QUESTIONS = [
    # READING COMPREHENSION
    {"skill": "reading_comprehension", "difficulty": "easy", "type": "free_text", "question": "What is the main idea of a passage?", "answer": "the central point or message the author wants to convey", "explanation": "The main idea is what the passage is mostly about.", "acceptable_answers": ["central point", "main message", "what the passage is about"]},
    {"skill": "reading_comprehension", "difficulty": "medium", "type": "multiple_choice", "question": "What does 'inference' mean in reading?", "options": ["Copying text exactly", "Drawing conclusions from clues", "Guessing randomly", "Summarizing"], "answer": "B", "explanation": "Inference means using evidence to figure out unstated information."},
    
    # VOCABULARY
    {"skill": "vocabulary", "difficulty": "easy", "type": "free_text", "question": "What is a synonym?", "answer": "a word with the same or similar meaning", "explanation": "Happy and joyful are synonyms.", "acceptable_answers": ["word with same meaning", "similar word", "word meaning the same thing"]},
    {"skill": "vocabulary", "difficulty": "easy", "type": "free_text", "question": "What is an antonym?", "answer": "a word with the opposite meaning", "explanation": "Hot and cold are antonyms.", "acceptable_answers": ["opposite word", "word with opposite meaning"]},
    {"skill": "vocabulary", "difficulty": "medium", "type": "multiple_choice", "question": "What does 'benevolent' mean?", "options": ["Evil", "Kind and generous", "Angry", "Tired"], "answer": "B", "explanation": "Benevolent means well-meaning and kindly."},
    
    # GRAMMAR
    {"skill": "grammar", "difficulty": "easy", "type": "multiple_choice", "question": "Which is a proper noun?", "options": ["city", "country", "London", "river"], "answer": "C", "explanation": "London is a proper noun - a specific name requiring capitalization."},
    {"skill": "grammar", "difficulty": "easy", "type": "free_text", "question": "What type of word describes a noun?", "answer": "adjective", "explanation": "Adjectives modify nouns (e.g., 'blue' sky, 'tall' building).", "acceptable_answers": ["adjective", "an adjective"]},
    {"skill": "grammar", "difficulty": "medium", "type": "multiple_choice", "question": "Identify the verb: 'The cat sleeps on the couch.'", "options": ["cat", "sleeps", "on", "couch"], "answer": "B", "explanation": "Sleeps is the action the cat is doing."},
    
    # LITERARY DEVICES
    {"skill": "literary_devices", "difficulty": "easy", "type": "free_text", "question": "What is a simile?", "answer": "a comparison using 'like' or 'as'", "explanation": "Example: 'He ran like the wind.'", "acceptable_answers": ["comparison using like or as", "comparing with like or as"]},
    {"skill": "literary_devices", "difficulty": "easy", "type": "free_text", "question": "What is a metaphor?", "answer": "a direct comparison without using like or as", "explanation": "Example: 'Life is a journey.'", "acceptable_answers": ["direct comparison", "comparison without like or as"]},
    {"skill": "literary_devices", "difficulty": "medium", "type": "multiple_choice", "question": "'The wind whispered through the trees' is an example of:", "options": ["Simile", "Metaphor", "Personification", "Alliteration"], "answer": "C", "explanation": "Personification gives human qualities to non-human things."},
    {"skill": "literary_devices", "difficulty": "medium", "type": "free_text", "question": "What is alliteration?", "answer": "repetition of initial consonant sounds", "explanation": "Example: 'Peter Piper picked a peck of pickled peppers.'", "acceptable_answers": ["same starting sound", "repetition of beginning sounds", "repeated consonant sounds"]},
    
    # POETRY ANALYSIS
    {"skill": "poetry_analysis", "difficulty": "easy", "type": "free_text", "question": "What is rhyme?", "answer": "words that have the same ending sound", "explanation": "Cat and hat rhyme because they both end in '-at'.", "acceptable_answers": ["same ending sounds", "matching sounds at end of words"]},
    {"skill": "poetry_analysis", "difficulty": "medium", "type": "free_text", "question": "What is a stanza?", "answer": "a group of lines in a poem", "explanation": "Stanzas are like paragraphs in poetry.", "acceptable_answers": ["group of lines", "verse", "paragraph of a poem"]},
    {"skill": "poetry_analysis", "difficulty": "medium", "type": "numeric", "question": "How many lines does a sonnet have?", "answer": "14", "explanation": "Traditional sonnets have 14 lines."},
    
    # FICTION ANALYSIS
    {"skill": "fiction_analysis", "difficulty": "easy", "type": "free_text", "question": "What is the setting of a story?", "answer": "the time and place where the story happens", "explanation": "Setting includes when and where the story takes place.", "acceptable_answers": ["time and place", "where and when", "location and time"]},
    {"skill": "fiction_analysis", "difficulty": "easy", "type": "free_text", "question": "What is the plot of a story?", "answer": "the sequence of events", "explanation": "Plot is what happens in the story from beginning to end.", "acceptable_answers": ["sequence of events", "what happens", "story events"]},
    {"skill": "fiction_analysis", "difficulty": "medium", "type": "free_text", "question": "What is the climax of a story?", "answer": "the turning point or most exciting moment", "explanation": "The climax is the peak of tension in the story.", "acceptable_answers": ["turning point", "highest point of tension", "most dramatic moment"]},
    {"skill": "fiction_analysis", "difficulty": "medium", "type": "multiple_choice", "question": "What is the conflict in a story?", "options": ["The ending", "The main problem or struggle", "The setting", "The dialogue"], "answer": "B", "explanation": "Conflict is the central problem the characters face."},
]

HISTORY_QUESTIONS = [
    # ANCIENT CIVILIZATIONS
    {"skill": "ancient_civilizations", "difficulty": "easy", "type": "free_text", "question": "Where did ancient Egyptian civilization develop?", "answer": "along the Nile River", "explanation": "The Nile provided water, fertile soil, and transportation.", "acceptable_answers": ["Nile River", "along the Nile", "Egypt", "Nile Valley"]},
    {"skill": "ancient_civilizations", "difficulty": "easy", "type": "free_text", "question": "What is Mesopotamia often called?", "answer": "the cradle of civilization", "explanation": "Some of the earliest civilizations developed in Mesopotamia.", "acceptable_answers": ["cradle of civilization", "birthplace of civilization"]},
    {"skill": "ancient_civilizations", "difficulty": "medium", "type": "multiple_choice", "question": "Who built the Great Pyramid of Giza?", "options": ["Greeks", "Romans", "Egyptians", "Persians"], "answer": "C", "explanation": "Ancient Egyptians built the pyramids as tombs for pharaohs."},
    {"skill": "ancient_civilizations", "difficulty": "medium", "type": "free_text", "question": "What writing system did the Egyptians use?", "answer": "hieroglyphics", "explanation": "Hieroglyphics used pictures and symbols to represent words and sounds.", "acceptable_answers": ["hieroglyphics", "hieroglyphs"]},
    
    # CLASSICAL ERA
    {"skill": "classical_era", "difficulty": "easy", "type": "free_text", "question": "What form of government originated in ancient Athens?", "answer": "democracy", "explanation": "Athens developed the first known democracy around 500 BCE.", "acceptable_answers": ["democracy", "democratic government"]},
    {"skill": "classical_era", "difficulty": "medium", "type": "free_text", "question": "Who was Alexander the Great?", "answer": "Greek king who conquered a vast empire", "explanation": "Alexander created one of history's largest empires by age 30.", "acceptable_answers": ["Greek conqueror", "Macedonian king", "king who built a huge empire"]},
    {"skill": "classical_era", "difficulty": "medium", "type": "multiple_choice", "question": "What language spread throughout the Roman Empire?", "options": ["Greek", "Latin", "Arabic", "Hebrew"], "answer": "B", "explanation": "Latin was the official language of the Roman Empire."},
    {"skill": "classical_era", "difficulty": "hard", "type": "numeric", "question": "In what year did the Roman Empire fall in the West? (approximate)", "answer": "476", "explanation": "476 CE is traditionally given as the fall of the Western Roman Empire."},
    
    # MEDIEVAL PERIOD
    {"skill": "medieval_period", "difficulty": "easy", "type": "free_text", "question": "What system organized medieval European society?", "answer": "feudalism", "explanation": "Feudalism was based on land ownership and loyalty relationships.", "acceptable_answers": ["feudalism", "feudal system"]},
    {"skill": "medieval_period", "difficulty": "medium", "type": "free_text", "question": "What were the Crusades?", "answer": "religious wars to reclaim the Holy Land", "explanation": "European Christians fought to take Jerusalem from Muslim control.", "acceptable_answers": ["religious wars", "wars for the Holy Land", "Christian military campaigns"]},
    {"skill": "medieval_period", "difficulty": "medium", "type": "free_text", "question": "What was the Black Death?", "answer": "a plague that killed millions in Europe", "explanation": "The Black Death (1347-1351) killed about 1/3 of Europe's population.", "acceptable_answers": ["plague", "bubonic plague", "deadly disease"]},
    
    # RENAISSANCE
    {"skill": "renaissance", "difficulty": "easy", "type": "free_text", "question": "What does 'Renaissance' mean?", "answer": "rebirth", "explanation": "The Renaissance was a 'rebirth' of classical learning and arts.", "acceptable_answers": ["rebirth", "revival", "reawakening"]},
    {"skill": "renaissance", "difficulty": "medium", "type": "free_text", "question": "Where did the Renaissance begin?", "answer": "Italy", "explanation": "The Renaissance started in Italian city-states like Florence.", "acceptable_answers": ["Italy", "Florence", "Italian city-states"]},
    {"skill": "renaissance", "difficulty": "medium", "type": "multiple_choice", "question": "Who painted the Mona Lisa?", "options": ["Michelangelo", "Raphael", "Leonardo da Vinci", "Botticelli"], "answer": "C", "explanation": "Leonardo da Vinci painted the Mona Lisa around 1503-1519."},
    
    # AGE OF EXPLORATION
    {"skill": "age_of_exploration", "difficulty": "easy", "type": "free_text", "question": "Who sailed to the Americas in 1492?", "answer": "Christopher Columbus", "explanation": "Columbus's voyage opened European exploration of the Americas.", "acceptable_answers": ["Christopher Columbus", "Columbus"]},
    {"skill": "age_of_exploration", "difficulty": "medium", "type": "free_text", "question": "What was the Columbian Exchange?", "answer": "transfer of plants, animals, and diseases between Old and New Worlds", "explanation": "This exchange transformed both hemispheres.", "acceptable_answers": ["exchange between continents", "trading of goods and diseases", "transfer between hemispheres"]},
    {"skill": "age_of_exploration", "difficulty": "medium", "type": "multiple_choice", "question": "Who was the first to circumnavigate the globe?", "options": ["Columbus", "Magellan's expedition", "Vespucci", "Da Gama"], "answer": "B", "explanation": "Magellan's expedition (1519-1522) first sailed around the world."},
    
    # REVOLUTIONS
    {"skill": "revolutions", "difficulty": "easy", "type": "numeric", "question": "In what year did American independence begin? (Declaration)", "answer": "1776", "explanation": "The Declaration of Independence was signed July 4, 1776."},
    {"skill": "revolutions", "difficulty": "medium", "type": "free_text", "question": "What event started the French Revolution?", "answer": "storming of the Bastille", "explanation": "On July 14, 1789, revolutionaries stormed the Bastille prison.", "acceptable_answers": ["storming the Bastille", "Bastille", "attack on Bastille"]},
    {"skill": "revolutions", "difficulty": "medium", "type": "free_text", "question": "What was the Industrial Revolution?", "answer": "shift from hand production to machine manufacturing", "explanation": "It began in Britain around 1760 and transformed society.", "acceptable_answers": ["shift to machines", "mechanization of production", "rise of factories"]},
    
    # WORLD WARS
    {"skill": "world_wars", "difficulty": "easy", "type": "free_text", "question": "What event triggered World War I?", "answer": "assassination of Archduke Franz Ferdinand", "explanation": "He was killed in Sarajevo on June 28, 1914.", "acceptable_answers": ["assassination of Franz Ferdinand", "Franz Ferdinand's death", "Archduke assassination"]},
    {"skill": "world_wars", "difficulty": "medium", "type": "numeric", "question": "What year did World War II end?", "answer": "1945", "explanation": "WWII ended in 1945 with Germany's and Japan's surrender."},
    {"skill": "world_wars", "difficulty": "medium", "type": "free_text", "question": "What was the Holocaust?", "answer": "Nazi genocide of Jews and other groups", "explanation": "About 6 million Jews were murdered by Nazi Germany.", "acceptable_answers": ["Nazi genocide", "murder of Jews by Nazis", "systematic killing by Nazis"]},
    
    # MODERN HISTORY
    {"skill": "modern_history", "difficulty": "easy", "type": "free_text", "question": "What was the Cold War?", "answer": "political tension between US and Soviet Union", "explanation": "It lasted from about 1947 to 1991.", "acceptable_answers": ["US vs USSR conflict", "superpower tension", "rivalry between America and Russia"]},
    {"skill": "modern_history", "difficulty": "medium", "type": "numeric", "question": "When did the Berlin Wall fall?", "answer": "1989", "explanation": "The Berlin Wall fell on November 9, 1989."},
    {"skill": "modern_history", "difficulty": "medium", "type": "free_text", "question": "Who was Martin Luther King Jr.?", "answer": "American civil rights leader", "explanation": "He led the movement for racial equality in the US.", "acceptable_answers": ["civil rights leader", "leader of civil rights movement", "American activist for equality"]},
]

PHILOSOPHY_QUESTIONS = [
    # LOGIC BASICS
    {"skill": "logic_basics", "difficulty": "easy", "type": "multiple_choice", "question": "What is a premise in an argument?", "options": ["The conclusion", "A statement supporting the conclusion", "The topic", "An opinion"], "answer": "B", "explanation": "Premises are statements that provide reasons for the conclusion."},
    {"skill": "logic_basics", "difficulty": "medium", "type": "free_text", "question": "What is a syllogism?", "answer": "a logical argument with two premises and a conclusion", "explanation": "Example: All men are mortal. Socrates is a man. Therefore, Socrates is mortal.", "acceptable_answers": ["argument with premises and conclusion", "logical deduction", "form of deductive reasoning"]},
    
    # ARGUMENTS & REASONING
    {"skill": "arguments", "difficulty": "easy", "type": "free_text", "question": "What is a fallacy?", "answer": "an error in reasoning", "explanation": "Fallacies make arguments invalid or weak.", "acceptable_answers": ["reasoning error", "logical error", "flawed argument"]},
    {"skill": "arguments", "difficulty": "medium", "type": "multiple_choice", "question": "What is an ad hominem fallacy?", "options": ["Attacking evidence", "Attacking the person instead of the argument", "Using emotion", "Circular reasoning"], "answer": "B", "explanation": "Ad hominem attacks the person rather than their argument."},
    
    # ETHICS BASICS
    {"skill": "ethics_basics", "difficulty": "easy", "type": "free_text", "question": "What is ethics?", "answer": "the study of right and wrong", "explanation": "Ethics examines moral principles and values.", "acceptable_answers": ["study of morality", "study of right and wrong", "moral philosophy"]},
    {"skill": "ethics_basics", "difficulty": "medium", "type": "free_text", "question": "What is utilitarianism?", "answer": "the greatest good for the greatest number", "explanation": "Actions are judged by their outcomes/consequences.", "acceptable_answers": ["greatest good for most people", "maximizing happiness", "consequentialist ethics"]},
    
    # PHILOSOPHICAL QUESTIONS
    {"skill": "philosophical_questions", "difficulty": "easy", "type": "free_text", "question": "Who said 'I think, therefore I am'?", "answer": "René Descartes", "explanation": "Descartes used this as a foundation for knowledge.", "acceptable_answers": ["Descartes", "René Descartes"]},
    {"skill": "philosophical_questions", "difficulty": "medium", "type": "free_text", "question": "What is epistemology?", "answer": "the study of knowledge", "explanation": "Epistemology asks: What can we know? How do we know it?", "acceptable_answers": ["study of knowledge", "theory of knowledge"]},
    
    # CRITICAL THINKING
    {"skill": "critical_thinking", "difficulty": "easy", "type": "free_text", "question": "What is confirmation bias?", "answer": "tendency to favor information that confirms existing beliefs", "explanation": "We tend to notice evidence that supports what we already believe.", "acceptable_answers": ["favoring supporting evidence", "seeking confirming information"]},
    {"skill": "critical_thinking", "difficulty": "medium", "type": "multiple_choice", "question": "What is the best way to evaluate an argument?", "options": ["See who made it", "Check if it sounds good", "Examine evidence and logic", "Trust your feelings"], "answer": "C", "explanation": "Good critical thinking focuses on evidence and logical structure."},
]

ALL_HUMANITIES_QUESTIONS = LITERATURE_QUESTIONS + HISTORY_QUESTIONS + PHILOSOPHY_QUESTIONS
