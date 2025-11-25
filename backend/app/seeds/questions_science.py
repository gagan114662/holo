"""
Science curriculum questions (Physics, Chemistry, Biology)
"""

PHYSICS_QUESTIONS = [
    # MOTION BASICS
    {"skill": "motion_basics", "difficulty": "easy", "type": "free_text", "question": "What is the SI unit for distance?", "answer": "meter", "explanation": "The meter (m) is the SI base unit for measuring distance.", "acceptable_answers": ["meter", "meters", "m"]},
    {"skill": "motion_basics", "difficulty": "easy", "type": "multiple_choice", "question": "Which of the following is a vector quantity?", "options": ["Speed", "Distance", "Velocity", "Time"], "answer": "C", "explanation": "Velocity has both magnitude and direction, making it a vector."},
    {"skill": "motion_basics", "difficulty": "easy", "type": "free_text", "question": "What is speed?", "answer": "distance divided by time", "explanation": "Speed = Distance / Time. It measures how fast something moves.", "acceptable_answers": ["distance divided by time", "distance/time", "d/t"]},
    {"skill": "motion_basics", "difficulty": "medium", "type": "numeric", "question": "If a car travels 100 km in 2 hours, what is its average speed in km/h?", "answer": "50", "explanation": "Speed = Distance/Time = 100 km / 2 h = 50 km/h."},
    {"skill": "motion_basics", "difficulty": "medium", "type": "numeric", "question": "A runner covers 400 meters in 50 seconds. What is their speed in m/s?", "answer": "8", "explanation": "Speed = 400 m / 50 s = 8 m/s."},
    
    # VELOCITY & ACCELERATION
    {"skill": "velocity_acceleration", "difficulty": "easy", "type": "free_text", "question": "What is acceleration?", "answer": "change in velocity over time", "explanation": "Acceleration measures how quickly velocity changes.", "acceptable_answers": ["change in velocity over time", "rate of change of velocity", "dv/dt"]},
    {"skill": "velocity_acceleration", "difficulty": "medium", "type": "numeric", "question": "A car accelerates from 0 to 20 m/s in 5 seconds. What is its acceleration?", "answer": "4", "explanation": "Acceleration = (20-0)/5 = 4 m/s²."},
    {"skill": "velocity_acceleration", "difficulty": "medium", "type": "free_text", "question": "What is the acceleration due to gravity on Earth (approximately)?", "answer": "9.8 m/s²", "explanation": "Objects in free fall accelerate at about 9.8 m/s² on Earth.", "acceptable_answers": ["9.8 m/s²", "9.8", "10 m/s²", "10"]},
    {"skill": "velocity_acceleration", "difficulty": "hard", "type": "numeric", "question": "An object falls freely for 3 seconds. How far does it fall? (g = 10 m/s²)", "answer": "45", "explanation": "Distance = ½gt² = ½(10)(3²) = 45 m."},
    
    # FORCES
    {"skill": "forces", "difficulty": "easy", "type": "free_text", "question": "What is the SI unit of force?", "answer": "Newton", "explanation": "Force is measured in Newtons (N), named after Isaac Newton.", "acceptable_answers": ["Newton", "Newtons", "N"]},
    {"skill": "forces", "difficulty": "easy", "type": "multiple_choice", "question": "Which force keeps us on the ground?", "options": ["Friction", "Gravity", "Magnetism", "Tension"], "answer": "B", "explanation": "Gravity pulls objects with mass toward each other."},
    {"skill": "forces", "difficulty": "medium", "type": "numeric", "question": "What force is needed to accelerate a 5 kg mass at 3 m/s²?", "answer": "15", "explanation": "F = ma = 5 × 3 = 15 N."},
    {"skill": "forces", "difficulty": "medium", "type": "free_text", "question": "What is the formula for force?", "answer": "F = ma", "explanation": "Newton's Second Law: Force equals mass times acceleration.", "acceptable_answers": ["F = ma", "F=ma", "force = mass × acceleration"]},
    
    # NEWTON'S LAWS
    {"skill": "newtons_laws", "difficulty": "easy", "type": "free_text", "question": "State Newton's First Law in simple terms.", "answer": "Objects stay at rest or in motion unless acted on by a force", "explanation": "This is the law of inertia.", "acceptable_answers": ["objects at rest stay at rest", "law of inertia", "an object remains at rest or in uniform motion unless acted upon by an external force"]},
    {"skill": "newtons_laws", "difficulty": "medium", "type": "multiple_choice", "question": "According to Newton's Third Law, when you push against a wall:", "options": ["The wall moves", "Nothing happens", "The wall pushes back on you", "You move toward the wall"], "answer": "C", "explanation": "Every action has an equal and opposite reaction."},
    {"skill": "newtons_laws", "difficulty": "medium", "type": "free_text", "question": "Which Newton's law explains why you feel pushed back when a car accelerates?", "answer": "First Law", "explanation": "Inertia causes your body to resist the change in motion.", "acceptable_answers": ["First Law", "Newton's First Law", "first", "inertia"]},
    
    # WORK & ENERGY
    {"skill": "work_energy", "difficulty": "easy", "type": "free_text", "question": "What is the SI unit of energy?", "answer": "Joule", "explanation": "Energy is measured in Joules (J).", "acceptable_answers": ["Joule", "Joules", "J"]},
    {"skill": "work_energy", "difficulty": "easy", "type": "free_text", "question": "What is kinetic energy?", "answer": "energy of motion", "explanation": "Kinetic energy is the energy an object has due to its motion.", "acceptable_answers": ["energy of motion", "energy due to motion", "motion energy"]},
    {"skill": "work_energy", "difficulty": "medium", "type": "numeric", "question": "Calculate the kinetic energy of a 2 kg ball moving at 3 m/s. (KE = ½mv²)", "answer": "9", "explanation": "KE = ½ × 2 × 3² = ½ × 2 × 9 = 9 J."},
    {"skill": "work_energy", "difficulty": "medium", "type": "numeric", "question": "How much work is done when a 10 N force moves an object 5 meters?", "answer": "50", "explanation": "Work = Force × Distance = 10 × 5 = 50 J."},
    {"skill": "work_energy", "difficulty": "hard", "type": "free_text", "question": "What is potential energy?", "answer": "stored energy due to position or condition", "explanation": "Potential energy is energy stored in an object due to its position or state.", "acceptable_answers": ["stored energy", "energy of position", "stored energy due to position"]},
    
    # MOMENTUM
    {"skill": "momentum", "difficulty": "easy", "type": "free_text", "question": "What is the formula for momentum?", "answer": "p = mv", "explanation": "Momentum (p) equals mass (m) times velocity (v).", "acceptable_answers": ["p = mv", "p=mv", "mass times velocity"]},
    {"skill": "momentum", "difficulty": "medium", "type": "numeric", "question": "What is the momentum of a 4 kg ball moving at 5 m/s?", "answer": "20", "explanation": "p = mv = 4 × 5 = 20 kg⋅m/s."},
    {"skill": "momentum", "difficulty": "medium", "type": "free_text", "question": "What is conservation of momentum?", "answer": "total momentum stays constant in a closed system", "explanation": "In the absence of external forces, momentum is conserved.", "acceptable_answers": ["momentum is conserved", "total momentum stays constant", "momentum remains constant"]},
    
    # GRAVITY
    {"skill": "gravity", "difficulty": "easy", "type": "free_text", "question": "Who discovered the law of universal gravitation?", "answer": "Isaac Newton", "explanation": "Newton formulated the law of universal gravitation in the 17th century.", "acceptable_answers": ["Isaac Newton", "Newton"]},
    {"skill": "gravity", "difficulty": "medium", "type": "multiple_choice", "question": "What happens to gravitational force if the distance between two objects doubles?", "options": ["It doubles", "It halves", "It quarters", "It stays the same"], "answer": "C", "explanation": "Gravity follows the inverse square law: F ∝ 1/r²."},
    {"skill": "gravity", "difficulty": "hard", "type": "numeric", "question": "What is the weight of a 60 kg person on Earth? (g = 10 m/s²)", "answer": "600", "explanation": "Weight = mg = 60 × 10 = 600 N."},
    
    # WAVES
    {"skill": "waves", "difficulty": "easy", "type": "free_text", "question": "What is frequency measured in?", "answer": "Hertz", "explanation": "Frequency is measured in Hertz (Hz), representing cycles per second.", "acceptable_answers": ["Hertz", "Hz"]},
    {"skill": "waves", "difficulty": "easy", "type": "multiple_choice", "question": "Which type of wave needs a medium to travel?", "options": ["Electromagnetic wave", "Light wave", "Mechanical wave", "Radio wave"], "answer": "C", "explanation": "Mechanical waves like sound need a medium (solid, liquid, or gas)."},
    {"skill": "waves", "difficulty": "medium", "type": "free_text", "question": "What is wavelength?", "answer": "the distance between two consecutive wave peaks", "explanation": "Wavelength (λ) is the distance from one point on a wave to the corresponding point on the next wave.", "acceptable_answers": ["distance between wave peaks", "distance between crests", "length of one wave cycle"]},
    {"skill": "waves", "difficulty": "medium", "type": "numeric", "question": "If a wave has frequency 5 Hz and wavelength 2 m, what is its speed?", "answer": "10", "explanation": "Wave speed = frequency × wavelength = 5 × 2 = 10 m/s."},
    
    # SOUND
    {"skill": "sound", "difficulty": "easy", "type": "numeric", "question": "Approximately how fast does sound travel in air (in m/s)?", "answer": "343", "explanation": "Sound travels at about 343 m/s in air at room temperature.", "acceptable_answers": ["343", "340", "330"]},
    {"skill": "sound", "difficulty": "easy", "type": "multiple_choice", "question": "Sound cannot travel through:", "options": ["Air", "Water", "Steel", "Vacuum"], "answer": "D", "explanation": "Sound needs a medium to travel; it cannot travel through a vacuum."},
    {"skill": "sound", "difficulty": "medium", "type": "free_text", "question": "What determines the pitch of a sound?", "answer": "frequency", "explanation": "Higher frequency = higher pitch, lower frequency = lower pitch.", "acceptable_answers": ["frequency", "the frequency"]},
    {"skill": "sound", "difficulty": "medium", "type": "free_text", "question": "What is an echo?", "answer": "sound reflected off a surface", "explanation": "An echo occurs when sound bounces off a surface and returns to the listener.", "acceptable_answers": ["reflected sound", "sound reflection", "sound reflected off a surface"]},
    
    # LIGHT & OPTICS
    {"skill": "light_optics", "difficulty": "easy", "type": "numeric", "question": "What is the speed of light in a vacuum (approximately, in million m/s)?", "answer": "300", "explanation": "Light travels at about 300,000,000 m/s (3 × 10⁸ m/s).", "acceptable_answers": ["300", "299", "3"]},
    {"skill": "light_optics", "difficulty": "easy", "type": "multiple_choice", "question": "Which color of light has the longest wavelength?", "options": ["Blue", "Green", "Yellow", "Red"], "answer": "D", "explanation": "Red light has the longest wavelength in the visible spectrum."},
    {"skill": "light_optics", "difficulty": "medium", "type": "free_text", "question": "What is refraction?", "answer": "bending of light when it passes from one medium to another", "explanation": "Light bends when it changes speed moving between different materials.", "acceptable_answers": ["bending of light", "light bending", "change in direction of light"]},
    {"skill": "light_optics", "difficulty": "medium", "type": "multiple_choice", "question": "What type of mirror is used in car rearview mirrors?", "options": ["Plane mirror", "Concave mirror", "Convex mirror", "Spherical mirror"], "answer": "C", "explanation": "Convex mirrors provide a wider field of view."},
    
    # ELECTRICITY
    {"skill": "electricity", "difficulty": "easy", "type": "free_text", "question": "What is the unit of electric current?", "answer": "Ampere", "explanation": "Electric current is measured in Amperes (A).", "acceptable_answers": ["Ampere", "Amperes", "A", "Amp", "Amps"]},
    {"skill": "electricity", "difficulty": "easy", "type": "free_text", "question": "What is Ohm's Law?", "answer": "V = IR", "explanation": "Voltage equals Current times Resistance.", "acceptable_answers": ["V = IR", "V=IR", "voltage equals current times resistance"]},
    {"skill": "electricity", "difficulty": "medium", "type": "numeric", "question": "If a circuit has 12V and 4A, what is the resistance?", "answer": "3", "explanation": "R = V/I = 12/4 = 3 Ohms."},
    {"skill": "electricity", "difficulty": "medium", "type": "numeric", "question": "Calculate the power if V = 10V and I = 3A.", "answer": "30", "explanation": "Power = V × I = 10 × 3 = 30 Watts."},
    {"skill": "electricity", "difficulty": "hard", "type": "free_text", "question": "What happens to total resistance when resistors are connected in series?", "answer": "resistances add up", "explanation": "In series: R_total = R1 + R2 + R3 + ...", "acceptable_answers": ["resistances add up", "they add", "total resistance increases", "add together"]},
    
    # MAGNETISM
    {"skill": "magnetism", "difficulty": "easy", "type": "multiple_choice", "question": "Like magnetic poles:", "options": ["Attract", "Repel", "Have no effect", "Become neutral"], "answer": "B", "explanation": "Like poles (N-N or S-S) repel, opposite poles attract."},
    {"skill": "magnetism", "difficulty": "easy", "type": "free_text", "question": "What are the two poles of a magnet?", "answer": "North and South", "explanation": "Every magnet has a north pole and a south pole.", "acceptable_answers": ["North and South", "N and S", "north, south"]},
    {"skill": "magnetism", "difficulty": "medium", "type": "free_text", "question": "What is an electromagnet?", "answer": "a magnet made by running electric current through a coil", "explanation": "Electromagnets are temporary magnets created by electric current.", "acceptable_answers": ["magnet made with electricity", "coil with current", "electrical magnet"]},
    
    # THERMODYNAMICS
    {"skill": "thermodynamics", "difficulty": "easy", "type": "free_text", "question": "What is absolute zero in Celsius?", "answer": "-273", "explanation": "Absolute zero is -273.15°C, the lowest possible temperature.", "acceptable_answers": ["-273", "-273.15", "-273°C"]},
    {"skill": "thermodynamics", "difficulty": "easy", "type": "multiple_choice", "question": "Heat naturally flows from:", "options": ["Cold to hot", "Hot to cold", "Any direction", "Doesn't flow"], "answer": "B", "explanation": "Heat spontaneously flows from higher to lower temperature."},
    {"skill": "thermodynamics", "difficulty": "medium", "type": "free_text", "question": "What is the First Law of Thermodynamics about?", "answer": "conservation of energy", "explanation": "Energy cannot be created or destroyed, only transformed.", "acceptable_answers": ["conservation of energy", "energy conservation", "energy is conserved"]},
]

CHEMISTRY_QUESTIONS = [
    # ATOMIC STRUCTURE
    {"skill": "atomic_structure", "difficulty": "easy", "type": "multiple_choice", "question": "What is the charge of an electron?", "options": ["Positive", "Negative", "Neutral", "Variable"], "answer": "B", "explanation": "Electrons carry a negative charge."},
    {"skill": "atomic_structure", "difficulty": "easy", "type": "free_text", "question": "What particle is found in the nucleus and has no charge?", "answer": "neutron", "explanation": "Neutrons are neutral particles in the nucleus.", "acceptable_answers": ["neutron", "neutrons"]},
    {"skill": "atomic_structure", "difficulty": "easy", "type": "free_text", "question": "What determines the atomic number of an element?", "answer": "number of protons", "explanation": "Atomic number = number of protons in the nucleus.", "acceptable_answers": ["number of protons", "protons", "proton count"]},
    {"skill": "atomic_structure", "difficulty": "medium", "type": "numeric", "question": "Carbon has 6 protons. How many electrons does a neutral carbon atom have?", "answer": "6", "explanation": "In a neutral atom, protons = electrons."},
    {"skill": "atomic_structure", "difficulty": "medium", "type": "free_text", "question": "What are isotopes?", "answer": "atoms with the same protons but different neutrons", "explanation": "Isotopes are variants of an element with different numbers of neutrons.", "acceptable_answers": ["atoms with different neutrons", "same element different mass", "same protons different neutrons"]},
    
    # PERIODIC TABLE
    {"skill": "periodic_table", "difficulty": "easy", "type": "free_text", "question": "What is the symbol for Gold?", "answer": "Au", "explanation": "Au comes from the Latin 'aurum'.", "acceptable_answers": ["Au"]},
    {"skill": "periodic_table", "difficulty": "easy", "type": "free_text", "question": "What is the symbol for Sodium?", "answer": "Na", "explanation": "Na comes from the Latin 'natrium'.", "acceptable_answers": ["Na"]},
    {"skill": "periodic_table", "difficulty": "easy", "type": "multiple_choice", "question": "Elements in the same column of the periodic table have:", "options": ["Same mass", "Similar properties", "Same electrons", "Same protons"], "answer": "B", "explanation": "Elements in the same group have similar chemical properties."},
    {"skill": "periodic_table", "difficulty": "medium", "type": "free_text", "question": "What group are the Noble Gases in?", "answer": "Group 18", "explanation": "Noble gases (He, Ne, Ar, Kr, Xe, Rn) are in Group 18.", "acceptable_answers": ["Group 18", "18", "group 18", "8A"]},
    {"skill": "periodic_table", "difficulty": "medium", "type": "free_text", "question": "What are the alkali metals?", "answer": "Group 1 elements", "explanation": "Alkali metals are Li, Na, K, Rb, Cs, Fr - highly reactive metals.", "acceptable_answers": ["Group 1", "Group 1 elements", "lithium sodium potassium"]},
    
    # CHEMICAL BONDING
    {"skill": "chemical_bonding", "difficulty": "easy", "type": "multiple_choice", "question": "What type of bond forms between metals and non-metals?", "options": ["Covalent", "Ionic", "Metallic", "Hydrogen"], "answer": "B", "explanation": "Ionic bonds form when electrons transfer from metal to non-metal."},
    {"skill": "chemical_bonding", "difficulty": "easy", "type": "free_text", "question": "What type of bond involves sharing electrons?", "answer": "covalent bond", "explanation": "Covalent bonds form when atoms share electrons.", "acceptable_answers": ["covalent", "covalent bond"]},
    {"skill": "chemical_bonding", "difficulty": "medium", "type": "multiple_choice", "question": "How many covalent bonds does carbon typically form?", "options": ["1", "2", "3", "4"], "answer": "D", "explanation": "Carbon has 4 valence electrons and forms 4 bonds."},
    {"skill": "chemical_bonding", "difficulty": "medium", "type": "free_text", "question": "What is an ion?", "answer": "an atom that has gained or lost electrons", "explanation": "Ions are charged atoms due to electron gain or loss.", "acceptable_answers": ["charged atom", "atom with charge", "atom that gained or lost electrons"]},
    
    # CHEMICAL EQUATIONS
    {"skill": "chemical_equations", "difficulty": "easy", "type": "free_text", "question": "What does the arrow (→) mean in a chemical equation?", "answer": "yields or produces", "explanation": "The arrow shows the direction of the reaction from reactants to products.", "acceptable_answers": ["yields", "produces", "forms", "becomes"]},
    {"skill": "chemical_equations", "difficulty": "medium", "type": "free_text", "question": "Balance: H₂ + O₂ → H₂O", "answer": "2H₂ + O₂ → 2H₂O", "explanation": "You need 4 H atoms and 2 O atoms on each side.", "acceptable_answers": ["2H2 + O2 → 2H2O", "2H₂ + O₂ → 2H₂O"]},
    {"skill": "chemical_equations", "difficulty": "medium", "type": "multiple_choice", "question": "In a balanced equation, what is conserved?", "options": ["Only mass", "Only atoms", "Both mass and atoms", "Neither"], "answer": "C", "explanation": "The law of conservation of mass: atoms are neither created nor destroyed."},
    
    # STOICHIOMETRY
    {"skill": "stoichiometry", "difficulty": "medium", "type": "numeric", "question": "In 2H₂O, how many hydrogen atoms are there per molecule of water?", "answer": "2", "explanation": "The subscript 2 in H₂O means 2 hydrogen atoms per water molecule."},
    {"skill": "stoichiometry", "difficulty": "medium", "type": "numeric", "question": "What is the molar mass of H₂O? (H=1, O=16)", "answer": "18", "explanation": "H₂O = 2(1) + 16 = 18 g/mol."},
    {"skill": "stoichiometry", "difficulty": "hard", "type": "numeric", "question": "What is the molar mass of CO₂? (C=12, O=16)", "answer": "44", "explanation": "CO₂ = 12 + 2(16) = 44 g/mol."},
    
    # STATES OF MATTER
    {"skill": "states_of_matter", "difficulty": "easy", "type": "multiple_choice", "question": "In which state do particles have the most energy?", "options": ["Solid", "Liquid", "Gas", "All the same"], "answer": "C", "explanation": "Gas particles move fastest and have the most kinetic energy."},
    {"skill": "states_of_matter", "difficulty": "easy", "type": "free_text", "question": "What is it called when a solid turns directly into a gas?", "answer": "sublimation", "explanation": "Sublimation is the phase transition from solid to gas.", "acceptable_answers": ["sublimation"]},
    {"skill": "states_of_matter", "difficulty": "medium", "type": "free_text", "question": "At what temperature (°C) does water boil at sea level?", "answer": "100", "explanation": "Water's boiling point at 1 atm pressure is 100°C.", "acceptable_answers": ["100", "100°C", "100 degrees"]},
    
    # SOLUTIONS
    {"skill": "solutions", "difficulty": "easy", "type": "free_text", "question": "What is the solvent in salt water?", "answer": "water", "explanation": "The solvent is the substance that dissolves others (usually the larger amount).", "acceptable_answers": ["water", "H2O"]},
    {"skill": "solutions", "difficulty": "easy", "type": "free_text", "question": "What is the solute in salt water?", "answer": "salt", "explanation": "The solute is the substance being dissolved.", "acceptable_answers": ["salt", "NaCl", "sodium chloride"]},
    {"skill": "solutions", "difficulty": "medium", "type": "multiple_choice", "question": "What happens to solubility of a gas when temperature increases?", "options": ["Increases", "Decreases", "Stays same", "Becomes zero"], "answer": "B", "explanation": "Gases become less soluble in liquids as temperature rises."},
    
    # ACIDS & BASES
    {"skill": "acids_bases", "difficulty": "easy", "type": "numeric", "question": "What is the pH of pure water?", "answer": "7", "explanation": "Pure water has a neutral pH of 7."},
    {"skill": "acids_bases", "difficulty": "easy", "type": "multiple_choice", "question": "Acids have a pH:", "options": ["Less than 7", "Equal to 7", "Greater than 7", "Equal to 14"], "answer": "A", "explanation": "Acids have pH values less than 7."},
    {"skill": "acids_bases", "difficulty": "medium", "type": "free_text", "question": "What is produced when an acid reacts with a base?", "answer": "salt and water", "explanation": "Acid + Base → Salt + Water (neutralization reaction).", "acceptable_answers": ["salt and water", "water and salt", "a salt and water"]},
    {"skill": "acids_bases", "difficulty": "medium", "type": "free_text", "question": "What color does litmus paper turn in an acid?", "answer": "red", "explanation": "Blue litmus paper turns red in acidic solutions.", "acceptable_answers": ["red"]},
    
    # REDOX REACTIONS
    {"skill": "redox_reactions", "difficulty": "medium", "type": "free_text", "question": "What is oxidation?", "answer": "loss of electrons", "explanation": "OIL RIG: Oxidation Is Loss (of electrons).", "acceptable_answers": ["loss of electrons", "losing electrons", "electron loss"]},
    {"skill": "redox_reactions", "difficulty": "medium", "type": "free_text", "question": "What is reduction?", "answer": "gain of electrons", "explanation": "OIL RIG: Reduction Is Gain (of electrons).", "acceptable_answers": ["gain of electrons", "gaining electrons", "electron gain"]},
    {"skill": "redox_reactions", "difficulty": "hard", "type": "multiple_choice", "question": "In the reaction 2Na + Cl₂ → 2NaCl, sodium is:", "options": ["Oxidized", "Reduced", "Neither", "Both"], "answer": "A", "explanation": "Sodium loses an electron (Na → Na⁺), so it's oxidized."},
    
    # ORGANIC CHEMISTRY
    {"skill": "organic_chemistry", "difficulty": "easy", "type": "free_text", "question": "What element is the basis of organic chemistry?", "answer": "carbon", "explanation": "Organic chemistry is the study of carbon-containing compounds.", "acceptable_answers": ["carbon", "C"]},
    {"skill": "organic_chemistry", "difficulty": "medium", "type": "free_text", "question": "What is the simplest alkane?", "answer": "methane", "explanation": "Methane (CH₄) is the simplest hydrocarbon.", "acceptable_answers": ["methane", "CH4", "CH₄"]},
    {"skill": "organic_chemistry", "difficulty": "medium", "type": "multiple_choice", "question": "What functional group defines alcohols?", "options": ["-COOH", "-OH", "-NH₂", "-CHO"], "answer": "B", "explanation": "Alcohols contain the hydroxyl (-OH) functional group."},
]

BIOLOGY_QUESTIONS = [
    # CELL STRUCTURE
    {"skill": "cell_structure", "difficulty": "easy", "type": "free_text", "question": "What organelle is the 'powerhouse of the cell'?", "answer": "mitochondria", "explanation": "Mitochondria produce ATP through cellular respiration.", "acceptable_answers": ["mitochondria", "mitochondrion"]},
    {"skill": "cell_structure", "difficulty": "easy", "type": "free_text", "question": "What structure contains the cell's genetic material?", "answer": "nucleus", "explanation": "The nucleus houses DNA and controls cell activities.", "acceptable_answers": ["nucleus", "the nucleus"]},
    {"skill": "cell_structure", "difficulty": "easy", "type": "multiple_choice", "question": "Which organelle is found in plant cells but not animal cells?", "options": ["Nucleus", "Ribosome", "Chloroplast", "Mitochondria"], "answer": "C", "explanation": "Chloroplasts perform photosynthesis in plants."},
    {"skill": "cell_structure", "difficulty": "medium", "type": "free_text", "question": "What is the function of ribosomes?", "answer": "protein synthesis", "explanation": "Ribosomes translate mRNA into proteins.", "acceptable_answers": ["protein synthesis", "make proteins", "produce proteins", "synthesize proteins"]},
    {"skill": "cell_structure", "difficulty": "medium", "type": "free_text", "question": "What does the cell membrane do?", "answer": "controls what enters and leaves the cell", "explanation": "The cell membrane is selectively permeable.", "acceptable_answers": ["controls entry and exit", "regulates movement", "selectively permeable barrier"]},
    
    # CELL PROCESSES
    {"skill": "cell_processes", "difficulty": "easy", "type": "free_text", "question": "What is photosynthesis?", "answer": "process by which plants make food using sunlight", "explanation": "Plants convert CO₂ and H₂O into glucose and O₂.", "acceptable_answers": ["plants making food from sunlight", "converting light to food", "producing glucose from sunlight"]},
    {"skill": "cell_processes", "difficulty": "medium", "type": "free_text", "question": "What gas do plants release during photosynthesis?", "answer": "oxygen", "explanation": "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂", "acceptable_answers": ["oxygen", "O2", "O₂"]},
    {"skill": "cell_processes", "difficulty": "medium", "type": "free_text", "question": "What is cellular respiration?", "answer": "process of breaking down glucose to release energy", "explanation": "Cells convert glucose + oxygen into ATP + CO₂ + H₂O.", "acceptable_answers": ["breaking down glucose for energy", "producing ATP from glucose", "metabolizing food for energy"]},
    {"skill": "cell_processes", "difficulty": "medium", "type": "multiple_choice", "question": "What type of cell division produces identical cells?", "options": ["Meiosis", "Mitosis", "Binary fission", "Budding"], "answer": "B", "explanation": "Mitosis produces two genetically identical daughter cells."},
    
    # GENETICS BASICS
    {"skill": "genetics_basics", "difficulty": "easy", "type": "free_text", "question": "What does DNA stand for?", "answer": "Deoxyribonucleic acid", "explanation": "DNA is the molecule that carries genetic information.", "acceptable_answers": ["Deoxyribonucleic acid", "deoxyribonucleic acid"]},
    {"skill": "genetics_basics", "difficulty": "easy", "type": "multiple_choice", "question": "What shape is the DNA molecule?", "options": ["Single helix", "Double helix", "Triple helix", "Linear"], "answer": "B", "explanation": "DNA forms a double helix structure."},
    {"skill": "genetics_basics", "difficulty": "medium", "type": "free_text", "question": "What are the four bases in DNA?", "answer": "Adenine, Thymine, Guanine, Cytosine", "explanation": "A pairs with T, G pairs with C.", "acceptable_answers": ["ATGC", "A, T, G, C", "adenine thymine guanine cytosine"]},
    {"skill": "genetics_basics", "difficulty": "medium", "type": "free_text", "question": "If a DNA strand has the sequence ATCG, what is the complementary strand?", "answer": "TAGC", "explanation": "A pairs with T, T pairs with A, C pairs with G, G pairs with C.", "acceptable_answers": ["TAGC"]},
    
    # DNA & RNA
    {"skill": "dna_rna", "difficulty": "medium", "type": "multiple_choice", "question": "How is RNA different from DNA?", "options": ["RNA has thymine", "RNA is double-stranded", "RNA has uracil instead of thymine", "RNA is longer"], "answer": "C", "explanation": "RNA uses Uracil (U) instead of Thymine (T)."},
    {"skill": "dna_rna", "difficulty": "medium", "type": "free_text", "question": "What is transcription?", "answer": "copying DNA to make RNA", "explanation": "Transcription produces mRNA from a DNA template.", "acceptable_answers": ["DNA to RNA", "copying DNA to RNA", "making RNA from DNA"]},
    {"skill": "dna_rna", "difficulty": "medium", "type": "free_text", "question": "What is translation?", "answer": "using RNA to make proteins", "explanation": "Translation converts mRNA codons into amino acid sequences.", "acceptable_answers": ["RNA to protein", "making proteins from RNA"]},
    
    # HEREDITY
    {"skill": "heredity", "difficulty": "easy", "type": "free_text", "question": "What do we call a trait that is hidden by a dominant trait?", "answer": "recessive", "explanation": "Recessive traits only show when no dominant allele is present.", "acceptable_answers": ["recessive", "recessive trait"]},
    {"skill": "heredity", "difficulty": "medium", "type": "multiple_choice", "question": "If both parents are Aa, what percentage of offspring will be aa?", "options": ["0%", "25%", "50%", "75%"], "answer": "B", "explanation": "Punnett square: AA, Aa, Aa, aa - 25% will be aa."},
    {"skill": "heredity", "difficulty": "medium", "type": "free_text", "question": "What is a genotype?", "answer": "the genetic makeup of an organism", "explanation": "Genotype refers to the actual genes/alleles an organism has.", "acceptable_answers": ["genetic makeup", "genes of an organism", "allele combination"]},
    {"skill": "heredity", "difficulty": "medium", "type": "free_text", "question": "What is a phenotype?", "answer": "the physical expression of genes", "explanation": "Phenotype is the observable characteristics of an organism.", "acceptable_answers": ["physical traits", "observable characteristics", "physical expression"]},
    
    # EVOLUTION
    {"skill": "evolution", "difficulty": "easy", "type": "free_text", "question": "Who proposed the theory of natural selection?", "answer": "Charles Darwin", "explanation": "Darwin published 'On the Origin of Species' in 1859.", "acceptable_answers": ["Charles Darwin", "Darwin"]},
    {"skill": "evolution", "difficulty": "medium", "type": "free_text", "question": "What is natural selection?", "answer": "survival and reproduction of organisms best adapted to their environment", "explanation": "Better adapted organisms are more likely to survive and reproduce.", "acceptable_answers": ["survival of the fittest", "better adapted survive", "adaptation over generations"]},
    {"skill": "evolution", "difficulty": "medium", "type": "free_text", "question": "What is a mutation?", "answer": "a change in DNA sequence", "explanation": "Mutations are changes in the genetic code that can be inherited.", "acceptable_answers": ["change in DNA", "genetic change", "alteration in genes"]},
    
    # CLASSIFICATION
    {"skill": "classification", "difficulty": "easy", "type": "free_text", "question": "What is the scientific naming system called?", "answer": "binomial nomenclature", "explanation": "Organisms are named using genus and species (e.g., Homo sapiens).", "acceptable_answers": ["binomial nomenclature", "binomial naming"]},
    {"skill": "classification", "difficulty": "medium", "type": "free_text", "question": "Put in order (largest to smallest): Class, Kingdom, Species, Phylum", "answer": "Kingdom, Phylum, Class, Species", "explanation": "King Philip Came Over For Good Soup.", "acceptable_answers": ["Kingdom Phylum Class Species", "kingdom, phylum, class, species"]},
    {"skill": "classification", "difficulty": "medium", "type": "multiple_choice", "question": "Which kingdom includes bacteria?", "options": ["Protista", "Fungi", "Monera/Bacteria", "Plantae"], "answer": "C", "explanation": "Bacteria belong to the kingdom Monera or domain Bacteria."},
    
    # ECOSYSTEMS
    {"skill": "ecosystems", "difficulty": "easy", "type": "free_text", "question": "What is a food chain?", "answer": "a sequence showing how energy flows from one organism to another", "explanation": "Energy transfers from producers to consumers.", "acceptable_answers": ["energy flow between organisms", "who eats whom", "feeding sequence"]},
    {"skill": "ecosystems", "difficulty": "easy", "type": "multiple_choice", "question": "What are organisms that make their own food called?", "options": ["Consumers", "Producers", "Decomposers", "Predators"], "answer": "B", "explanation": "Producers (like plants) use photosynthesis to make food."},
    {"skill": "ecosystems", "difficulty": "medium", "type": "free_text", "question": "What is a food web?", "answer": "interconnected food chains in an ecosystem", "explanation": "A food web shows the complex feeding relationships in an ecosystem.", "acceptable_answers": ["multiple food chains", "connected food chains", "network of food chains"]},
    {"skill": "ecosystems", "difficulty": "medium", "type": "free_text", "question": "What do decomposers do?", "answer": "break down dead organisms and waste", "explanation": "Decomposers recycle nutrients back into the ecosystem.", "acceptable_answers": ["break down dead matter", "decompose organic material", "recycle nutrients"]},
    
    # HUMAN BODY
    {"skill": "human_body", "difficulty": "easy", "type": "numeric", "question": "How many chambers does the human heart have?", "answer": "4", "explanation": "The heart has 4 chambers: 2 atria and 2 ventricles."},
    {"skill": "human_body", "difficulty": "easy", "type": "free_text", "question": "What organ produces insulin?", "answer": "pancreas", "explanation": "The pancreas produces insulin to regulate blood sugar.", "acceptable_answers": ["pancreas", "the pancreas"]},
    {"skill": "human_body", "difficulty": "medium", "type": "free_text", "question": "What is the function of red blood cells?", "answer": "carry oxygen", "explanation": "Red blood cells contain hemoglobin which binds oxygen.", "acceptable_answers": ["carry oxygen", "transport oxygen", "deliver oxygen to cells"]},
    {"skill": "human_body", "difficulty": "medium", "type": "multiple_choice", "question": "Which system fights infections?", "options": ["Digestive", "Respiratory", "Immune", "Nervous"], "answer": "C", "explanation": "The immune system defends against pathogens."},
    
    # PLANTS
    {"skill": "plants", "difficulty": "easy", "type": "free_text", "question": "What is the green pigment in plants called?", "answer": "chlorophyll", "explanation": "Chlorophyll absorbs light for photosynthesis.", "acceptable_answers": ["chlorophyll"]},
    {"skill": "plants", "difficulty": "medium", "type": "free_text", "question": "What part of the plant absorbs water and minerals?", "answer": "roots", "explanation": "Roots anchor the plant and absorb water and nutrients.", "acceptable_answers": ["roots", "the roots", "root system"]},
    {"skill": "plants", "difficulty": "medium", "type": "free_text", "question": "What do stomata do?", "answer": "allow gas exchange in leaves", "explanation": "Stomata open and close to regulate CO₂, O₂, and water vapor exchange.", "acceptable_answers": ["gas exchange", "allow gases in and out", "regulate gas exchange"]},
]

ALL_SCIENCE_QUESTIONS = PHYSICS_QUESTIONS + CHEMISTRY_QUESTIONS + BIOLOGY_QUESTIONS
