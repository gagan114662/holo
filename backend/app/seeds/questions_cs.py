"""
Computer Science curriculum questions
"""

CS_QUESTIONS = [
    # COMPUTATIONAL THINKING
    {"skill": "computational_thinking", "difficulty": "easy", "type": "free_text", "question": "What is an algorithm?", "answer": "a step-by-step procedure to solve a problem", "explanation": "Algorithms are like recipes - clear instructions to complete a task.", "acceptable_answers": ["step-by-step instructions", "set of steps", "procedure for solving problems"]},
    {"skill": "computational_thinking", "difficulty": "easy", "type": "free_text", "question": "What is decomposition in problem-solving?", "answer": "breaking a problem into smaller parts", "explanation": "Large problems become manageable when broken down.", "acceptable_answers": ["breaking down problems", "dividing into smaller parts"]},
    {"skill": "computational_thinking", "difficulty": "medium", "type": "free_text", "question": "What is abstraction?", "answer": "focusing on essential details while ignoring irrelevant ones", "explanation": "Abstraction helps manage complexity.", "acceptable_answers": ["hiding complexity", "simplifying", "focusing on important details"]},
    {"skill": "computational_thinking", "difficulty": "medium", "type": "free_text", "question": "What is pattern recognition?", "answer": "finding similarities or trends in data", "explanation": "Patterns help us make predictions and generalizations.", "acceptable_answers": ["finding patterns", "identifying similarities", "recognizing trends"]},
    
    # VARIABLES & DATA TYPES
    {"skill": "variables_data", "difficulty": "easy", "type": "free_text", "question": "What is a variable in programming?", "answer": "a named container that stores data", "explanation": "Variables hold values that can change during program execution.", "acceptable_answers": ["storage for data", "named storage", "container for values"]},
    {"skill": "variables_data", "difficulty": "easy", "type": "multiple_choice", "question": "Which is an integer?", "options": ["3.14", "42", "'hello'", "True"], "answer": "B", "explanation": "42 is a whole number (integer). 3.14 is a float, 'hello' is a string."},
    {"skill": "variables_data", "difficulty": "medium", "type": "free_text", "question": "What is a string?", "answer": "a sequence of characters", "explanation": "Strings represent text and are usually in quotes.", "acceptable_answers": ["text data", "sequence of characters", "text"]},
    {"skill": "variables_data", "difficulty": "medium", "type": "multiple_choice", "question": "What data type is True or False?", "options": ["Integer", "String", "Boolean", "Float"], "answer": "C", "explanation": "Booleans represent true/false values."},
    {"skill": "variables_data", "difficulty": "hard", "type": "free_text", "question": "What is the difference between an integer and a float?", "answer": "integers are whole numbers, floats have decimal points", "explanation": "5 is an integer; 5.0 is a float.", "acceptable_answers": ["integers are whole, floats have decimals", "floats have decimal points"]},
    
    # CONDITIONALS
    {"skill": "conditionals", "difficulty": "easy", "type": "free_text", "question": "What does an if statement do?", "answer": "executes code only if a condition is true", "explanation": "If statements allow programs to make decisions.", "acceptable_answers": ["runs code if condition is true", "checks condition then runs code"]},
    {"skill": "conditionals", "difficulty": "easy", "type": "multiple_choice", "question": "What does 'else' do in programming?", "options": ["Starts a loop", "Ends the program", "Runs if the 'if' condition is false", "Declares a variable"], "answer": "C", "explanation": "Else provides an alternative when if is false."},
    {"skill": "conditionals", "difficulty": "medium", "type": "free_text", "question": "What does 'elif' or 'else if' do?", "answer": "checks another condition if the previous ones were false", "explanation": "elif allows multiple conditions to be checked.", "acceptable_answers": ["checks another condition", "alternative condition check"]},
    {"skill": "conditionals", "difficulty": "medium", "type": "free_text", "question": "What is a comparison operator?", "answer": "symbols used to compare values", "explanation": "Examples: ==, !=, <, >, <=, >=", "acceptable_answers": ["compares values", "operators for comparison", "symbols like < > =="]},
    
    # LOOPS
    {"skill": "loops", "difficulty": "easy", "type": "free_text", "question": "What is a loop?", "answer": "code that repeats until a condition is met", "explanation": "Loops let you run the same code multiple times.", "acceptable_answers": ["repeating code", "code that runs multiple times", "iteration"]},
    {"skill": "loops", "difficulty": "easy", "type": "multiple_choice", "question": "Which loop runs a known number of times?", "options": ["while loop", "for loop", "do-while loop", "infinite loop"], "answer": "B", "explanation": "For loops typically iterate a specific number of times."},
    {"skill": "loops", "difficulty": "medium", "type": "free_text", "question": "What is an infinite loop?", "answer": "a loop that never stops running", "explanation": "This usually indicates a bug - the exit condition is never met.", "acceptable_answers": ["loop that never ends", "endless loop", "loop without exit condition"]},
    {"skill": "loops", "difficulty": "medium", "type": "numeric", "question": "How many times does this loop run: for i in range(5)?", "answer": "5", "explanation": "range(5) generates 0, 1, 2, 3, 4 - five iterations."},
    
    # FUNCTIONS
    {"skill": "functions", "difficulty": "easy", "type": "free_text", "question": "What is a function?", "answer": "a reusable block of code that performs a specific task", "explanation": "Functions help organize and reuse code.", "acceptable_answers": ["reusable code block", "code that can be called", "named code block"]},
    {"skill": "functions", "difficulty": "easy", "type": "free_text", "question": "What is a parameter?", "answer": "input value passed to a function", "explanation": "Parameters customize what a function does each time it's called.", "acceptable_answers": ["input to function", "value passed in", "function input"]},
    {"skill": "functions", "difficulty": "medium", "type": "free_text", "question": "What does 'return' do in a function?", "answer": "sends a value back from the function", "explanation": "Return provides the function's output to the caller.", "acceptable_answers": ["gives back a value", "outputs from function", "sends result back"]},
    {"skill": "functions", "difficulty": "medium", "type": "multiple_choice", "question": "Why do we use functions?", "options": ["To slow down code", "To avoid repeating code", "To make code harder to read", "To use more memory"], "answer": "B", "explanation": "Functions promote code reuse and organization."},
    
    # ARRAYS & LISTS
    {"skill": "arrays_lists", "difficulty": "easy", "type": "free_text", "question": "What is an array or list?", "answer": "a collection of items stored in order", "explanation": "Arrays/lists hold multiple values in a single variable.", "acceptable_answers": ["ordered collection", "collection of items", "multiple values together"]},
    {"skill": "arrays_lists", "difficulty": "easy", "type": "numeric", "question": "In most programming languages, what is the index of the first element?", "answer": "0", "explanation": "Most languages use zero-based indexing."},
    {"skill": "arrays_lists", "difficulty": "medium", "type": "free_text", "question": "What does it mean to iterate through an array?", "answer": "visiting each element one by one", "explanation": "Iteration processes each item in sequence.", "acceptable_answers": ["go through each element", "process each item", "loop through array"]},
    {"skill": "arrays_lists", "difficulty": "medium", "type": "free_text", "question": "What is array.length or len(array)?", "answer": "the number of elements in the array", "explanation": "Length tells you how many items are stored.", "acceptable_answers": ["number of elements", "size of array", "count of items"]},
    
    # ALGORITHMS
    {"skill": "algorithms", "difficulty": "easy", "type": "free_text", "question": "What is a search algorithm?", "answer": "a method to find a specific item in data", "explanation": "Search algorithms locate target values efficiently.", "acceptable_answers": ["finding items in data", "method to locate data"]},
    {"skill": "algorithms", "difficulty": "medium", "type": "free_text", "question": "What is a sorting algorithm?", "answer": "a method to arrange items in order", "explanation": "Sorting puts data in ascending or descending order.", "acceptable_answers": ["arranging in order", "ordering data", "putting items in sequence"]},
    {"skill": "algorithms", "difficulty": "medium", "type": "multiple_choice", "question": "Which is faster for searching a sorted list?", "options": ["Linear search", "Binary search", "Random search", "They're equal"], "answer": "B", "explanation": "Binary search divides the search space in half each time."},
    {"skill": "algorithms", "difficulty": "hard", "type": "free_text", "question": "What is Big O notation used for?", "answer": "describing algorithm efficiency or complexity", "explanation": "Big O shows how runtime grows with input size.", "acceptable_answers": ["measuring efficiency", "algorithm complexity", "performance measurement"]},
    
    # DEBUGGING
    {"skill": "debugging", "difficulty": "easy", "type": "free_text", "question": "What is a bug in programming?", "answer": "an error or mistake in code", "explanation": "Bugs cause programs to behave incorrectly.", "acceptable_answers": ["code error", "mistake in program", "programming error"]},
    {"skill": "debugging", "difficulty": "easy", "type": "free_text", "question": "What is debugging?", "answer": "finding and fixing errors in code", "explanation": "Debugging is the process of removing bugs.", "acceptable_answers": ["fixing errors", "finding and fixing bugs", "removing errors"]},
    {"skill": "debugging", "difficulty": "medium", "type": "multiple_choice", "question": "What is a syntax error?", "options": ["Logic mistake", "Grammar mistake in code", "Missing file", "Slow performance"], "answer": "B", "explanation": "Syntax errors violate the language's grammar rules."},
    {"skill": "debugging", "difficulty": "medium", "type": "free_text", "question": "What is a logic error?", "answer": "code that runs but produces wrong results", "explanation": "Logic errors are mistakes in the algorithm or reasoning.", "acceptable_answers": ["wrong output", "incorrect results", "code that works wrong"]},
]

ALL_CS_QUESTIONS = CS_QUESTIONS
