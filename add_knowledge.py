#!/usr/bin/env python3
"""
Interactive script to add NotebookLM knowledge manually.
Run this script and paste responses from NotebookLM.
"""

from notebooklm_knowledge import NotebookLMKnowledge
import sys

def main():
    kb = NotebookLMKnowledge()
    
    # Try to load existing knowledge
    try:
        kb.load()
        print("✓ Loaded existing knowledge")
    except:
        print("Starting with empty knowledge base")
    
    kb.print_summary()
    
    print("\n" + "=" * 70)
    print("Add NotebookLM Knowledge")
    print("=" * 70)
    print("\nPaste responses from your NotebookLM notebook.")
    print("Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done with each field.\n")
    
    # Add summary
    if not kb.knowledge.get("summary"):
        print("1. NOTEBOOK SUMMARY")
        print("   (What is this notebook about? List main sources.)")
        print("   Paste here (Ctrl+D when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            summary = "\n".join(lines)
            if summary.strip():
                kb.add_summary(summary)
                print("✓ Summary added\n")
    else:
        print("✓ Summary already exists (skipping)\n")
    
    # Add model requirements
    if not kb.knowledge.get("model_requirements"):
        print("2. MODEL REQUIREMENTS")
        print("   (Key variables, parameters, considerations for building the model)")
        print("   Paste here (Ctrl+D when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            requirements = "\n".join(lines)
            if requirements.strip():
                kb.add_model_requirements(requirements)
                print("✓ Model requirements added\n")
    else:
        print("✓ Model requirements already exist (skipping)\n")
    
    # Add data requirements
    if not kb.knowledge.get("data_requirements"):
        print("3. DATA REQUIREMENTS")
        print("   (What data is needed? Measurements, sample sizes, quality considerations)")
        print("   Paste here (Ctrl+D when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            data_req = "\n".join(lines)
            if data_req.strip():
                kb.add_data_requirements(data_req)
                print("✓ Data requirements added\n")
    else:
        print("✓ Data requirements already exist (skipping)\n")
    
    # Add methodology
    if not kb.knowledge.get("methodology"):
        print("4. METHODOLOGY RECOMMENDATIONS")
        print("   (Recommended methodologies, compare approaches)")
        print("   Paste here (Ctrl+D when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            methodology = "\n".join(lines)
            if methodology.strip():
                kb.add_methodology(methodology)
                print("✓ Methodology added\n")
    else:
        print("✓ Methodology already exists (skipping)\n")
    
    # Add mathematical approaches
    if not kb.knowledge.get("mathematical_approaches"):
        print("5. MATHEMATICAL APPROACHES (Optional)")
        print("   (D-max, MLSS, FTP, etc. - compare methods)")
        print("   Paste here (Ctrl+D when done, or press Ctrl+D to skip):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            approaches = "\n".join(lines)
            if approaches.strip():
                kb.add_mathematical_approaches(approaches)
                print("✓ Mathematical approaches added\n")
    else:
        print("✓ Mathematical approaches already exist (skipping)\n")
    
    # Add validation criteria
    if not kb.knowledge.get("validation_criteria"):
        print("6. VALIDATION CRITERIA (Optional)")
        print("   (How to validate the model? Metrics, testing approaches)")
        print("   Paste here (Ctrl+D when done, or press Ctrl+D to skip):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            validation = "\n".join(lines)
            if validation.strip():
                kb.add_validation_criteria(validation)
                print("✓ Validation criteria added\n")
    else:
        print("✓ Validation criteria already exist (skipping)\n")
    
    # Save
    kb.save()
    print("\n" + "=" * 70)
    print("Knowledge saved!")
    print("=" * 70)
    kb.print_summary()


if __name__ == "__main__":
    main()
