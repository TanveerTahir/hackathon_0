"""
Vault/Memory Skills - Knowledge Management for AI Employee

This module contains skills for reading, writing, and managing tasks
in the Obsidian vault (the AI's long-term memory).

Silver Tier Implementation - Personal AI Employee Hackathon 0
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import re
import yaml

from ..core.base_skill import BaseSkill, SkillExecutionError


class ReadVaultTasksSkill(BaseSkill):
    """
    Skill: read_vault_tasks
    
    Reads tasks from vault folders with filtering and sorting capabilities.
    
    Input:
        - folder: str - Folder to read from (Needs_Action, Plans, etc.)
        - filters: dict - Filters to apply (priority, type, status, etc.)
        - sort_by: str - Field to sort by
        - sort_order: str - Sort order (asc, desc)
        - limit: int - Maximum number of tasks to return
    
    Output:
        - success: bool
        - data: dict containing:
            - tasks: list of task objects
            - total_count: int
            - folder: str
            - filters_applied: dict
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="read_vault_tasks",
            description="Read tasks from vault folders with filtering and sorting",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.vault_folders = [
            "Needs_Action",
            "Plans",
            "Pending_Approval",
            "Approved",
            "Rejected",
            "Done",
            "Inbox"
        ]
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "Folder to read from"
                },
                "filters": {
                    "type": "object",
                    "description": "Filters to apply"
                },
                "sort_by": {
                    "type": "string",
                    "description": "Field to sort by"
                },
                "sort_order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum tasks to return"
                }
            },
            "required": []
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
                        "total_count": {"type": "integer"},
                        "folder": {"type": "string"},
                        "filters_applied": {"type": "object"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the read vault tasks skill"""
        try:
            folder = kwargs.get("folder", "Needs_Action")
            filters = kwargs.get("filters", {})
            sort_by = kwargs.get("sort_by", "created")
            sort_order = kwargs.get("sort_order", "desc")
            limit = kwargs.get("limit", 100)
            
            if not self.vault_path:
                raise SkillExecutionError("vault_path not configured")
            
            # Get folder path
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                return {"success": True, "data": {
                    "tasks": [],
                    "total_count": 0,
                    "folder": folder,
                    "filters_applied": filters,
                    "message": f"Folder does not exist: {folder}"
                }, "error": None}
            
            # Read all markdown files
            tasks = self._read_task_files(folder_path)
            
            # Apply filters
            filtered_tasks = self._apply_filters(tasks, filters)
            
            # Sort tasks
            sorted_tasks = self._sort_tasks(filtered_tasks, sort_by, sort_order)
            
            # Apply limit
            limited_tasks = sorted_tasks[:limit]
            
            result = {
                "tasks": limited_tasks,
                "total_count": len(filtered_tasks),
                "folder": folder,
                "filters_applied": filters,
                "read_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "read_vault_tasks",
                "folder": folder,
                "tasks_found": len(tasks),
                "tasks_returned": len(limited_tasks),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error reading vault tasks: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _read_task_files(self, folder_path: Path) -> List[Dict]:
        """Read all task files from folder"""
        tasks = []
        
        for file_path in folder_path.glob("*.md"):
            try:
                task = self._parse_task_file(file_path)
                if task:
                    task["_file_path"] = str(file_path)
                    tasks.append(task)
            except Exception as e:
                self.logger.warning(f"Error reading {file_path}: {e}")
        
        return tasks
    
    def _parse_task_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a task markdown file"""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = {}
        body = content
        
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if frontmatter_match:
            fm_text = frontmatter_match.group(1)
            body = frontmatter_match.group(2)
            
            try:
                frontmatter = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError:
                # Fallback to simple parsing
                frontmatter = self._parse_frontmatter_simple(fm_text)
        
        # Build task object
        task = {
            "frontmatter": frontmatter,
            "body": body.strip(),
            "title": frontmatter.get("title", file_path.stem),
            "type": frontmatter.get("type", "unknown"),
            "priority": frontmatter.get("priority", "normal"),
            "status": frontmatter.get("status", "pending"),
            "created": frontmatter.get("created", frontmatter.get("created_at")),
            "task_id": frontmatter.get("task_id"),
            "file_name": file_path.name
        }
        
        return task
    
    def _parse_frontmatter_simple(self, fm_text: str) -> Dict:
        """Simple frontmatter parser fallback"""
        frontmatter = {}
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
                
                frontmatter[key] = value
        
        return frontmatter
    
    def _apply_filters(self, tasks: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters to tasks"""
        if not filters:
            return tasks
        
        filtered = []
        for task in tasks:
            match = True
            
            for key, value in filters.items():
                task_value = task.get(key) or task.get("frontmatter", {}).get(key)
                
                if isinstance(value, list):
                    if task_value not in value:
                        match = False
                        break
                elif task_value != value:
                    match = False
                    break
            
            if match:
                filtered.append(task)
        
        return filtered
    
    def _sort_tasks(self, tasks: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
        """Sort tasks by field"""
        reverse = sort_order == "desc"
        
        def get_sort_key(task):
            value = task.get(sort_by) or task.get("frontmatter", {}).get(sort_by)
            if value is None:
                return ""
            if isinstance(value, str):
                return value.lower()
            return value
        
        return sorted(tasks, key=get_sort_key, reverse=reverse)


class WriteVaultTasksSkill(BaseSkill):
    """
    Skill: write_vault_tasks
    
    Creates and updates task files in the vault.
    
    Input:
        - task_data: dict - Task data to write
        - folder: str - Target folder
        - update_mode: str - Create, update, or upsert
        - file_path: str - Specific file path (for updates)
    
    Output:
        - success: bool
        - data: dict containing:
            - file_path: str
            - task_id: str
            - operation: str (created, updated)
            - timestamp: str
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="write_vault_tasks",
            description="Create and update task files in the vault",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_data": {
                    "type": "object",
                    "description": "Task data to write"
                },
                "folder": {
                    "type": "string",
                    "description": "Target folder"
                },
                "update_mode": {
                    "type": "string",
                    "enum": ["create", "update", "upsert"],
                    "description": "Operation mode"
                },
                "file_path": {
                    "type": "string",
                    "description": "Specific file path for updates"
                }
            },
            "required": ["task_data"]
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
                        "task_id": {"type": "string"},
                        "operation": {"type": "string"},
                        "timestamp": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the write vault tasks skill"""
        try:
            task_data = kwargs.get("task_data", {})
            folder = kwargs.get("folder", "Needs_Action")
            update_mode = kwargs.get("update_mode", "create")
            file_path = kwargs.get("file_path")
            
            if not self.vault_path:
                raise SkillExecutionError("vault_path not configured")
            
            if update_mode == "create":
                result = self._create_task(task_data, folder)
            elif update_mode == "update":
                result = self._update_task(task_data, file_path)
            else:  # upsert
                result = self._upsert_task(task_data, folder, file_path)
            
            self._write_log({
                "action": "write_vault_tasks",
                "operation": result.get("operation"),
                "file_path": result.get("file_path"),
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error writing vault tasks: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _create_task(self, task_data: Dict, folder: str) -> Dict:
        """Create a new task file"""
        # Ensure folder exists
        folder_path = self.vault_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Generate task ID
        task_id = task_data.get("task_id", f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Generate filename
        safe_title = re.sub(r'[^\w\s-]', '', task_data.get("title", "Untitled"))[:30]
        safe_title = safe_title.replace(" ", "_")
        filename = f"{safe_title}_{task_id}.md"
        file_path = folder_path / filename
        
        # Generate content
        content = self._generate_task_content(task_data, task_id)
        
        # Write file
        file_path.write_text(content, encoding='utf-8')
        
        return {
            "file_path": str(file_path),
            "task_id": task_id,
            "operation": "created",
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_task(self, task_data: Dict, file_path: str) -> Dict:
        """Update an existing task file"""
        if not file_path:
            raise SkillExecutionError("file_path required for update")
        
        path = Path(file_path)
        if not path.is_absolute():
            path = self.vault_path / file_path
        
        if not path.exists():
            raise SkillExecutionError(f"File not found: {path}")
        
        # Read existing content
        content = path.read_text(encoding='utf-8')
        
        # Update frontmatter
        updated_content = self._update_frontmatter(content, task_data)
        
        # Write back
        path.write_text(updated_content, encoding='utf-8')
        
        # Extract task ID from existing frontmatter
        task_id = self._extract_task_id(content)
        
        return {
            "file_path": str(path),
            "task_id": task_id or "unknown",
            "operation": "updated",
            "timestamp": datetime.now().isoformat()
        }
    
    def _upsert_task(self, task_data: Dict, folder: str, file_path: str) -> Dict:
        """Update if exists, create otherwise"""
        if file_path:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.vault_path / file_path
            
            if path.exists():
                return self._update_task(task_data, file_path)
        
        return self._create_task(task_data, folder)
    
    def _generate_task_content(self, task_data: Dict, task_id: str) -> str:
        """Generate markdown content for task"""
        # Build frontmatter
        frontmatter = {
            "task_id": task_id,
            "title": task_data.get("title", "Untitled"),
            "type": task_data.get("type", "general"),
            "priority": task_data.get("priority", "normal"),
            "status": task_data.get("status", "pending"),
            "created": task_data.get("created", datetime.now().isoformat()),
        }
        
        # Add optional fields
        for key in ["description", "source", "category", "tags", "due_date"]:
            if key in task_data:
                frontmatter[key] = task_data[key]
        
        # Generate YAML frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        
        frontmatter_text = "\n".join(fm_lines)
        
        # Generate body
        body = f"""

# Task: {task_data.get('title', 'Untitled')}

"""
        
        if task_data.get("description"):
            body += f"## Description\n\n{task_data['description']}\n\n"
        
        body += "## Action Items\n\n"
        for action in task_data.get("actions", ["- [ ] Complete task"]):
            body += f"{action}\n"
        
        if task_data.get("notes"):
            body += f"\n## Notes\n\n{task_data['notes']}\n"
        
        body += "\n---\n*Generated by AI Employee Skill System*\n"
        
        return frontmatter_text + body
    
    def _update_frontmatter(self, content: str, updates: Dict) -> str:
        """Update frontmatter in existing content"""
        # Find frontmatter section
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        
        if not match:
            # No frontmatter, add it
            frontmatter = updates
            body = content
        else:
            fm_text = match.group(1)
            body = match.group(2)
            
            # Parse existing frontmatter
            frontmatter = self._parse_frontmatter_simple(fm_text)
            
            # Update with new values
            frontmatter.update(updates)
            
            # Add updated timestamp
            frontmatter["updated"] = datetime.now().isoformat()
        
        # Generate new frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        
        new_fm = "\n".join(fm_lines)
        
        return f"{new_fm}\n\n{body.strip()}"
    
    def _extract_task_id(self, content: str) -> Optional[str]:
        """Extract task ID from content"""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            for line in fm_text.split('\n'):
                if line.startswith('task_id:'):
                    return line.split(':', 1)[1].strip()
        return None


class UpdateTaskStatusSkill(BaseSkill):
    """
    Skill: update_task_status
    
    Updates task status and moves files between folders.
    
    Input:
        - task_id: str - Task ID to update
        - new_status: str - New status value
        - target_folder: str - Target folder (optional, auto-determined)
        - additional_updates: dict - Additional frontmatter updates
    
    Output:
        - success: bool
        - data: dict containing:
            - task_id: str
            - old_status: str
            - new_status: str
            - file_moved: bool
            - new_file_path: str
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="update_task_status",
            description="Update task status and move files between folders",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.status_folder_map = {
            "pending": "Needs_Action",
            "in_progress": "Plans",
            "approved": "Approved",
            "rejected": "Rejected",
            "completed": "Done",
            "waiting": "Pending_Approval"
        }
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to update"
                },
                "new_status": {
                    "type": "string",
                    "description": "New status value"
                },
                "target_folder": {
                    "type": "string",
                    "description": "Target folder (optional)"
                },
                "additional_updates": {
                    "type": "object",
                    "description": "Additional frontmatter updates"
                }
            },
            "required": ["task_id", "new_status"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "old_status": {"type": "string"},
                        "new_status": {"type": "string"},
                        "file_moved": {"type": "boolean"},
                        "new_file_path": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the update task status skill"""
        try:
            task_id = kwargs.get("task_id")
            new_status = kwargs.get("new_status")
            target_folder = kwargs.get("target_folder")
            additional_updates = kwargs.get("additional_updates", {})
            
            if not task_id or not new_status:
                raise SkillExecutionError("task_id and new_status are required")
            
            if not self.vault_path:
                raise SkillExecutionError("vault_path not configured")
            
            # Find task file
            task_file, current_folder = self._find_task_file(task_id)
            
            if not task_file:
                raise SkillExecutionError(f"Task not found: {task_id}")
            
            # Read current content
            content = task_file.read_text(encoding='utf-8')
            
            # Extract current status
            old_status = self._extract_status(content)
            
            # Update content
            updates = {"status": new_status}
            updates.update(additional_updates)
            
            if new_status == "completed":
                updates["completed_at"] = datetime.now().isoformat()
            
            updated_content = self._update_frontmatter(content, updates)
            
            # Determine target folder
            if not target_folder:
                target_folder = self.status_folder_map.get(new_status, current_folder)
            
            # Move file if needed
            file_moved = False
            new_file_path = str(task_file)
            
            if target_folder != current_folder:
                new_path = self._move_task_file(task_file, target_folder)
                new_file_path = str(new_path)
                file_moved = True
            
            # Write updated content
            if not file_moved:
                task_file.write_text(updated_content, encoding='utf-8')
            else:
                # Write to new location
                new_path = Path(new_file_path)
                new_path.write_text(updated_content, encoding='utf-8')
            
            result = {
                "task_id": task_id,
                "old_status": old_status,
                "new_status": new_status,
                "file_moved": file_moved,
                "new_file_path": new_file_path,
                "updated_at": datetime.now().isoformat()
            }
            
            self._write_log({
                "action": "update_task_status",
                "task_id": task_id,
                "old_status": old_status,
                "new_status": new_status,
                "file_moved": file_moved,
                "success": True
            })
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error updating task status: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _find_task_file(self, task_id: str) -> Tuple[Optional[Path], Optional[str]]:
        """Find task file by ID"""
        for folder in self.status_folder_map.values():
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                continue
            
            for file in folder_path.glob(f"*{task_id}*.md"):
                return file, folder
        
        # Also search without task_id pattern
        for folder in self.status_folder_map.values():
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                continue
            
            for file in folder_path.glob("*.md"):
                content = file.read_text(encoding='utf-8')
                if task_id in content:
                    return file, folder
        
        return None, None
    
    def _extract_status(self, content: str) -> str:
        """Extract status from frontmatter"""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            for line in fm_text.split('\n'):
                if line.startswith('status:'):
                    return line.split(':', 1)[1].strip()
        return "unknown"
    
    def _update_frontmatter(self, content: str, updates: Dict) -> str:
        """Update frontmatter in content"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        
        if not match:
            return content
        
        fm_text = match.group(1)
        body = match.group(2)
        
        # Parse existing frontmatter
        frontmatter = self._parse_frontmatter_simple(fm_text)
        
        # Apply updates
        frontmatter.update(updates)
        
        # Generate new frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}:")
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        
        new_fm = "\n".join(fm_lines)
        
        return f"{new_fm}\n\n{body.strip()}"
    
    def _parse_frontmatter_simple(self, fm_text: str) -> Dict:
        """Simple frontmatter parser"""
        frontmatter = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                
                frontmatter[key] = value
        
        return frontmatter
    
    def _move_task_file(self, file: Path, target_folder: str) -> Path:
        """Move task file to target folder"""
        target_path = self.vault_path / target_folder / file.name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        file.rename(target_path)
        return target_path


class LogAgentActivitySkill(BaseSkill):
    """
    Skill: log_agent_activity
    
    Logs agent activities, decisions, and actions for audit trails.
    
    Input:
        - activity_type: str - Type of activity
        - activity_data: dict - Activity details
        - agent_id: str - Agent identifier
        - session_id: str - Session identifier
    
    Output:
        - success: bool
        - data: dict containing:
            - log_id: str
            - log_file: str
            - timestamp: str
        - error: str (if failed)
    """
    
    def __init__(self, vault_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="log_agent_activity",
            description="Log agent activities for audit trails",
            version="1.0.0",
            vault_path=vault_path,
            config=config or {}
        )
        
        self.log_retention_days = self.config.get("log_retention_days", 90)
        self.log_level = self.config.get("log_level", "INFO")
    
    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "activity_type": {
                    "type": "string",
                    "description": "Type of activity"
                },
                "activity_data": {
                    "type": "object",
                    "description": "Activity details"
                },
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session identifier"
                },
                "log_level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
                    "description": "Log level"
                }
            },
            "required": ["activity_type", "activity_data"]
        }
    
    def _get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "log_id": {"type": "string"},
                        "log_file": {"type": "string"},
                        "timestamp": {"type": "string"}
                    }
                },
                "error": {"type": "string"}
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the log agent activity skill"""
        try:
            activity_type = kwargs.get("activity_type")
            activity_data = kwargs.get("activity_data", {})
            agent_id = kwargs.get("agent_id", "ai_employee")
            session_id = kwargs.get("session_id", datetime.now().strftime("%Y%m%d"))
            log_level = kwargs.get("log_level", self.log_level)
            
            if not self.vault_path:
                raise SkillExecutionError("vault_path not configured")
            
            # Generate log entry
            timestamp = datetime.now()
            log_entry = {
                "log_id": f"LOG_{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
                "timestamp": timestamp.isoformat(),
                "date": timestamp.strftime("%Y-%m-%d"),
                "activity_type": activity_type,
                "activity_data": activity_data,
                "agent_id": agent_id,
                "session_id": session_id,
                "log_level": log_level
            }
            
            # Get log file path
            logs_dir = self.vault_path / "Logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = logs_dir / f"{timestamp.strftime('%Y-%m-%d')}.json"
            
            # Load existing logs
            logs = []
            if log_file.exists():
                try:
                    logs = json.loads(log_file.read_text(encoding='utf-8'))
                except json.JSONDecodeError:
                    logs = []
            
            # Add new entry
            logs.append(log_entry)
            
            # Write back
            log_file.write_text(json.dumps(logs, indent=2, default=str), encoding='utf-8')
            
            # Also update daily summary
            self._update_daily_summary(timestamp, activity_type, log_level)
            
            result = {
                "log_id": log_entry["log_id"],
                "log_file": str(log_file),
                "timestamp": log_entry["timestamp"]
            }
            
            return {"success": True, "data": result, "error": None}
            
        except Exception as e:
            error_msg = f"Error logging activity: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "data": None, "error": error_msg}
    
    def _update_daily_summary(self, timestamp: datetime, activity_type: str, log_level: str) -> None:
        """Update daily activity summary"""
        logs_dir = self.vault_path / "Logs"
        summary_file = logs_dir / f"Daily_Summary_{timestamp.strftime('%Y-%m-%d')}.md"
        
        # Load or create summary
        if summary_file.exists():
            content = summary_file.read_text(encoding='utf-8')
        else:
            content = f"""---
date: {timestamp.strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
---

# Daily Activity Summary - {timestamp.strftime('%Y-%m-%d')}

## Activity Counts
"""
        
        # Parse and update counts
        # This is simplified - in production would parse and update properly
        summary_file.write_text(content, encoding='utf-8')
    
    def get_logs(
        self,
        start_date: str,
        end_date: str,
        activity_type: Optional[str] = None,
        log_level: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve logs for a date range"""
        if not self.vault_path:
            return []
        
        logs_dir = self.vault_path / "Logs"
        all_logs = []
        
        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Read all log files in range
        current = start
        while current <= end:
            log_file = logs_dir / f"{current.strftime('%Y-%m-%d')}.json"
            if log_file.exists():
                try:
                    day_logs = json.loads(log_file.read_text(encoding='utf-8'))
                    
                    # Filter
                    for log in day_logs:
                        match = True
                        if activity_type and log.get("activity_type") != activity_type:
                            match = False
                        if log_level and log.get("log_level") != log_level:
                            match = False
                        
                        if match:
                            all_logs.append(log)
                
                except (json.JSONDecodeError, Exception) as e:
                    self.logger.warning(f"Error reading {log_file}: {e}")
            
            current += timedelta(days=1)
        
        return all_logs
    
    def generate_report(self, start_date: str, end_date: str) -> str:
        """Generate activity report for date range"""
        logs = self.get_logs(start_date, end_date)
        
        # Aggregate statistics
        stats = {
            "total_activities": len(logs),
            "by_type": {},
            "by_level": {},
            "by_agent": {}
        }
        
        for log in logs:
            # Count by type
            activity_type = log.get("activity_type", "unknown")
            stats["by_type"][activity_type] = stats["by_type"].get(activity_type, 0) + 1
            
            # Count by level
            level = log.get("log_level", "INFO")
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Count by agent
            agent = log.get("agent_id", "unknown")
            stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1
        
        # Generate report
        report = f"""# Activity Report: {start_date} to {end_date}

## Summary
- Total Activities: {stats['total_activities']}

## By Activity Type
"""
        for activity_type, count in stats["by_type"].items():
            report += f"- {activity_type}: {count}\n"
        
        report += "\n## By Log Level\n"
        for level, count in stats["by_level"].items():
            report += f"- {level}: {count}\n"
        
        report += "\n## By Agent\n"
        for agent, count in stats["by_agent"].items():
            report += f"- {agent}: {count}\n"
        
        return report


# Import uuid for LogAgentActivitySkill
import uuid
from datetime import timedelta

# Export all vault skills
__all__ = [
    "ReadVaultTasksSkill",
    "WriteVaultTasksSkill",
    "UpdateTaskStatusSkill",
    "LogAgentActivitySkill"
]
