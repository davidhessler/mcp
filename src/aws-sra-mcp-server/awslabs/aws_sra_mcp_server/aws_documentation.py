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
"""AWS Documentation search functionality for AWS Security Reference Architecture MCP Server."""
from http.client import responses

import httpx
import re
from loguru import logger
from typing import List, Dict, Any
from awslabs.aws_sra_mcp_server.models import SearchResult, RecommendationResult
from awslabs.aws_sra_mcp_server import DEFAULT_USER_AGENT
from awslabs.aws_sra_mcp_server import SECURITY_KEYWORDS
from uuid import uuid4

# API URLs
SEARCH_API_URL = "https://proxy.search.docs.aws.amazon.com/search"
RECOMMENDATIONS_API_URL = "https://contentrecs-api.docs.aws.amazon.com/v1/recommendations"
SESSION_UUID = str(uuid4())

def parse_recommendation_results(data: Dict[str, Any]) -> List[RecommendationResult]:
    """Parse recommendation API response into RecommendationResult objects.

    Args:
        data: Raw API response data

    Returns:
        List of recommendation results
    """
    results = []

    # Process highly rated recommendations
    if 'highlyRated' in data and 'items' in data['highlyRated']:
        for item in data['highlyRated']['items']:
            context = item.get('abstract') if 'abstract' in item else None

            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    # Process journey recommendations (organized by intent)
    if 'journey' in data and 'items' in data['journey']:
        for intent_group in data['journey']['items']:
            intent = intent_group.get('intent', '')
            if 'urls' in intent_group:
                for url_item in intent_group['urls']:
                    # Add intent as part of the context
                    context = f'Intent: {intent}' if intent else None

                    results.append(
                        RecommendationResult(
                            url=url_item.get('url', ''),
                            title=url_item.get('assetTitle', ''),
                            context=context,
                        )
                    )

    # Process new content recommendations
    if 'new' in data and 'items' in data['new']:
        for item in data['new']['items']:
            # Add "New content" label to context
            date_created = item.get('dateCreated', '')
            context = f'New content added on {date_created}' if date_created else 'New content'

            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    # Process similar recommendations
    if 'similar' in data and 'items' in data['similar']:
        for item in data['similar']['items']:
            context = item.get('abstract') if 'abstract' in item else 'Similar content'

            results.append(
                RecommendationResult(
                    url=item.get('url', ''), title=item.get('assetTitle', ''), context=context
                )
            )

    return results

def parse_search_results(data: Dict[str, Any], limit: int = 10) -> List[SearchResult]:
    """
    Parse search API response into SearchResult objects.

    Args:
        data: Raw API response data
    """
    results = []
    if 'suggestions' in data:
        for i, suggestion in enumerate(data['suggestions'][:limit]):
            if 'textExcerptSuggestion' in suggestion:
                text_suggestion = suggestion['textExcerptSuggestion']
                context = text_suggestion['context']

                # Add context if available
                if 'summary' in text_suggestion:
                    context = text_suggestion['summary']
                elif 'suggestionBody' in text_suggestion:
                    context = text_suggestion['suggestionBody']

                results.append(
                    SearchResult(
                        rank_order=i + 1,
                        url=text_suggestion.get('link', ''),
                        title=text_suggestion.get('title', ''),
                        context=context,
                    )
                )

    return results

async def search_sra_documentation(
        search_phrase: str,
        limit: int = 10
) -> List[SearchResult]:
    """
    Search SRA documentation
    
    Args:
        search_phrase: Search phrase to use
        limit: Maximum number of results to return
        
    Returns:
        List of search results from AWS documentation
    """
    logger.debug(f"Searching AWS documentation for: {search_phrase}")

    request_body = {
        'textQuery': {
            'input': search_phrase,
        },
        'contextAttributes': [{'key':'aws-docs-search-guide', 'value': 'AWS Security Reference Architecture'}], # Limits to SRA Docs only
        'acceptSuggestionBody': 'RawText',
        'locales': ['en_us'],
    }

    search_url_with_session = f'{SEARCH_API_URL}?session={SESSION_UUID}'

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': DEFAULT_USER_AGENT,
        'X-MCP-Session-Id': SESSION_UUID,
    }

    # Create a client for AWS documentation search
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(search_url_with_session, json=request_body, headers=headers)
            response.raise_for_status()

            data = response.json()
            return parse_search_results(data, limit)

        except Exception as e:
            logger.error(f"Error searching AWS documentation: {e}")
            return []

async def get_recommendations(url: str) -> List[RecommendationResult]:
    """
    Get content recommendations for an AWS documentation page.
    
    Args:
        url: URL of the AWS documentation page
        
    Returns:
        List of recommended pages
    """
    logger.debug(f"Getting recommendations for: {url}")
    recommendation_url = f'{RECOMMENDATIONS_API_URL}?path={url}&session={SESSION_UUID}'

    # Create a client for AWS documentation recommendations
    async with httpx.AsyncClient() as client:
        params = {
            "url": url,
        }
        
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
        }
        
        try:
            response = await client.get(recommendation_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return parse_recommendation_results(data)
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []