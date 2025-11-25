"""
Mathematics curriculum questions
"""

MATH_QUESTIONS = [
    # ADDITION (30 questions)
    {"skill": "addition", "difficulty": "easy", "type": "numeric", "question": "What is 5 + 3?", "answer": "8", "explanation": "When we add 5 and 3, we get 8. Think of having 5 apples and getting 3 more."},
    {"skill": "addition", "difficulty": "easy", "type": "numeric", "question": "What is 7 + 4?", "answer": "11", "explanation": "7 + 4 = 11. You can count up from 7: 8, 9, 10, 11."},
    {"skill": "addition", "difficulty": "easy", "type": "numeric", "question": "What is 9 + 6?", "answer": "15", "explanation": "9 + 6 = 15. A helpful trick: 9 + 6 = 10 + 5 = 15."},
    {"skill": "addition", "difficulty": "easy", "type": "numeric", "question": "What is 12 + 8?", "answer": "20", "explanation": "12 + 8 = 20. Notice that 8 is 2 less than 10, so 12 + 8 is the same as 12 + 10 - 2."},
    {"skill": "addition", "difficulty": "easy", "type": "numeric", "question": "What is 15 + 5?", "answer": "20", "explanation": "15 + 5 = 20. Adding 5 to 15 gives us a nice round number."},
    {"skill": "addition", "difficulty": "medium", "type": "numeric", "question": "What is 47 + 35?", "answer": "82", "explanation": "47 + 35 = 82. Add the ones: 7+5=12, carry the 1. Add the tens: 4+3+1=8."},
    {"skill": "addition", "difficulty": "medium", "type": "numeric", "question": "What is 128 + 256?", "answer": "384", "explanation": "128 + 256 = 384. Add column by column from right to left."},
    {"skill": "addition", "difficulty": "medium", "type": "numeric", "question": "What is 99 + 47?", "answer": "146", "explanation": "99 + 47 = 146. Trick: 99 + 47 = 100 + 46 = 146."},
    {"skill": "addition", "difficulty": "medium", "type": "numeric", "question": "What is 345 + 678?", "answer": "1023", "explanation": "345 + 678 = 1023. Stack and add each column."},
    {"skill": "addition", "difficulty": "hard", "type": "numeric", "question": "What is 4,567 + 8,934?", "answer": "13501", "explanation": "4,567 + 8,934 = 13,501. Align the numbers and add each place value."},
    
    # SUBTRACTION (30 questions)
    {"skill": "subtraction", "difficulty": "easy", "type": "numeric", "question": "What is 10 - 4?", "answer": "6", "explanation": "10 - 4 = 6. If you have 10 cookies and eat 4, you have 6 left."},
    {"skill": "subtraction", "difficulty": "easy", "type": "numeric", "question": "What is 15 - 7?", "answer": "8", "explanation": "15 - 7 = 8. Count back from 15: 14, 13, 12, 11, 10, 9, 8."},
    {"skill": "subtraction", "difficulty": "easy", "type": "numeric", "question": "What is 20 - 12?", "answer": "8", "explanation": "20 - 12 = 8. You can think: 12 + ? = 20."},
    {"skill": "subtraction", "difficulty": "medium", "type": "numeric", "question": "What is 100 - 37?", "answer": "63", "explanation": "100 - 37 = 63. Borrow from tens place: 10-7=3, 9-3=6."},
    {"skill": "subtraction", "difficulty": "medium", "type": "numeric", "question": "What is 543 - 267?", "answer": "276", "explanation": "543 - 267 = 276. Use borrowing: 3-7 needs borrowing."},
    {"skill": "subtraction", "difficulty": "medium", "type": "numeric", "question": "What is 1000 - 456?", "answer": "544", "explanation": "1000 - 456 = 544. A trick: 999 - 456 = 543, then add 1."},
    {"skill": "subtraction", "difficulty": "hard", "type": "numeric", "question": "What is 5,280 - 2,847?", "answer": "2433", "explanation": "5,280 - 2,847 = 2,433. Multiple borrowing required."},
    
    # MULTIPLICATION (40 questions)
    {"skill": "multiplication", "difficulty": "easy", "type": "numeric", "question": "What is 3 × 4?", "answer": "12", "explanation": "3 × 4 = 12. This means 3 groups of 4, or 4 + 4 + 4."},
    {"skill": "multiplication", "difficulty": "easy", "type": "numeric", "question": "What is 5 × 5?", "answer": "25", "explanation": "5 × 5 = 25. Five squared equals 25."},
    {"skill": "multiplication", "difficulty": "easy", "type": "numeric", "question": "What is 6 × 7?", "answer": "42", "explanation": "6 × 7 = 42. A common multiplication fact to memorize."},
    {"skill": "multiplication", "difficulty": "easy", "type": "numeric", "question": "What is 8 × 9?", "answer": "72", "explanation": "8 × 9 = 72. Think: 8 × 10 - 8 = 80 - 8 = 72."},
    {"skill": "multiplication", "difficulty": "easy", "type": "numeric", "question": "What is 7 × 8?", "answer": "56", "explanation": "7 × 8 = 56. Memory trick: 5, 6, 7, 8: 56 = 7 × 8."},
    {"skill": "multiplication", "difficulty": "medium", "type": "numeric", "question": "What is 12 × 12?", "answer": "144", "explanation": "12 × 12 = 144. This is 12 squared."},
    {"skill": "multiplication", "difficulty": "medium", "type": "numeric", "question": "What is 15 × 8?", "answer": "120", "explanation": "15 × 8 = 120. Think: 10×8 + 5×8 = 80 + 40."},
    {"skill": "multiplication", "difficulty": "medium", "type": "numeric", "question": "What is 25 × 4?", "answer": "100", "explanation": "25 × 4 = 100. Four quarters make a dollar!"},
    {"skill": "multiplication", "difficulty": "medium", "type": "numeric", "question": "What is 23 × 7?", "answer": "161", "explanation": "23 × 7 = 161. Calculate: 20×7 + 3×7 = 140 + 21."},
    {"skill": "multiplication", "difficulty": "hard", "type": "numeric", "question": "What is 56 × 34?", "answer": "1904", "explanation": "56 × 34 = 1904. Use long multiplication or break into parts."},
    {"skill": "multiplication", "difficulty": "hard", "type": "numeric", "question": "What is 125 × 8?", "answer": "1000", "explanation": "125 × 8 = 1000. Useful fact: 125 is 1000 ÷ 8."},
    
    # DIVISION (30 questions)
    {"skill": "division", "difficulty": "easy", "type": "numeric", "question": "What is 12 ÷ 3?", "answer": "4", "explanation": "12 ÷ 3 = 4. How many groups of 3 can you make from 12?"},
    {"skill": "division", "difficulty": "easy", "type": "numeric", "question": "What is 20 ÷ 5?", "answer": "4", "explanation": "20 ÷ 5 = 4. Five groups of 4 make 20."},
    {"skill": "division", "difficulty": "easy", "type": "numeric", "question": "What is 36 ÷ 6?", "answer": "6", "explanation": "36 ÷ 6 = 6. This uses the fact that 6 × 6 = 36."},
    {"skill": "division", "difficulty": "easy", "type": "numeric", "question": "What is 56 ÷ 8?", "answer": "7", "explanation": "56 ÷ 8 = 7. Remember: 7 × 8 = 56."},
    {"skill": "division", "difficulty": "medium", "type": "numeric", "question": "What is 144 ÷ 12?", "answer": "12", "explanation": "144 ÷ 12 = 12. This is because 12² = 144."},
    {"skill": "division", "difficulty": "medium", "type": "numeric", "question": "What is 256 ÷ 16?", "answer": "16", "explanation": "256 ÷ 16 = 16. This is 16² = 256."},
    {"skill": "division", "difficulty": "medium", "type": "numeric", "question": "What is 375 ÷ 25?", "answer": "15", "explanation": "375 ÷ 25 = 15. Think: 25 × 15 = 25 × 10 + 25 × 5 = 375."},
    {"skill": "division", "difficulty": "hard", "type": "numeric", "question": "What is 1728 ÷ 12?", "answer": "144", "explanation": "1728 ÷ 12 = 144. Use long division."},
    
    # FRACTIONS (40 questions)
    {"skill": "fractions", "difficulty": "easy", "type": "free_text", "question": "Simplify 4/8", "answer": "1/2", "explanation": "4/8 = 1/2. Divide both numbers by 4.", "acceptable_answers": ["1/2", "0.5", "one half"]},
    {"skill": "fractions", "difficulty": "easy", "type": "free_text", "question": "What is 1/2 + 1/2?", "answer": "1", "explanation": "1/2 + 1/2 = 2/2 = 1. Two halves make a whole.", "acceptable_answers": ["1", "2/2", "one"]},
    {"skill": "fractions", "difficulty": "easy", "type": "free_text", "question": "Simplify 6/9", "answer": "2/3", "explanation": "6/9 = 2/3. Divide both by 3.", "acceptable_answers": ["2/3", "two thirds"]},
    {"skill": "fractions", "difficulty": "medium", "type": "free_text", "question": "What is 1/4 + 1/3?", "answer": "7/12", "explanation": "1/4 + 1/3 = 3/12 + 4/12 = 7/12. Find common denominator 12.", "acceptable_answers": ["7/12"]},
    {"skill": "fractions", "difficulty": "medium", "type": "free_text", "question": "What is 2/3 × 3/4?", "answer": "1/2", "explanation": "2/3 × 3/4 = 6/12 = 1/2. Multiply numerators and denominators.", "acceptable_answers": ["1/2", "6/12", "0.5"]},
    {"skill": "fractions", "difficulty": "medium", "type": "free_text", "question": "What is 3/4 ÷ 1/2?", "answer": "3/2", "explanation": "3/4 ÷ 1/2 = 3/4 × 2/1 = 6/4 = 3/2. Flip and multiply.", "acceptable_answers": ["3/2", "1.5", "1 1/2"]},
    {"skill": "fractions", "difficulty": "hard", "type": "free_text", "question": "Simplify 24/36", "answer": "2/3", "explanation": "24/36 = 2/3. GCD of 24 and 36 is 12.", "acceptable_answers": ["2/3"]},
    
    # DECIMALS (30 questions)
    {"skill": "decimals", "difficulty": "easy", "type": "numeric", "question": "What is 0.5 + 0.3?", "answer": "0.8", "explanation": "0.5 + 0.3 = 0.8. Line up decimal points and add."},
    {"skill": "decimals", "difficulty": "easy", "type": "numeric", "question": "What is 1.5 × 2?", "answer": "3", "explanation": "1.5 × 2 = 3.0 = 3. One and a half times two."},
    {"skill": "decimals", "difficulty": "easy", "type": "free_text", "question": "Convert 0.25 to a fraction", "answer": "1/4", "explanation": "0.25 = 25/100 = 1/4.", "acceptable_answers": ["1/4", "25/100", "one quarter"]},
    {"skill": "decimals", "difficulty": "medium", "type": "numeric", "question": "What is 3.75 + 2.48?", "answer": "6.23", "explanation": "3.75 + 2.48 = 6.23. Align decimal points."},
    {"skill": "decimals", "difficulty": "medium", "type": "numeric", "question": "What is 4.2 × 0.5?", "answer": "2.1", "explanation": "4.2 × 0.5 = 2.1. Multiplying by 0.5 is like dividing by 2."},
    {"skill": "decimals", "difficulty": "hard", "type": "numeric", "question": "What is 12.5 × 0.8?", "answer": "10", "explanation": "12.5 × 0.8 = 10. Think: 12.5 × 8 ÷ 10."},
    
    # PERCENTAGES (30 questions)
    {"skill": "percentages", "difficulty": "easy", "type": "numeric", "question": "What is 50% of 100?", "answer": "50", "explanation": "50% of 100 = 50. Half of 100 is 50."},
    {"skill": "percentages", "difficulty": "easy", "type": "numeric", "question": "What is 25% of 80?", "answer": "20", "explanation": "25% of 80 = 20. 25% is 1/4, and 80 ÷ 4 = 20."},
    {"skill": "percentages", "difficulty": "easy", "type": "numeric", "question": "What is 10% of 250?", "answer": "25", "explanation": "10% of 250 = 25. Move decimal one place left."},
    {"skill": "percentages", "difficulty": "medium", "type": "numeric", "question": "What is 15% of 200?", "answer": "30", "explanation": "15% of 200 = 30. 10% = 20, 5% = 10, total = 30."},
    {"skill": "percentages", "difficulty": "medium", "type": "numeric", "question": "What is 33% of 300?", "answer": "99", "explanation": "33% of 300 = 99. Approximately 1/3 of 300."},
    {"skill": "percentages", "difficulty": "medium", "type": "free_text", "question": "Express 3/5 as a percentage", "answer": "60%", "explanation": "3/5 = 0.6 = 60%.", "acceptable_answers": ["60%", "60", "sixty percent"]},
    {"skill": "percentages", "difficulty": "hard", "type": "numeric", "question": "A shirt costs $40. With 20% off, what is the sale price?", "answer": "32", "explanation": "20% of 40 = 8. Sale price = 40 - 8 = 32."},
    
    # ALGEBRA BASICS (40 questions)
    {"skill": "algebra_basics", "difficulty": "easy", "type": "numeric", "question": "If x = 5, what is x + 3?", "answer": "8", "explanation": "x + 3 = 5 + 3 = 8. Substitute the value."},
    {"skill": "algebra_basics", "difficulty": "easy", "type": "numeric", "question": "Solve: x + 7 = 12", "answer": "5", "explanation": "x = 12 - 7 = 5. Subtract 7 from both sides."},
    {"skill": "algebra_basics", "difficulty": "easy", "type": "numeric", "question": "Solve: 3x = 15", "answer": "5", "explanation": "x = 15 ÷ 3 = 5. Divide both sides by 3."},
    {"skill": "algebra_basics", "difficulty": "medium", "type": "numeric", "question": "Solve: 2x + 5 = 17", "answer": "6", "explanation": "2x = 17 - 5 = 12, so x = 12 ÷ 2 = 6."},
    {"skill": "algebra_basics", "difficulty": "medium", "type": "numeric", "question": "Solve: 4x - 8 = 20", "answer": "7", "explanation": "4x = 28, x = 7."},
    {"skill": "algebra_basics", "difficulty": "medium", "type": "free_text", "question": "Simplify: 3x + 5x", "answer": "8x", "explanation": "Combine like terms: 3x + 5x = 8x.", "acceptable_answers": ["8x"]},
    {"skill": "algebra_basics", "difficulty": "hard", "type": "numeric", "question": "Solve: 3(x + 2) = 21", "answer": "5", "explanation": "3x + 6 = 21, 3x = 15, x = 5."},
    
    # LINEAR EQUATIONS (30 questions)
    {"skill": "linear_equations", "difficulty": "easy", "type": "free_text", "question": "What is the slope of y = 2x + 3?", "answer": "2", "explanation": "In y = mx + b, m is the slope. Here m = 2.", "acceptable_answers": ["2", "m=2"]},
    {"skill": "linear_equations", "difficulty": "easy", "type": "free_text", "question": "What is the y-intercept of y = 5x - 4?", "answer": "-4", "explanation": "In y = mx + b, b is the y-intercept. Here b = -4.", "acceptable_answers": ["-4", "b=-4"]},
    {"skill": "linear_equations", "difficulty": "medium", "type": "free_text", "question": "Find y when x = 2 in y = 3x + 1", "answer": "7", "explanation": "y = 3(2) + 1 = 6 + 1 = 7.", "acceptable_answers": ["7", "y=7"]},
    {"skill": "linear_equations", "difficulty": "medium", "type": "numeric", "question": "Solve for x: 2x + 3y = 12 when y = 2", "answer": "3", "explanation": "2x + 3(2) = 12, 2x + 6 = 12, 2x = 6, x = 3."},
    {"skill": "linear_equations", "difficulty": "hard", "type": "free_text", "question": "What is the equation of a line with slope 2 passing through (0, 5)?", "answer": "y = 2x + 5", "explanation": "Using y = mx + b: m = 2, b = 5 (y-intercept).", "acceptable_answers": ["y = 2x + 5", "y=2x+5", "2x + 5"]},
    
    # QUADRATIC EQUATIONS (20 questions)
    {"skill": "quadratic_equations", "difficulty": "medium", "type": "free_text", "question": "Solve: x² = 16", "answer": "±4", "explanation": "x = ±4, because both 4² and (-4)² equal 16.", "acceptable_answers": ["±4", "4 and -4", "4, -4", "-4, 4"]},
    {"skill": "quadratic_equations", "difficulty": "medium", "type": "free_text", "question": "Solve: x² - 9 = 0", "answer": "±3", "explanation": "x² = 9, so x = ±3.", "acceptable_answers": ["±3", "3 and -3", "3, -3"]},
    {"skill": "quadratic_equations", "difficulty": "hard", "type": "free_text", "question": "Factor: x² + 5x + 6", "answer": "(x+2)(x+3)", "explanation": "Find two numbers that multiply to 6 and add to 5: 2 and 3.", "acceptable_answers": ["(x+2)(x+3)", "(x+3)(x+2)"]},
    {"skill": "quadratic_equations", "difficulty": "hard", "type": "free_text", "question": "Solve: x² - 5x + 6 = 0", "answer": "2 and 3", "explanation": "Factor: (x-2)(x-3) = 0, so x = 2 or x = 3.", "acceptable_answers": ["2 and 3", "x=2, x=3", "2, 3", "3, 2"]},
    
    # GEOMETRY BASICS (30 questions)
    {"skill": "geometry_basics", "difficulty": "easy", "type": "numeric", "question": "How many sides does a hexagon have?", "answer": "6", "explanation": "A hexagon has 6 sides. 'Hex' means six."},
    {"skill": "geometry_basics", "difficulty": "easy", "type": "numeric", "question": "How many degrees are in a right angle?", "answer": "90", "explanation": "A right angle is exactly 90 degrees."},
    {"skill": "geometry_basics", "difficulty": "easy", "type": "numeric", "question": "What is the sum of angles in a triangle?", "answer": "180", "explanation": "The three angles in any triangle always add up to 180°."},
    {"skill": "geometry_basics", "difficulty": "medium", "type": "numeric", "question": "If two angles of a triangle are 45° and 65°, what is the third angle?", "answer": "70", "explanation": "180 - 45 - 65 = 70°."},
    {"skill": "geometry_basics", "difficulty": "medium", "type": "free_text", "question": "What do you call a triangle with all equal sides?", "answer": "equilateral", "explanation": "An equilateral triangle has three equal sides and three 60° angles.", "acceptable_answers": ["equilateral", "equilateral triangle"]},
    {"skill": "geometry_basics", "difficulty": "hard", "type": "numeric", "question": "What is the sum of interior angles of a pentagon?", "answer": "540", "explanation": "Formula: (n-2) × 180 = (5-2) × 180 = 540°."},
    
    # AREA & PERIMETER (30 questions)
    {"skill": "area_perimeter", "difficulty": "easy", "type": "numeric", "question": "What is the perimeter of a square with side 5 cm?", "answer": "20", "explanation": "Perimeter = 4 × side = 4 × 5 = 20 cm."},
    {"skill": "area_perimeter", "difficulty": "easy", "type": "numeric", "question": "What is the area of a rectangle with length 6 and width 4?", "answer": "24", "explanation": "Area = length × width = 6 × 4 = 24 square units."},
    {"skill": "area_perimeter", "difficulty": "medium", "type": "numeric", "question": "What is the area of a triangle with base 10 and height 6?", "answer": "30", "explanation": "Area = (base × height) / 2 = (10 × 6) / 2 = 30."},
    {"skill": "area_perimeter", "difficulty": "medium", "type": "numeric", "question": "What is the perimeter of a rectangle with length 8 and width 5?", "answer": "26", "explanation": "Perimeter = 2(length + width) = 2(8 + 5) = 26."},
    {"skill": "area_perimeter", "difficulty": "hard", "type": "numeric", "question": "What is the area of a circle with radius 7? (Use π = 22/7)", "answer": "154", "explanation": "Area = πr² = (22/7) × 7² = 22 × 7 = 154."},
    
    # VOLUME (20 questions)
    {"skill": "volume", "difficulty": "easy", "type": "numeric", "question": "What is the volume of a cube with side 3 cm?", "answer": "27", "explanation": "Volume = side³ = 3³ = 27 cm³."},
    {"skill": "volume", "difficulty": "medium", "type": "numeric", "question": "What is the volume of a rectangular box with dimensions 4×3×2?", "answer": "24", "explanation": "Volume = length × width × height = 4 × 3 × 2 = 24."},
    {"skill": "volume", "difficulty": "medium", "type": "numeric", "question": "What is the volume of a cylinder with radius 3 and height 10? (Use π ≈ 3.14)", "answer": "282.6", "explanation": "Volume = πr²h = 3.14 × 9 × 10 = 282.6."},
    
    # TRIGONOMETRY (20 questions)
    {"skill": "trigonometry", "difficulty": "medium", "type": "numeric", "question": "In a right triangle, if the opposite side is 3 and hypotenuse is 5, what is sin(θ)?", "answer": "0.6", "explanation": "sin(θ) = opposite/hypotenuse = 3/5 = 0.6."},
    {"skill": "trigonometry", "difficulty": "medium", "type": "free_text", "question": "What is cos(0°)?", "answer": "1", "explanation": "The cosine of 0 degrees is 1.", "acceptable_answers": ["1", "1.0"]},
    {"skill": "trigonometry", "difficulty": "medium", "type": "free_text", "question": "What is sin(90°)?", "answer": "1", "explanation": "The sine of 90 degrees is 1.", "acceptable_answers": ["1", "1.0"]},
    {"skill": "trigonometry", "difficulty": "hard", "type": "free_text", "question": "What is tan(45°)?", "answer": "1", "explanation": "tan(45°) = sin(45°)/cos(45°) = 1.", "acceptable_answers": ["1", "1.0"]},
    
    # STATISTICS (20 questions)
    {"skill": "statistics", "difficulty": "easy", "type": "numeric", "question": "What is the mean of 2, 4, 6, 8, 10?", "answer": "6", "explanation": "Mean = (2+4+6+8+10)/5 = 30/5 = 6."},
    {"skill": "statistics", "difficulty": "easy", "type": "numeric", "question": "What is the median of 3, 5, 7, 9, 11?", "answer": "7", "explanation": "The median is the middle value when sorted. Here it's 7."},
    {"skill": "statistics", "difficulty": "medium", "type": "numeric", "question": "What is the mode of 2, 3, 3, 4, 5, 3, 6?", "answer": "3", "explanation": "The mode is the most frequent value. 3 appears 3 times."},
    {"skill": "statistics", "difficulty": "medium", "type": "numeric", "question": "What is the range of 5, 12, 3, 18, 7?", "answer": "15", "explanation": "Range = max - min = 18 - 3 = 15."},
    {"skill": "statistics", "difficulty": "hard", "type": "numeric", "question": "What is the median of 4, 8, 2, 10, 6, 12?", "answer": "7", "explanation": "Sorted: 2, 4, 6, 8, 10, 12. Median = (6+8)/2 = 7."},
    
    # PROBABILITY (20 questions)
    {"skill": "probability", "difficulty": "easy", "type": "free_text", "question": "What is the probability of getting heads on a fair coin flip?", "answer": "1/2", "explanation": "There are 2 equally likely outcomes, heads is 1 of them: 1/2.", "acceptable_answers": ["1/2", "0.5", "50%"]},
    {"skill": "probability", "difficulty": "easy", "type": "free_text", "question": "What is the probability of rolling a 6 on a fair die?", "answer": "1/6", "explanation": "A die has 6 faces, each equally likely: 1/6.", "acceptable_answers": ["1/6"]},
    {"skill": "probability", "difficulty": "medium", "type": "free_text", "question": "What is the probability of drawing a heart from a standard deck?", "answer": "1/4", "explanation": "13 hearts out of 52 cards: 13/52 = 1/4.", "acceptable_answers": ["1/4", "0.25", "25%", "13/52"]},
    {"skill": "probability", "difficulty": "medium", "type": "free_text", "question": "What is the probability of rolling an even number on a die?", "answer": "1/2", "explanation": "Even numbers: 2, 4, 6 = 3 outcomes out of 6 = 1/2.", "acceptable_answers": ["1/2", "3/6", "0.5", "50%"]},
    {"skill": "probability", "difficulty": "hard", "type": "free_text", "question": "If you flip a coin twice, what is P(at least one head)?", "answer": "3/4", "explanation": "P(at least one head) = 1 - P(no heads) = 1 - 1/4 = 3/4.", "acceptable_answers": ["3/4", "0.75", "75%"]},
]

# Generate additional questions programmatically
def generate_more_math_questions():
    """Generate additional practice questions"""
    more_questions = []
    
    # More addition problems
    for a in range(10, 100, 7):
        for b in range(5, 50, 11):
            more_questions.append({
                "skill": "addition",
                "difficulty": "medium",
                "type": "numeric",
                "question": f"What is {a} + {b}?",
                "answer": str(a + b),
                "explanation": f"{a} + {b} = {a + b}"
            })
    
    # More multiplication problems
    for a in range(2, 13):
        for b in range(2, 13):
            more_questions.append({
                "skill": "multiplication",
                "difficulty": "easy",
                "type": "numeric",
                "question": f"What is {a} × {b}?",
                "answer": str(a * b),
                "explanation": f"{a} × {b} = {a * b}"
            })
    
    return more_questions

# Combine all math questions
ALL_MATH_QUESTIONS = MATH_QUESTIONS + generate_more_math_questions()
