"""
Example usage of the NotebookLM Model Builder (Manual Input Version)
"""

from model_builder import ModelBuilder
from notebooklm_knowledge import NotebookLMKnowledge

def main():
    print("=" * 70)
    print("NotebookLM-Guided Model Builder (Manual Input)")
    print("=" * 70)
    print("\nThis application uses knowledge from NotebookLM to guide")
    print("the development of a lactate threshold calculation model.")
    print("\nFirst, gather knowledge from NotebookLM, then add it here.\n")
    
    # Initialize the knowledge base
    kb = NotebookLMKnowledge()
    
    # Try to load existing knowledge
    try:
        kb.load()
        print("✓ Loaded existing knowledge from notebooklm_knowledge.json")
    except:
        print("⚠️  No existing knowledge found.")
        print("\nTo add knowledge:")
        print("1. Open your NotebookLM notebook in a browser")
        print("2. Ask questions and copy the responses")
        print("3. Run: python add_knowledge.py")
        print("\nOr add knowledge programmatically:")
        print("  kb = NotebookLMKnowledge()")
        print("  kb.add_summary('...')")
        print("  kb.save()")
        return
    
    # Show knowledge status
    kb.print_summary()
    
    if not kb.is_complete():
        print("\n⚠️  Knowledge base is incomplete.")
        print("Please add missing fields using: python add_knowledge.py")
        return
    
    # Initialize builder
    builder = ModelBuilder()
    
    print("\n" + "=" * 70)
    print("Generating Model Development Plan")
    print("=" * 70)
    
    # Build and display plan
    builder.print_plan()
    
    # Save plan
    plan_file = "model_development_plan.json"
    builder.save_plan(plan_file)
    
    print(f"\n✓ Plan saved to: {plan_file}")
    print("\nNext steps:")
    print("1. Review the model specification")
    print("2. Implement the recommended code structure")
    print("3. Use the validation criteria to test your model")


if __name__ == "__main__":
    main()
