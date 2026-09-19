import os
import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Skill(BaseModel):
    id: str
    name: str
    description: str
    triggers: List[str] = Field(default_factory=list)
    instructions: str
    enabled: bool = True

class SkillManager:
    """
    Manages loading, parsing, auto-detection, and prompt injection of agent skills.
    Skills are stored as structured markdown files with metadata headers.
    """

    def __init__(self, skills_dir: str = "skills/data"):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self.load_all()

    def parse_skill_file(self, file_path: str) -> Optional[Skill]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            skill_id = os.path.splitext(os.path.basename(file_path))[0]
            name = skill_id.replace("_", " ").title()
            description = ""
            triggers: List[str] = []
            instructions = content

            # Parse YAML-like frontmatter if present
            frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
            if frontmatter_match:
                fm_text = frontmatter_match.group(1)
                instructions = frontmatter_match.group(2).strip()

                for line in fm_text.splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                    elif line.startswith("triggers:"):
                        triggers_part = line.split(":", 1)[1].strip()
                        if triggers_part:
                            triggers = [t.strip() for t in triggers_part.split(",") if t.strip()]

            return Skill(
                id=skill_id,
                name=name,
                description=description or f"Domain skill for {name}",
                triggers=triggers,
                instructions=instructions,
                enabled=True
            )
        except Exception as e:
            print(f"Failed to load skill {file_path}: {e}")
            return None

    def load_all(self):
        self.skills.clear()
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir, exist_ok=True)
            return

        for fname in os.listdir(self.skills_dir):
            if fname.endswith(".md"):
                skill = self.parse_skill_file(os.path.join(self.skills_dir, fname))
                if skill:
                    self.skills[skill.id] = skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)

    def list_skills(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "triggers": s.triggers,
                "enabled": s.enabled
            }
            for s in self.skills.values()
        ]

    def detect_relevant_skills(self, user_prompt: str) -> List[str]:
        """Detect skills whose triggers match the user prompt."""
        lower_prompt = user_prompt.lower()
        matched: List[str] = []
        for s_id, s in self.skills.items():
            if not s.enabled:
                continue
            for trigger in s.triggers:
                if trigger.lower() in lower_prompt:
                    matched.append(s_id)
                    break
        return matched

    def build_system_instructions(self, active_skill_ids: List[str]) -> str:
        """Combine instructions of all active skills to inject into system prompt."""
        if not active_skill_ids:
            return ""

        sections = ["\n### Active Specialized Skills:"]
        for s_id in active_skill_ids:
            skill = self.skills.get(s_id)
            if skill and skill.enabled:
                sections.append(f"\n#### Skill: {skill.name}\n{skill.instructions}")

        return "\n".join(sections)
