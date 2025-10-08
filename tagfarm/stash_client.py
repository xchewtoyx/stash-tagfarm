"""StashApp GraphQL client for fetching data."""

import httpx
from typing import Dict, List, Optional, Any
from pathlib import Path


class StashClient:
    """Client for interacting with StashApp GraphQL API."""
    
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["ApiKey"] = api_key
    
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query against StashApp."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        with httpx.Client() as client:
            response = client.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data.get("data", {})
    
    def get_favourite_tags(self) -> List[Dict[str, Any]]:
        """Get all favourite tags from StashApp."""
        query = """
        query FindTags {
            findTags(
                tag_filter: { is_missing: false }
                filter: { per_page: -1 }
            ) {
                tags {
                    id
                    name
                    favorite
                }
            }
        }
        """
        
        result = self._execute_query(query)
        tags = result.get("findTags", {}).get("tags", [])
        return [tag for tag in tags if tag.get("favorite")]
    
    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tag by name."""
        query = """
        query FindTags($name: String!) {
            findTags(
                tag_filter: { name: { value: $name, modifier: EQUALS } }
                filter: { per_page: 1 }
            ) {
                tags {
                    id
                    name
                }
            }
        }
        """
        
        result = self._execute_query(query, {"name": name})
        tags = result.get("findTags", {}).get("tags", [])
        return tags[0] if tags else None
    
    def get_scenes_by_tag(self, tag_id: str) -> List[Dict[str, Any]]:
        """Get all scenes that have a specific tag."""
        query = """
        query FindScenes($tag_id: ID!) {
            findScenes(
                scene_filter: { tags: { value: [$tag_id], modifier: INCLUDES } }
                filter: { per_page: -1 }
            ) {
                scenes {
                    id
                    title
                    files {
                        path
                        basename
                    }
                }
            }
        }
        """
        
        result = self._execute_query(query, {"tag_id": tag_id})
        return result.get("findScenes", {}).get("scenes", [])
    
    def get_favourite_performers(self) -> List[Dict[str, Any]]:
        """Get all favourite performers from StashApp."""
        query = """
        query FindPerformers {
            findPerformers(
                performer_filter: { is_missing: false }
                filter: { per_page: -1 }
            ) {
                performers {
                    id
                    name
                    favorite
                }
            }
        }
        """
        
        result = self._execute_query(query)
        performers = result.get("findPerformers", {}).get("performers", [])
        return [p for p in performers if p.get("favorite")]
    
    def get_performer_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a performer by name."""
        query = """
        query FindPerformers($name: String!) {
            findPerformers(
                performer_filter: { name: { value: $name, modifier: EQUALS } }
                filter: { per_page: 1 }
            ) {
                performers {
                    id
                    name
                }
            }
        }
        """
        
        result = self._execute_query(query, {"name": name})
        performers = result.get("findPerformers", {}).get("performers", [])
        return performers[0] if performers else None
    
    def get_scenes_by_performer(self, performer_id: str) -> List[Dict[str, Any]]:
        """Get all scenes that feature a specific performer."""
        query = """
        query FindScenes($performer_id: ID!) {
            findScenes(
                scene_filter: { 
                    performers: { value: [$performer_id], modifier: INCLUDES } 
                }
                filter: { per_page: -1 }
            ) {
                scenes {
                    id
                    title
                    files {
                        path
                        basename
                    }
                }
            }
        }
        """
        
        result = self._execute_query(query, {"performer_id": performer_id})
        return result.get("findScenes", {}).get("scenes", [])