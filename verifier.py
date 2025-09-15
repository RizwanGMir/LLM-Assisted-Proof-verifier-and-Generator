# verifier.py

import re
import os

# part 1: Formula Helpers

def is_variable(formula):
    return isinstance(formula, str) and re.match(r"^[A-Z]$", formula)

def is_negation(formula):
    return isinstance(formula, tuple) and len(formula) == 2 and formula[0] == '~'

def is_implication(formula):
    return isinstance(formula, tuple) and len(formula) == 3 and formula[0] == '->'

# part 2: Parser

class ParserError(Exception):
    pass

def parse(formula_string: str):
    formula_string = formula_string.strip()
    if is_variable(formula_string):
        return formula_string
    if formula_string.startswith('~'):
        return ('~', parse(formula_string[1:]))
    if formula_string.startswith('(') and formula_string.endswith(')'):
        balance = 0
        split_index = -1
        for i, char in enumerate(formula_string[1:-1]):
            if char == '(': balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0: raise ParserError(f"Mismatched closing parenthesis in '{formula_string}'")
            elif char == '-' and i + 2 < len(formula_string) and formula_string[i+2] == '>' and balance == 0:
                split_index = i + 1
                break
        if split_index != -1:
            left_str = formula_string[1:split_index]
            right_str = formula_string[split_index + 3:-1]
            if left_str and right_str:
                return ('->', parse(left_str), parse(right_str))
        raise ParserError(f"Malformed implication or unbalanced parentheses in '{formula_string}'")
    raise ParserError(f"Invalid formula syntax for '{formula_string}'")

# part 3: Axiom Checkers

def is_axiom1(formula) -> bool:
    if not (is_implication(formula) and is_implication(formula[2])): return False
    A, A_prime = formula[1], formula[2][2]
    return A == A_prime

def is_axiom2(formula) -> bool:
    if not (is_implication(formula) and is_implication(formula[1]) and is_implication(formula[1][2]) and \
            is_implication(formula[2]) and is_implication(formula[2][1]) and is_implication(formula[2][2])): return False
    A, B, C = formula[1][1], formula[1][2][1], formula[1][2][2]
    return formula[2][1] == ('->', A, B) and formula[2][2] == ('->', A, C)

def is_axiom3(formula) -> bool:
    if not (is_implication(formula) and is_implication(formula[1]) and is_negation(formula[1][1]) and \
            is_negation(formula[1][2]) and is_implication(formula[2])): return False
    A, B = formula[2][1], formula[2][2]
    return formula[1] == ('->', ('~', B), ('~', A))

# part 4: Modified Verifier Logic

def verify_proof(proof_content: list, proof_name: str):
    """Verifies a single proof passed as a list of strings."""
    print(f"--- Verifying Proof: {proof_name} ---")
    proven_formulas = {}

    for line_text in proof_content:
        line_text = line_text.strip()
        if not line_text or line_text.startswith('#'): continue

        line_num_match = re.match(r"^\s*(\d+)\.\s*(.+)", line_text)
        if not line_num_match:
            print(f"FAILED: Invalid line format: '{line_text}'"); return
        
        line_num_str, rest_of_line = line_num_match.groups()
        line_num = int(line_num_str)

        justification_pattern = r"\s+(Premise|AX[123]|MP\s*\d+,\d+)$"
        justification_match = re.search(justification_pattern, rest_of_line)
        if not justification_match:
            print(f"FAILED: Malformed justification on line {line_num}: '{line_text}'"); return
            
        formula_str = rest_of_line[:justification_match.start()].strip()
        justification = justification_match.group(0).strip()

        try:
            current_formula = parse(formula_str)
        except ParserError as e:
            print(f"FAILED: Syntax Error on line {line_num}.\n  Details: {e}"); return
        
        is_valid, error_detail = False, ""
        if justification == "Premise": is_valid = True
        elif justification == "AX1":
            is_valid = is_axiom1(current_formula)
            if not is_valid: error_detail = "Formula does not match AX1 schema."
        elif justification == "AX2":
            is_valid = is_axiom2(current_formula)
            if not is_valid: error_detail = "Formula does not match AX2 schema."
        elif justification == "AX3":
            is_valid = is_axiom3(current_formula)
            if not is_valid: error_detail = "Formula does not match AX3 schema."
        elif justification.startswith("MP"):
            mp_match = re.match(r"MP\s*(\d+),(\d+)", justification)
            i, j = map(int, mp_match.groups())
            if i >= line_num or j >= line_num: error_detail = f"MP refers to future lines {i},{j}."
            elif i not in proven_formulas or j not in proven_formulas: error_detail = f"MP refers to non-existent lines {i},{j}."
            else:
                f_i, f_j = proven_formulas[i], proven_formulas[j]
                if (is_implication(f_j) and f_j[1] == f_i and f_j[2] == current_formula) or \
                   (is_implication(f_i) and f_i[1] == f_j and f_i[2] == current_formula):
                    is_valid = True
                else: error_detail = f"Conclusion does not follow from lines {i} and {j} by Modus Ponens."
        
        if is_valid:
            proven_formulas[line_num] = current_formula
        else:
            print(f"FAILED: Invalid Justification on line {line_num}.\n  Formula: {formula_str}\n  Reason: {error_detail}"); return
    
    print("VALID: The proof is correct.")
    print("-" * 40)

def load_and_run_tests_from_file(filepath: str):
    """Loads a file containing multiple proofs and verifies each one."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Test file not found at '{filepath}'")
        return

    current_proof_content = []
    current_proof_name = "Unnamed Proof"
    
    # Define a delimiter that separates tests
    DELIMITER = "--- TEST:"

    for line in lines:
        if line.startswith(DELIMITER):
            # If we have content from a previous test, run it first
            if current_proof_content:
                verify_proof(current_proof_content, current_proof_name)
            
            # Start a new test
            current_proof_name = line.replace(DELIMITER, "").strip().replace("---", "").strip()
            current_proof_content = []
        else:
            # Add the current line to the list of lines for the current proof
            current_proof_content.append(line)
    
    # Run the very last test in the file
    if current_proof_content:
        verify_proof(current_proof_content, current_proof_name)

# part 5: Main Execution
if __name__ == "__main__":
    # You can change this filename to point to any test file you want.
    TEST_FILE_PATH = "all_proofs.txt"
    
    print(f"Loading all proofs from '{TEST_FILE_PATH}'...")
    print("=" * 40)
    load_and_run_tests_from_file(TEST_FILE_PATH)
