"""LinkFarm manager for creating and managing symlinks."""

import os
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console

console = Console()


class LinkFarmManager:
    """Manages the creation and maintenance of linkfarms."""
    
    def __init__(self, farm_path: Path, use_title: bool = True, dry_run: bool = False):
        self.farm_path = Path(farm_path)
        self.use_title = use_title
        self.dry_run = dry_run
        
        if not dry_run:
            self.farm_path.mkdir(parents=True, exist_ok=True)
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as a directory/file name."""
        # Replace problematic characters with underscores
        problematic_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = name
        for char in problematic_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed"
        
        return sanitized
    
    def _get_link_name(self, scene: Dict[str, Any]) -> str:
        """Get the name to use for a symlink based on configuration."""
        if self.use_title and scene.get("title"):
            base_name = self._sanitize_name(scene["title"])
        else:
            # Use the basename from the first file
            files = scene.get("files", [])
            if files:
                base_name = Path(files[0]["basename"]).stem
            else:
                base_name = f"scene_{scene.get('id', 'unknown')}"
        
        return base_name
    
    def _get_file_extension(self, scene: Dict[str, Any]) -> str:
        """Get the file extension from the scene's first file."""
        files = scene.get("files", [])
        if files:
            return Path(files[0]["path"]).suffix
        return ""
    
    def _create_symlink(
        self, 
        source_path: Path, 
        link_path: Path, 
        category: str,
        item_name: str
    ) -> bool:
        """Create a symlink, handling conflicts and dry-run mode."""
        if not source_path.exists():
            console.print(f"[yellow]Warning: Source file does not exist: {source_path}[/yellow]")
            return False
        
        if self.dry_run:
            console.print(f"[dim]Would create: {link_path} -> {source_path}[/dim]")
            return True
        
        # Handle existing links
        if link_path.exists() or link_path.is_symlink():
            if link_path.is_symlink():
                existing_target = link_path.readlink()
                if existing_target == source_path:
                    # Link already exists and points to correct target
                    return True
                else:
                    console.print(
                        f"[yellow]Overwriting existing link: {link_path}[/yellow]"
                    )
                    link_path.unlink()
            else:
                # Regular file exists with same name
                console.print(
                    f"[red]Error: Regular file exists at link location: {link_path}[/red]"
                )
                return False
        
        try:
            link_path.symlink_to(source_path)
            return True
        except OSError as e:
            console.print(f"[red]Error creating symlink {link_path}: {e}[/red]")
            return False
    
    def create_tag_links(self, tag_name: str, scenes: List[Dict[str, Any]]) -> None:
        """Create symlinks for scenes under a tag directory."""
        tag_dir = self.farm_path / "tags" / self._sanitize_name(tag_name)
        
        if not self.dry_run:
            tag_dir.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        for scene in scenes:
            files = scene.get("files", [])
            if not files:
                continue
            
            source_path = Path(files[0]["path"])
            link_name = self._get_link_name(scene)
            extension = self._get_file_extension(scene)
            
            # Handle duplicate names by adding a counter
            base_link_path = tag_dir / f"{link_name}{extension}"
            link_path = base_link_path
            counter = 1
            
            while (not self.dry_run and link_path.exists() and 
                   link_path.readlink() != source_path):
                link_path = tag_dir / f"{link_name}_{counter}{extension}"
                counter += 1
            
            if self._create_symlink(source_path, link_path, "tag", tag_name):
                created_count += 1
        
        console.print(
            f"[green]Created {created_count} links for tag '{tag_name}'[/green]"
        )
    
    def create_performer_links(
        self, 
        performer_name: str, 
        scenes: List[Dict[str, Any]]
    ) -> None:
        """Create symlinks for scenes under a performer directory."""
        performer_dir = self.farm_path / "performers" / self._sanitize_name(performer_name)
        
        if not self.dry_run:
            performer_dir.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        for scene in scenes:
            files = scene.get("files", [])
            if not files:
                continue
            
            source_path = Path(files[0]["path"])
            link_name = self._get_link_name(scene)
            extension = self._get_file_extension(scene)
            
            # Handle duplicate names by adding a counter
            base_link_path = performer_dir / f"{link_name}{extension}"
            link_path = base_link_path
            counter = 1
            
            while (not self.dry_run and link_path.exists() and 
                   link_path.readlink() != source_path):
                link_path = performer_dir / f"{link_name}_{counter}{extension}"
                counter += 1
            
            if self._create_symlink(source_path, link_path, "performer", performer_name):
                created_count += 1
        
        console.print(
            f"[green]Created {created_count} links for performer '{performer_name}'[/green]"
        )
    
    def find_dangling_links(self) -> List[Path]:
        """Find all dangling symlinks in the linkfarm."""
        dangling_links = []
        
        if not self.farm_path.exists():
            return dangling_links
        
        for root, dirs, files in os.walk(self.farm_path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if file_path.is_symlink() and not file_path.exists():
                    dangling_links.append(file_path)
        
        return dangling_links
    
    def remove_dangling_links(self, dangling_links: List[Path]) -> None:
        """Remove the specified dangling symlinks."""
        for link_path in dangling_links:
            try:
                link_path.unlink()
                console.print(f"[green]Removed: {link_path}[/green]")
            except OSError as e:
                console.print(f"[red]Error removing {link_path}: {e}[/red]")