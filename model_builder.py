"""
Model Builder using NotebookLM Knowledge
Uses manually input NotebookLM knowledge to guide model development.
"""

from notebooklm_knowledge import NotebookLMKnowledge
from typing import Dict, Any, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelBuilder:
    """Builds models guided by NotebookLM knowledge (manually input)."""
    
    def __init__(self, knowledge_file: Optional[str] = None):
        """
        Initialize the model builder with NotebookLM knowledge.
        
        Args:
            knowledge_file: Path to JSON file with NotebookLM knowledge. If None, uses default.
        """
        self.kb = NotebookLMKnowledge()
        if knowledge_file:
            self.kb.load(knowledge_file)
        else:
            # Try to load default file
            try:
                self.kb.load()
            except:
                logger.info("No existing knowledge file found. Start adding knowledge from NotebookLM.")
    
    def get_knowledge(self) -> Dict[str, Any]:
        """Get all stored knowledge."""
        return self.kb.get_knowledge()
    
    def generate_model_specification(self) -> Dict[str, Any]:
        """
        Generate a model specification based on NotebookLM knowledge.
        
        Returns:
            Model specification dictionary
        """
        knowledge = self.kb.get_knowledge()
        
        if not self.kb.is_complete():
            logger.warning("Knowledge base is incomplete. Some fields may be missing.")
        
        spec = {
            "model_type": "Lactate Threshold Calculator",
            "knowledge_source": knowledge["notebook_id"],
            "notebook_title": knowledge.get("notebook_title", "Unknown"),
            "source_count": knowledge.get("source_count", 0),
            "requirements": knowledge.get("model_requirements", "Not provided"),
            "data_needs": knowledge.get("data_requirements", "Not provided"),
            "methodology": knowledge.get("methodology", "Not provided"),
            "mathematical_approaches": knowledge.get("mathematical_approaches", "Not provided"),
            "validation_criteria": knowledge.get("validation_criteria", "Not provided")
        }
        
        return spec
    
    def generate_code_structure(self) -> Dict[str, Any]:
        """
        Generate code structure recommendations based on the knowledge.
        
        Returns:
            Code structure dictionary
        """
        knowledge = self.kb.get_knowledge()
        
        structure = {
            "recommendations": knowledge.get("code_structure", "Not provided"),
            "key_components": self._extract_key_components(knowledge),
            "suggested_modules": self._suggest_modules(knowledge)
        }
        
        return structure
    
    def _extract_key_components(self, knowledge: Dict[str, Any]) -> list:
        """Extract key components needed for the model."""
        components = []
        
        if knowledge.get("model_requirements"):
            # Try to extract key variables/components from requirements
            req_text = knowledge["model_requirements"].lower()
            if "input" in req_text or "variable" in req_text:
                components.append("Input data processing")
            if "calculation" in req_text or "formula" in req_text:
                components.append("Calculation engine")
            if "validation" in req_text:
                components.append("Validation module")
        
        # Default components
        if not components:
            components = [
                "Data input handler",
                "Lactate threshold calculator",
                "Validation module",
                "Output formatter"
            ]
        
        return components
    
    def _suggest_modules(self, knowledge: Dict[str, Any]) -> list:
        """Suggest Python modules based on knowledge."""
        modules = []
        
        if knowledge.get("mathematical_approaches"):
            modules.append("numpy - For numerical calculations")
            modules.append("scipy - For advanced mathematical functions")
        
        if knowledge.get("data_requirements"):
            modules.append("pandas - For data handling")
        
        modules.extend([
            "json - For configuration and data storage",
            "typing - For type hints",
            "logging - For debugging and monitoring"
        ])
        
        return modules
    
    def build_model_plan(self) -> Dict[str, Any]:
        """
        Create a complete model development plan.
        
        Returns:
            Complete development plan
        """
        logger.info("Building model development plan from NotebookLM knowledge...")
        
        plan = {
            "specification": self.generate_model_specification(),
            "code_structure": self.generate_code_structure(),
            "knowledge_summary": {
                "notebook_id": self.kb.knowledge["notebook_id"],
                "last_updated": self.kb.knowledge.get("last_updated"),
                "completeness": "Complete" if self.kb.is_complete() else "Incomplete"
            }
        }
        
        return plan
    
    def save_plan(self, filename: str = "model_development_plan.json"):
        """Save the development plan to a file."""
        plan = self.build_model_plan()
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
        logger.info(f"Plan saved to {filename}")
    
    def print_plan(self):
        """Print the development plan to console."""
        plan = self.build_model_plan()
        
        print("\n" + "=" * 70)
        print("MODEL DEVELOPMENT PLAN")
        print("=" * 70)
        
        print("\n1. MODEL SPECIFICATION")
        print("-" * 70)
        spec = plan["specification"]
        print(f"Model Type: {spec['model_type']}")
        print(f"Knowledge Source: {spec['knowledge_source']}")
        print(f"Notebook: {spec['notebook_title']} ({spec['source_count']} sources)")
        
        print("\n2. REQUIREMENTS")
        print("-" * 70)
        print(spec['requirements'])
        
        print("\n3. DATA NEEDS")
        print("-" * 70)
        print(spec['data_needs'])
        
        print("\n4. METHODOLOGY")
        print("-" * 70)
        print(spec['methodology'])
        
        if spec.get('mathematical_approaches'):
            print("\n5. MATHEMATICAL APPROACHES")
            print("-" * 70)
            print(spec['mathematical_approaches'])
        
        print("\n6. CODE STRUCTURE")
        print("-" * 70)
        structure = plan["code_structure"]
        print("Key Components:")
        for component in structure["key_components"]:
            print(f"  - {component}")
        print("\nSuggested Modules:")
        for module in structure["suggested_modules"]:
            print(f"  - {module}")
        
        if structure.get("recommendations") and structure["recommendations"] != "Not provided":
            print("\nRecommendations:")
            print(structure["recommendations"])
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    builder = ModelBuilder()
    
    print("=" * 70)
    print("Building Model Development Plan")
    print("=" * 70)
    
    # Check knowledge completeness
    builder.kb.print_summary()
    
    if not builder.kb.is_complete():
        print("\n⚠️  Knowledge base is incomplete.")
        print("Please add knowledge from NotebookLM using:")
        print("  from notebooklm_knowledge import NotebookLMKnowledge")
        print("  kb = NotebookLMKnowledge()")
        print("  kb.add_summary('...')")
        print("  kb.add_model_requirements('...')")
        print("  # etc.")
        print("  kb.save()")
    else:
        builder.print_plan()
        builder.save_plan()
