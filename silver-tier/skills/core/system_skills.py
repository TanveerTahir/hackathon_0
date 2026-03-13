"""
System Skills - Core functionality for the AI Employee

This module contains fundamental skills for reading, parsing, and processing
information within the AI Employee system.

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import re
import json

from ..core.base_skill import BaseSkill, SkillExecutionError


class ReadMarkdownFileSkill(BaseSkill):
    """
    Skill: read_markdown_file
    
    Reads and parses Markdown files from the vault, extracting both
    frontmatter metadata and content.
    
    Input:
        - file_path: str - Path to the markdown file (relative or absolute)
        - include_content: bool - Whether to include full content (default: True)
        - parse_frontmatter: bool - Whether to parse frontmatter (default: True)
    
    Output:
        - success: bool
        - data: dict containing:
            - file_path: str
            - exists: bool
            - frontmatter: dict (if parsed)
            - content: str (if requested)
            - word_count: int
            - line_count: int
            - last_modified: str (ISO format)
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="read_markdown_file",
            description="Read and parse Markdown files from the vault",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown file"
                },
                "include_content": {
                    "type": "boolean",
                    "description": "Include full file content",
                    "default": True
                },
                "parse_frontmatter": {
                    "type": "boolean",
                    "description": "Parse YAML frontmatter",
                    "default": True
                }
            },
            "required": ["file_path"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "exists": {"type": "boolean"},
                        "frontmatter": {"type": "object"},
                        "content": {"type": "string"},
                        "word_count": {"type": "integer"},
                        "line_count": {"type": "integer"},
                        "last_modified": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the read markdown file skill"""
        try:
            file_path = kwargs.get("file_path")
            include_content = kwargs.get("include_content", True)
            parse_frontmatter = kwargs.get("parse_frontmatter", True)
            
            if not file_path:
                raise SkillExecutionError("file_path is required")
            
            # Resolve file path
            path = Path(file_path)
            if not path.is_absolute() and self.vault_path:
                path = self.vault_path / file_path
            
            result = {
                "file_path": str(path),
                "exists": path.exists(),
                "frontmatter": {},
                "content": "",
                "word_count": 0,
                "line_count": 0,
                "last_modified": None
            }
            
            if not path.exists():
                self.logger.warning(f"File not found: {path}")
                return {"success": True, "data": result, "error": None}
            
            # Read file
            content = path.read_text(encoding='utf-8')
            result["last_modified"] = datetime.fromtimestamp(
                path.stat().st_mtime
            ).isoformat()
            
            # Parse frontmatter if requested
            if parse_frontmatter:
                frontmatter, content_body = self._parse_frontmatter(content)
                result["frontmatter"] = frontmatter
                if include_content:
                    result["content"] = content_body
            elif include_content:
                result["content"] = content
            
            # Calculate metrics
            if result["content"]:
                result["word_count"] = len(result["content"].split())
                result["line_count"] = len(result["content"].splitlines())
            
            self._write_log({
                "action": "read_file",
                "file_path": str(path),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown content"""
        frontmatter = {}
        body = content
        
        # Match frontmatter between --- markers
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            fm_text = match.group(1)
            body = match.group(2)
            
            # Simple YAML parser for key-value pairs
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Parse value types
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value.isdigit():
                        value = int(value)
                    elif value.startswith('[') and value.endswith(']'):
                        value = [v.strip() for v in value[1:-1].split(',')]
                    
                    frontmatter[key] = value
        
        return frontmatter, body


class ParseHackathonRequirementsSkill(BaseSkill):
    """
    Skill: parse_hackathon_requirements
    
    Parses the hackathon document to extract requirements, tiers, and deliverables.
    
    Input:
        - document_path: str - Path to hackathon document
        - tier: str - Target tier (bronze, silver, gold, platinum)
    
    Output:
        - success: bool
        - data: dict containing:
            - tier_requirements: list
            - deliverables: list
            - estimated_time: str
            - architecture_components: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="parse_hackathon_requirements",
            description="Parse hackathon document to extract requirements and deliverables",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "document_path": {
                    "type": "string",
                    "description": "Path to hackathon document"
                },
                "tier": {
                    "type": "string",
                    "description": "Target tier level",
                    "enum": ["bronze", "silver", "gold", "platinum"]
                }
            },
            "required": ["document_path", "tier"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "tier_requirements": {"type": "array"},
                        "deliverables": {"type": "array"},
                        "estimated_time": {"type": "string"},
                        "architecture_components": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the parse hackathon requirements skill"""
        try:
            document_path = kwargs.get("document_path")
            tier = kwargs.get("tier", "silver")
            
            if not document_path:
                raise SkillExecutionError("document_path is required")
            
            # Read document
            path = Path(document_path)
            if not path.is_absolute():
                path = self.vault_path / path if self.vault_path else Path(document_path)
            
            if not path.exists():
                raise SkillExecutionError(f"Document not found: {path}")
            
            content = path.read_text(encoding='utf-8')
            
            # Extract tier requirements
            tier_requirements = self._extract_tier_requirements(content, tier)
            
            # Extract deliverables
            deliverables = self._extract_deliverables(content, tier)
            
            # Extract estimated time
            estimated_time = self._extract_estimated_time(content, tier)
            
            # Extract architecture components
            architecture_components = self._extract_architecture(content)
            
            result = {
                "tier": tier,
                "tier_requirements": tier_requirements,
                "deliverables": deliverables,
                "estimated_time": estimated_time,
                "architecture_components": architecture_components
            }
            
            self._write_log({
                "action": "parse_requirements",
                "tier": tier,
                "document": str(path),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error parsing requirements: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _extract_tier_requirements(self, content: str, tier: str) -> List[str]:
        """Extract requirements for a specific tier"""
        requirements = []
        
        # Pattern to find tier section
        tier_patterns = {
            "bronze": r"##?\s*\*\*Bronze Tier.*?\*\*(.*?)(?=##|\Z)",
            "silver": r"##?\s*\*\*Silver Tier.*?\*\*(.*?)(?=##|\Z)",
            "gold": r"##?\s*\*\*Gold Tier.*?\*\*(.*?)(?=##|\Z)",
            "platinum": r"##?\s*\*\*Platinum Tier.*?\*\*(.*?)(?=##|\Z)"
        }
        
        pattern = tier_patterns.get(tier, "")
        if pattern:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                tier_section = match.group(1)
                # Extract numbered or bulleted items
                items = re.findall(r'[\d\-\*]\s+(.+?)(?=\n[\d\-\*]|\n\n|\Z)', tier_section)
                requirements = [item.strip() for item in items if item.strip()]
        
        return requirements
    
    def _extract_deliverables(self, content: str, tier: str) -> List[str]:
        """Extract deliverables for a specific tier"""
        deliverables = []
        
        # Look for deliverables section
        pattern = r"(?:deliverables|achievements?|must have)[:\s]+(.*?)(?=\n\n|\Z)"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                items = re.findall(r'[\-\*]\s+(.+?)\n', match)
                deliverables.extend([item.strip() for item in items])
        
        return deliverables[:10]  # Limit to 10 items
    
    def _extract_estimated_time(self, content: str, tier: str) -> str:
        """Extract estimated time for a tier"""
        pattern = r"(?:estimated time|time estimate)[:\s]+(\d+-?\d*\s*(?:hours?|days?))"
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1) if match else "Not specified"
    
    def _extract_architecture(self, content: str) -> List[str]:
        """Extract architecture components"""
        components = []
        
        # Look for architecture section
        pattern = r"(?:architecture|components|layers)[:\s]+(.*?)(?=\n\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            arch_section = match.group(1)
            # Extract component names
            items = re.findall(r'\*\*([^*]+)\*\*', arch_section)
            components = [item.strip() for item in items]
        
        return components


class TaskExtractorSkill(BaseSkill):
    """
    Skill: task_extractor
    
    Extracts actionable tasks from text content (emails, messages, documents).
    
    Input:
        - content: str - Text content to analyze
        - source_type: str - Type of source (email, whatsapp, linkedin, document)
        - priority_keywords: list - Keywords indicating high priority
    
    Output:
        - success: bool
        - data: dict containing:
            - tasks: list of extracted tasks
            - context: dict with source information
            - confidence: float (0-1)
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="task_extractor",
            description="Extract actionable tasks from text content",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
        
        # Default priority keywords
        self.priority_keywords = self.config.get(
            "priority_keywords",
            ["urgent", "asap", "immediately", "priority", "important", "deadline"]
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Text content to analyze"
                },
                "source_type": {
                    "type": "string",
                    "description": "Type of source",
                    "enum": ["email", "whatsapp", "linkedin", "document", "other"]
                },
                "priority_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords indicating high priority"
                }
            },
            "required": ["content"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "tasks": {"type": "array"},
                        "context": {"type": "object"},
                        "confidence": {"type": "number"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the task extraction skill"""
        try:
            content = kwargs.get("content", "")
            source_type = kwargs.get("source_type", "other")
            priority_keywords = kwargs.get("priority_keywords", self.priority_keywords)
            
            if not content:
                raise SkillExecutionError("content is required")
            
            # Extract tasks
            tasks = self._extract_tasks(content, source_type, priority_keywords)
            
            # Calculate confidence
            confidence = self._calculate_confidence(tasks, content)
            
            # Build context
            context = {
                "source_type": source_type,
                "content_length": len(content),
                "extraction_timestamp": datetime.now().isoformat(),
                "priority_keywords_used": priority_keywords
            }
            
            result = {
                "tasks": tasks,
                "context": context,
                "confidence": confidence
            }
            
            self._write_log({
                "action": "extract_tasks",
                "source_type": source_type,
                "tasks_found": len(tasks),
                "confidence": confidence,
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error extracting tasks: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _extract_tasks(self, content: str, source_type: str, priority_keywords: List[str]) -> List[Dict]:
        """Extract tasks from content"""
        tasks = []
        
        # Patterns for task indicators
        task_patterns = [
            r'(?:please|kindly|could you|can you|need to|want to|would like to)\s+(.+?)(?:\.|\n|$)',
            r'(?:action required|to[- ]do|task|next step)[:\s]+(.+?)(?:\.|\n|$)',
            r'-\s*\[\s*\]\s*(.+?)(?:\n|$)',  # Markdown checkbox
            r'(?:follow[- ]?up|schedule|arrange|organize|prepare|send|reply|review|check|confirm)\s+(.+?)(?:\.|\n|$)',
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                task_text = match.strip()
                if len(task_text) > 5:  # Filter out very short matches
                    priority = self._determine_priority(task_text, priority_keywords)
                    tasks.append({
                        "title": task_text,
                        "description": self._generate_description(task_text, content),
                        "priority": priority,
                        "source_type": source_type,
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    })
        
        # Remove duplicates
        seen = set()
        unique_tasks = []
        for task in tasks:
            if task["title"] not in seen:
                seen.add(task["title"])
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _determine_priority(self, task_text: str, priority_keywords: List[str]) -> str:
        """Determine task priority based on keywords"""
        text_lower = task_text.lower()
        for keyword in priority_keywords:
            if keyword.lower() in text_lower:
                return "high"
        return "normal"
    
    def _generate_description(self, task_text: str, full_content: str) -> str:
        """Generate a description for the task"""
        # Find surrounding context (2 sentences before and after)
        sentences = re.split(r'(?<=[.!?])\s+', full_content)
        
        for i, sentence in enumerate(sentences):
            if task_text[:20].lower() in sentence.lower():
                # Get context around the task
                start = max(0, i - 1)
                end = min(len(sentences), i + 2)
                context = ' '.join(sentences[start:end])
                return context[:200]  # Limit to 200 chars
        
        return task_text
    
    def _calculate_confidence(self, tasks: List[Dict], content: str) -> float:
        """Calculate confidence score for extraction"""
        if not tasks:
            return 0.0
        
        # Factors affecting confidence
        content_length = len(content)
        task_count = len(tasks)
        
        # Base confidence
        confidence = 0.5
        
        # Adjust based on content length
        if content_length > 100:
            confidence += 0.1
        if content_length > 500:
            confidence += 0.1
        
        # Adjust based on task count (not too few, not too many)
        if 1 <= task_count <= 10:
            confidence += 0.2
        elif task_count > 10:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)


class TaskPrioritizerSkill(BaseSkill):
    """
    Skill: task_prioritizer
    
    Prioritizes tasks based on urgency, importance, and deadlines.
    
    Input:
        - tasks: list - List of task dictionaries
        - business_goals: dict - Current business goals and priorities
        - max_priority_tasks: int - Maximum number of high priority tasks
    
    Output:
        - success: bool
        - data: dict containing:
            - prioritized_tasks: list (sorted by priority)
            - priority_distribution: dict
            - recommendations: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="task_prioritizer",
            description="Prioritize tasks based on urgency, importance, and deadlines",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of tasks to prioritize"
                },
                "business_goals": {
                    "type": "object",
                    "description": "Current business goals"
                },
                "max_priority_tasks": {
                    "type": "integer",
                    "description": "Max high priority tasks",
                    "default": 5
                }
            },
            "required": ["tasks"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "prioritized_tasks": {"type": "array"},
                        "priority_distribution": {"type": "object"},
                        "recommendations": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the task prioritization skill"""
        try:
            tasks = kwargs.get("tasks", [])
            business_goals = kwargs.get("business_goals", {})
            max_priority_tasks = kwargs.get("max_priority_tasks", 5)
            
            if not tasks:
                return {"success": True, "data": {
                    "prioritized_tasks": [],
                    "priority_distribution": {},
                    "recommendations": []
                }, "error": None}
            
            # Score and prioritize tasks
            scored_tasks = self._score_tasks(tasks, business_goals)
            
            # Sort by score
            prioritized = sorted(scored_tasks, key=lambda x: x["priority_score"], reverse=True)
            
            # Assign priority levels
            prioritized = self._assign_priority_levels(prioritized, max_priority_tasks)
            
            # Calculate distribution
            distribution = self._calculate_distribution(prioritized)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(prioritized, business_goals)
            
            result = {
                "prioritized_tasks": prioritized,
                "priority_distribution": distribution,
                "recommendations": recommendations
            }
            
            self._write_log({
                "action": "prioritize_tasks",
                "task_count": len(tasks),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error prioritizing tasks: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _score_tasks(self, tasks: List[Dict], business_goals: Dict) -> List[Dict]:
        """Score tasks based on multiple factors"""
        scored = []
        
        for task in tasks:
            score = 0
            
            # Base priority score
            priority_scores = {"high": 30, "normal": 15, "low": 5}
            score += priority_scores.get(task.get("priority", "normal"), 15)
            
            # Urgency bonus
            if "urgent" in task.get("title", "").lower():
                score += 20
            if "asap" in task.get("title", "").lower():
                score += 25
            
            # Business goal alignment
            goal_keywords = business_goals.get("keywords", [])
            for keyword in goal_keywords:
                if keyword.lower() in task.get("title", "").lower():
                    score += 15
            
            # Revenue impact
            revenue_keywords = ["invoice", "payment", "revenue", "sale", "client"]
            for keyword in revenue_keywords:
                if keyword in task.get("title", "").lower():
                    score += 10
            
            # Deadline proximity
            if "deadline" in task:
                score += 20
            
            task["priority_score"] = score
            scored.append(task)
        
        return scored
    
    def _assign_priority_levels(self, tasks: List[Dict], max_high: int) -> List[Dict]:
        """Assign priority levels based on scores"""
        sorted_tasks = sorted(tasks, key=lambda x: x["priority_score"], reverse=True)
        
        for i, task in enumerate(sorted_tasks):
            if i < max_high and task["priority_score"] >= 40:
                task["priority_level"] = "critical"
            elif i < max_high * 2 and task["priority_score"] >= 25:
                task["priority_level"] = "high"
            elif task["priority_score"] >= 15:
                task["priority_level"] = "normal"
            else:
                task["priority_level"] = "low"
        
        return sorted_tasks
    
    def _calculate_distribution(self, tasks: List[Dict]) -> Dict[str, int]:
        """Calculate priority distribution"""
        distribution = {"critical": 0, "high": 0, "normal": 0, "low": 0}
        for task in tasks:
            level = task.get("priority_level", "normal")
            distribution[level] = distribution.get(level, 0) + 1
        return distribution
    
    def _generate_recommendations(self, tasks: List[Dict], business_goals: Dict) -> List[str]:
        """Generate prioritization recommendations"""
        recommendations = []
        
        critical_count = sum(1 for t in tasks if t.get("priority_level") == "critical")
        
        if critical_count > 5:
            recommendations.append(
                f"You have {critical_count} critical tasks. Consider delegating or rescheduling some."
            )
        
        if not tasks:
            recommendations.append("No tasks to prioritize. Great job staying on top of things!")
        
        revenue_tasks = [t for t in tasks if any(
            kw in t.get("title", "").lower() 
            for kw in ["invoice", "payment", "revenue"]
        )]
        
        if revenue_tasks and len(revenue_tasks) < len(tasks) / 3:
            recommendations.append(
                "Consider prioritizing revenue-generating tasks to meet business goals."
            )
        
        return recommendations


class ExecutionPlannerSkill(BaseSkill):
    """
    Skill: execution_planner
    
    Creates detailed execution plans for tasks, breaking them into actionable steps.
    
    Input:
        - task: dict - Task to plan
        - available_resources: list - Available tools/skills
        - constraints: dict - Time, budget, or other constraints
    
    Output:
        - success: bool
        - data: dict containing:
            - plan_id: str
            - task_title: str
            - steps: list of action steps
            - estimated_duration: str
            - required_approvals: list
            - resources_needed: list
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="execution_planner",
            description="Create detailed execution plans for tasks",
            version="1.0.0",
            vault_path=vault_path,
            config=config
        )
        
        # Task type templates
        self.task_templates = self.config.get("task_templates", {
            "email_reply": ["Draft response", "Review content", "Send email"],
            "invoice_generation": ["Gather client info", "Calculate amount", "Generate PDF", "Send invoice"],
            "social_post": ["Create content", "Review guidelines", "Schedule post", "Monitor engagement"],
            "meeting_prep": ["Review agenda", "Prepare materials", "Send reminders", "Setup room"],
        })
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "object",
                    "description": "Task to create plan for"
                },
                "available_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Available tools/skills"
                },
                "constraints": {
                    "type": "object",
                    "description": "Time, budget, or other constraints"
                }
            },
            "required": ["task"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "plan_id": {"type": "string"},
                        "task_title": {"type": "string"},
                        "steps": {"type": "array"},
                        "estimated_duration": {"type": "string"},
                        "required_approvals": {"type": "array"},
                        "resources_needed": {"type": "array"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the execution planner skill"""
        try:
            task = kwargs.get("task", {})
            available_resources = kwargs.get("available_resources", [])
            constraints = kwargs.get("constraints", {})
            
            if not task:
                raise SkillExecutionError("task is required")
            
            # Generate plan ID
            plan_id = f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task.get('title', 'unknown')[:20]}"
            
            # Determine task type and get template
            task_type = self._determine_task_type(task)
            template_steps = self.task_templates.get(task_type, ["Analyze task", "Execute action", "Verify completion"])
            
            # Create detailed steps
            steps = self._create_steps(template_steps, task, available_resources)
            
            # Estimate duration
            duration = self._estimate_duration(steps, constraints)
            
            # Determine required approvals
            approvals = self._determine_approvals(task, constraints)
            
            # Identify resources needed
            resources = self._identify_resources(steps, available_resources)
            
            result = {
                "plan_id": plan_id,
                "task_title": task.get("title", "Untitled Task"),
                "task_type": task_type,
                "steps": steps,
                "estimated_duration": duration,
                "required_approvals": approvals,
                "resources_needed": resources,
                "constraints": constraints,
                "created_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "create_plan",
                "task_title": task.get("title", ""),
                "plan_id": plan_id,
                "step_count": len(steps),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error creating execution plan: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _determine_task_type(self, task: Dict) -> str:
        """Determine task type from title/description"""
        title = task.get("title", "").lower()
        
        if any(word in title for word in ["email", "reply", "respond"]):
            return "email_reply"
        elif any(word in title for word in ["invoice", "bill", "payment"]):
            return "invoice_generation"
        elif any(word in title for word in ["post", "social", "linkedin", "twitter", "facebook"]):
            return "social_post"
        elif any(word in title for word in ["meeting", "call", "appointment"]):
            return "meeting_prep"
        
        return "general"
    
    def _create_steps(self, template: List[str], task: Dict, resources: List[str]) -> List[Dict]:
        """Create detailed steps from template"""
        steps = []
        
        for i, step_template in enumerate(template):
            steps.append({
                "step_number": i + 1,
                "title": step_template,
                "description": f"Execute: {step_template}",
                "status": "pending",
                "estimated_minutes": 10,
                "requires_approval": False,
                "resources": []
            })
        
        return steps
    
    def _estimate_duration(self, steps: List[Dict], constraints: Dict) -> str:
        """Estimate total duration"""
        total_minutes = sum(step.get("estimated_minutes", 10) for step in steps)
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{total_minutes}m"
    
    def _determine_approvals(self, task: Dict, constraints: Dict) -> List[str]:
        """Determine required approvals"""
        approvals = []
        
        # Check for sensitive actions
        sensitive_keywords = ["payment", "send", "delete", "approve", "transfer"]
        title = task.get("title", "").lower()
        
        if any(word in title for word in sensitive_keywords):
            approvals.append("human_approval")
        
        # Check budget constraints
        if constraints.get("budget_limit"):
            approvals.append("budget_approval")
        
        return approvals
    
    def _identify_resources(self, steps: List[Dict], available: List[str]) -> List[str]:
        """Identify resources needed"""
        needed = []
        
        # Default resources
        default_resources = ["file_system", "markdown_parser"]
        
        for resource in default_resources:
            if resource in available or not available:
                needed.append(resource)
        
        return needed


# Export all system skills
__all__ = [
    "ReadMarkdownFileSkill",
    "ParseHackathonRequirementsSkill",
    "TaskExtractorSkill",
    "TaskPrioritizerSkill",
    "ExecutionPlannerSkill"
]
