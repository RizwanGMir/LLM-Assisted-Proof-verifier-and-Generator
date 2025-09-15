# LLM-Assisted-Proof-verifier-and-Generator
Proof Verifier – Verifies proofs in a given axiomatic system using axioms and inference rules.  
LLM-Assisted Proof Generator – Extends the verifier with an LLM-guided search to suggest or generate proof steps.

# 1) Verifier

This project is a simple tool written in Python that checks if a formal logic proof is correct.

## What It Does

The program reads a text file that contains one or more proofs. For each proof, it checks every single line to make sure it follows the rules.

The rules it checks are:
1.  Is the line a given **Premise**?
2.  Does the line match one of the three allowed **Axioms** (AX1, AX2, AX3)?
3.  Does the line correctly follow from two previous lines using **Modus Ponens** (MP)?

If every line in a proof is correct, the program will report that the proof is **VALID**. If it finds even one mistake, it will stop and report that the proof **FAILED**, telling you which line has the error.

This tool helps you make sure your logic proofs are built correctly from start to finish.
