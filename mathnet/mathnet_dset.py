"""
This file contains a series of functions for creating txt datasets of question answer pairs separated by a ;
"""

import json
import random


BASES = [
    "ones",
    "tens",
    "hundreds",
    "thousands",
    "ten thousands",
    "hundred thousands",
    "millions",
    "ten millions",
    "hundred millions",
    "billions",
    "ten billions",
    "hundred billions",
    "trillions",
    "ten trillions",
    "hundred trillions",
    "quadrillions",
    "ten quadrillions",
    "hundred quadrillions",
]


def basic_arithmetic(up_to=15):
    """
    Saves basic arithmetic operations to a JSON file
    """
    operands = ["+", "-", "*", "/"]
    examples = []
    counter = 1
    for op in operands:
        for i in range(1, up_to + 1):
            for j in range(1, up_to + 1):
                if op == "+":
                    solution = i + j
                elif op == "-":
                    solution = i - j
                elif op == "*":
                    solution = i * j
                elif op == "/":
                    if j != 0:
                        solution = i / j
                    else:
                        solution = "can not divide by 0"

                question = f"{i} {op} {j}"
                answer = str(solution) if isinstance(solution, int) else solution
                examples.append(
                    {
                        "question": question,
                        "answer": str(answer),
                        "question_id": counter,
                    }
                )
                counter += 1

    return examples


def make_number_pairs(num=100, max_digits=3):
    """
    Generates a list of tuples of integer pairs. Right number is bigger
    Returns a list of strings for easier digit wise operations
    """
    problems = []
    for _ in range(num):
        digits_top = max(2, random.randint(1, max_digits))
        digits_bottom = min(digits_top, random.randint(1, max_digits))

        top_number = random.randint(10 ** (digits_top - 1), 10**digits_top - 1)
        bottom_number = random.randint(10 ** (digits_bottom - 1), 10**digits_bottom - 1)

        if bottom_number > top_number:
            top_number, bottom_number = bottom_number, top_number

        problems.append((str(top_number), str(bottom_number)))
    return problems


def make_add_prompt(problem):
    """
    Converts a pair of strings into a parsed addition solution
    """
    top, bot = problem
    gt = int(top) + int(bot)

    prompt = f"Add {top} and {bot} step by step:\n"
    top = top[::-1]
    bot = bot[::-1]
    steps = []
    carry = 0
    new_carry = 0
    final = []
    for i in range(len(top)):
        top_digit = int(top[i])
        bot_digit = int(bot[i]) if i < len(bot) else 0

        column_sum = top_digit + bot_digit + carry
        remainder = column_sum % 10
        new_carry = column_sum // 10

        place = BASES[i]

        if i >= len(bot):
            explanation = f"Adding the {place}: {top_digit} + {bot_digit} + {carry} = {column_sum} (There are no digits in the smaller number greater greater than the {place}, so we write down the {remainder} from the {place} spot from the top number)"
        else:
            explanation = f"Adding the {place}: {top_digit} + {bot_digit} + {carry} = {column_sum} (carry {new_carry} to the next pair, and we write down {remainder} at the {place} place)"

        steps.append(explanation)
        final.insert(0, str(remainder))

        carry = new_carry

    if new_carry != 0:
        final.insert(0, str(new_carry))

    sol = "".join([e for e in final])

    if int(sol) != gt:
        return False

    prompt += "\n".join(steps) + "\nThe answer is " + "".join([e for e in final])

    return f"{top[::-1]} + {bot[::-1]}", prompt, sol
    # return {"question": f"{top[::-1]} + {bot[::-1]}", "answer": prompt}


def make_mult_prompt(problem):
    """
    Make multiplication prompt step by step
    """
    top, bot = problem
    gt = int(top) * int(bot)

    prompt = f"Multiply {top} and {bot} step by step:\n"
    top = top[::-1]
    bot = bot[::-1]
    carry = 0
    new_carry = 0
    steps = []
    final = []
    total_steps = []
    intermediates = []

    for i in range(len(bot)):
        bot_digit = int(bot[i])
        carry = 0
        step_result = []

        place = BASES[i]

        explanation = f"Multiplying {top[::-1]} by the {bot_digit} in the {place} place"
        steps.append(explanation)

        intermediate = []
        for j in range(len(top)):
            top_digit = int(top[j])
            mult = top_digit * bot_digit + carry
            remainder = mult % 10
            new_carry = mult // 10
            step_result.append(
                f"{top_digit} * {bot_digit} + {carry} = {mult} (carry {new_carry}, remainder {remainder})"
            )
            carry = new_carry
            intermediate.insert(0, str(remainder))

        if new_carry != 0:
            intermediate.insert(0, str(new_carry))

        if i > 0:
            intermediate.append("0" * i)

        intermediate = "".join([e for e in intermediate])

        intermediates.append(intermediate)

        steps.append("\n".join(step_result))
        explanation = f"Multiplying {top[::-1]} by the {bot_digit} in the {place} place yields {intermediate}\n"
        steps.append(explanation)

    # solving for the ints
    explanation = f"Adding all of our intermediate solutions together {' + '.join(intermediates)}:\n"
    steps.append(explanation)

    while len(intermediates) > 1:
        left, right = intermediates.pop(0), intermediates.pop(0)

        _, a, sol = make_add_prompt(
            (str(max(int(left), int(right))), str(min(int(left), int(right))))
        )
        steps.append(a)
        steps.append("")  # joins with newline
        intermediates.insert(0, sol)

        if len(intermediates) > 1:
            steps.append(
                f"After adding the intermediates now are {' + '.join(intermediates)}"
            )
        else:
            steps.append(
                f"Adding all of the intermediates results in the final solution of: {' + '.join(intermediates)}"
            )

    sol = "".join([e for e in intermediates[0]])
    if int(sol) != gt:
        return False

    prompt += "\n".join(steps)
    return f"{top[::-1]} * {bot[::-1]}", prompt, sol


# TODO touble shoot multiplication steps
def make_subtract_prompt(problem):
    """
    Converts a pair of strings into a parsed subtraction solution, step by step.
    """
    top, bot = problem
    gt = int(top) - int(bot)

    prompt = f"Subtract {bot} from {top} step by step:\n"
    top = top[::-1]
    bot = bot[::-1]
    steps = []
    borrow = 0
    final = []
    for i in range(len(top)):
        top_digit = int(top[i])
        bot_digit = int(bot[i]) if i < len(bot) else 0

        column_sub = top_digit - bot_digit - borrow
        if column_sub < 0:
            column_sub += 10
            borrow = 1
        else:
            borrow = 0

        place = BASES[i]

        explanation = f"Subtracting the {place}: {top_digit} - {bot_digit} - previous borrow {borrow} = {column_sub} (place the {column_sub} at the {place} place)"
        steps.append(explanation)
        final.insert(0, str(column_sub))

    sol = "".join(final)

    if int(sol) != gt:
        return False

    prompt += "\n".join(steps) + "\nThe answer is " + sol

    return f"{top[::-1]} - {bot[::-1]}", prompt, sol


def make_divide_prompt(problem):
    """
    Converts a pair of strings into a parsed division solution, explaining each step in the style of long division.
    This does with remainder, so there is only the need for one subtraction.
    long division doesn't work yet but this should be fine tbh.
    TODO implement long division
    """
    top, bot = problem
    divisor = int(bot)
    dividend = int(top)
    if divisor == 0:
        return f"{top} / {bot}", "Cannot divide by zero", "undefined"

    quotient = 0
    remainder = dividend

    prompt = f"How many times does {bot} fit into {top}. Divide {top} by {bot} step by step:\n"
    steps = []

    # Trying to find the highest multiplier
    multiplier = 0
    product = 0
    while product <= dividend:

        if product == dividend:
            steps.append(
                f"Trying {divisor} * {multiplier} = {product} (which is exactly {dividend})"
            )
            break
        else:
            steps.append(
                f"Trying {divisor} * {multiplier} = {product} (which is {'not ' if product <= dividend else ''}less than or equal to {dividend})"
            )
            multiplier += 1
        product = divisor * multiplier

    # Perform the subtraction
    if product > dividend:
        multiplier -= 1
        product = divisor * multiplier
        remainder = dividend - product

        _, a, sol = make_subtract_prompt(
            (
                str(max(int(dividend), int(product))),
                str(min(int(dividend), int(product))),
            )
        )

        steps.append(
            f"{divisor} * {multiplier} = {product} which is less than {dividend}"
        )
        steps.append(
            f"Now subtract {product} from {dividend} to get the remainder: {a}"
            # {dividend} - {product} = {remainder}
        )
    else:
        remainder = dividend - product
        steps.append(
            f"{divisor} * {multiplier} = {product} which is exactly {dividend}, hence remainder is 0"
        )

    prompt += (
        "\n".join(steps)
        + f"\nThus, the quotient is {multiplier} and the remainder is {remainder}\nThe answer is {multiplier}R{remainder}"
    )

    return f"{top} / {bot}", prompt, f"{multiplier}R{remainder}"


# Example of how to integrate these functions into your main script

if __name__ == "__main__":
    # print(make_subtract_prompt(("983", "612")))
    # print(make_divide_prompt(("983", "612")))

    examples = basic_arithmetic()
    question_count = len(
        examples
    )  # Starts counting from the number of basic arithmetic questions

    # Adding addition problems with index
    for pair in make_number_pairs(num=2000, max_digits=5):
        q, a, s = make_add_prompt(pair)
        question_count += 1
        examples.append({"question": q, "answer": a, "question_id": question_count})

    # Adding subtraction problems with indexed IDs
    for pair in make_number_pairs(num=2000, max_digits=5):
        q, a, s = make_subtract_prompt(pair)
        question_count += 1
        examples.append({"question": q, "answer": a, "question_id": question_count})

    # Adding multiplication problems with indexed IDs
    for pair in make_number_pairs(num=1000, max_digits=3):
        q, a, s = make_mult_prompt(pair)
        question_count += 1
        examples.append({"question": q, "answer": a, "question_id": question_count})

    # Adding division problems with indexed IDs
    for pair in make_number_pairs(num=1000, max_digits=3):
        q, a, s = make_divide_prompt(pair)
        question_count += 1
        examples.append({"question": q, "answer": a, "question_id": question_count})

    with open("basic_arithmetic.json", "w", encoding="utf-8") as file:
        json.dump(examples, file, indent=4)
    # problem = ("1234589", "9876541")
    # prompt = make_add_prompt(problem)
    # print(prompt["answer"])

    # problem = ("983", "612")
