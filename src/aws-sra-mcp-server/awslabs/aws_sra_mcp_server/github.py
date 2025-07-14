# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""GitHub search functionality for AWS Security Reference Architecture MCP Server."""

import httpx
from loguru import logger
from typing import List
from awslabs.aws_sra_mcp_server.models import SearchResult

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# SRA GitHub repositories to search
SRA_REPOSITORIES = [
    'awslabs/sra-verify',
    'aws-samples/aws-security-reference-architecture-examples'
]

async def search_github(search_phrase: str, limit: int = 10, github_token: str = None) -> List[SearchResult]:
    """
    Search GitHub repositories for AWS Security Reference Architecture content.
    
    Args:
        search_phrase: Search phrase to use
        limit: Maximum number of results to return
        github_token: Optional GitHub access token for authentication
        
    Returns:
        List of search results from GitHub repositories
    """
    logger.debug(f"Searching GitHub repositories for: {search_phrase}")
    
    results = []
    
    # Create a client for GitHub API requests
    async with httpx.AsyncClient() as client:
        # Set up headers with authorization if token is provided
        headers = {}
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"
        for repo in SRA_REPOSITORIES:
            # Search code in repository
            code_search_url = f"{GITHUB_API_URL}/search/code"
            params = {
                "q": f"{search_phrase} repo:{repo}",
                "per_page": limit // 2  # Split limit between repositories
            }
            
            try:
                response = await client.get(code_search_url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                for i, item in enumerate(items):
                    result = SearchResult(
                        rank_order=i + 1,
                        url=item.get("html_url", ""),
                        title=f"[Code] {item.get('name', '')} - {repo}",
                        context=item.get("path", "")
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error searching GitHub code: {e}")
                
            # Search issues in repository
            issues_search_url = f"{GITHUB_API_URL}/search/issues"
            params = {
                "q": f"{search_phrase} repo:{repo}",
                "per_page": limit // 2  # Split limit between repositories
            }
            
            try:
                response = await client.get(issues_search_url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                for i, item in enumerate(items):
                    # Determine if it's an issue or PR
                    item_type = "[PR]" if "pull_request" in item else "[Issue]"
                    
                    result = SearchResult(
                        rank_order=i + len(results) + 1,
                        url=item.get("html_url", ""),
                        title=f"{item_type} {item.get('title', '')} - {repo}",
                        context=item.get("body", "")[:200] + "..." if item.get("body") and len(item.get("body")) > 200 else item.get("body", "")
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error searching GitHub issues: {e}")
    
    # Sort results by rank_order and limit to requested number
    results.sort(key=lambda x: x.rank_order)
    return results[:limit]