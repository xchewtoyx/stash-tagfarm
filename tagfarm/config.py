"""Configuration management for TagFarm."""

import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class TagConfig(BaseModel):
    """Configuration for tag processing."""
    favourite: bool = False
    names: Optional[List[str]] = None


class PerformerConfig(BaseModel):
    """Configuration for performer processing."""
    favourite: bool = False
    names: Optional[List[str]] = None


class TagFarmConfig(BaseModel):
    """Main configuration model for TagFarm."""

    # StashApp connection settings
    stash_url: str = Field(..., description="StashApp GraphQL endpoint URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    path_map: Optional[Dict[str, str]] = Field(
        None,
        description="Mapping of source paths to target paths for media files",
    )

    # LinkFarm settings
    farm_path: Path = Field(..., description="Path to the linkfarm directory")
    use_title: bool = Field(True, description="Use scene title for link names")

    # Processing settings
    tags: Optional[TagConfig] = None
    performers: Optional[PerformerConfig] = None

    @validator('farm_path')
    def validate_farm_path(cls, v):
        """Ensure farm_path is a Path object."""
        if isinstance(v, str):
            return Path(v)
        return v


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("tagfarm.yaml")
    
    def load(self) -> TagFarmConfig:
        """Load and validate configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return TagFarmConfig(**data)
    
    def save(self, config: TagFarmConfig) -> None:
        """Save configuration to file."""
        data = config.dict()
        
        # Convert Path objects to strings for YAML serialization
        if 'farm_path' in data:
            data['farm_path'] = str(data['farm_path'])
        
        with open(self.config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def create_sample_config(self, output_path: Path) -> None:
        """Create a sample configuration file."""
        sample_config = {
            "stash_url": "http://localhost:9999/graphql",
            "api_key": None,  # Optional, use if StashApp requires authentication
            "farm_path": "/path/to/linkfarm",
            "use_title": True,  # Use scene title rather than filename
            "tags": {
                "favourite": True,
                "names": [
                    "Manual Tag",
                    "Overrides",
                    "Go Here"
                ]
            },
            "performers": {
                "favourite": True,
                "names": [
                    "Manual Performer",
                    "Overrides", 
                    "Go Here"
                ]
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
