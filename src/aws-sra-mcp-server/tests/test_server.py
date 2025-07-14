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

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from awslabs.aws_sra_mcp_server.server import read_documentation, search_documentation, recommend


@pytest.mark.asyncio
async def test_read_documentation_validation(mock_context):
    """Test URL validation in read_documentation."""
    # Test with invalid domain
    with pytest.raises(ValueError, match="URL must be from the docs.aws.amazon.com domain"):
        await read_documentation(mock_context, "https://example.com/page.html")

    # Test with invalid file extension
    with pytest.raises(ValueError, match="URL must end with .html"):
        await read_documentation(mock_context, "https://docs.aws.amazon.com/page")


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.server.read_documentation_impl")
async def test_read_documentation_calls_impl(mock_read_impl, mock_context):
    """Test that read_documentation calls the implementation function."""
    mock_read_impl.return_value = "Test content"

    url = "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    max_length = 1000
    start_index = 0

    await read_documentation(mock_context, url, max_length, start_index)

    # Verify the implementation function was called with the correct arguments
    mock_read_impl.assert_called_once()
    args = mock_read_impl.call_args[0]
    assert args[0] == mock_context
    assert args[1] == url
    assert args[2] == max_length
    assert args[3] == start_index


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.github.search_github")
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_search_documentation(mock_client, mock_github_search, mock_context):
    """Test the search_documentation function."""
    # Setup mock AWS docs response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suggestions": [
            {
                "textExcerptSuggestion": {
                    "link": "https://docs.aws.amazon.com/security-reference-architecture/welcome.html",
                    "title": "AWS Security Reference Architecture",
                    "context": "A guide for security architecture",
                    "summary": "A guide for security architecture",
                }
            }
        ]
    }

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.post.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    # Setup mock GitHub search results
    from awslabs.aws_sra_mcp_server.models import SearchResult
    mock_github_search.return_value = [
        SearchResult(
            rank_order=2,
            url="https://github.com/awslabs/sra-verify/blob/main/README.md",
            title="[Code] sra-verify: README.md",
            context="Security Reference Architecture verification tool"
        )
    ]

    # Call the function
    results = await search_documentation(mock_context, "security reference architecture", 10)

    # Verify the results - should have AWS docs result
    assert len(results) >= 1
    
    # Check AWS docs result
    aws_result = next(r for r in results if "docs.aws.amazon.com" in r.url)
    assert aws_result.url == "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    assert aws_result.title == "AWS Security Reference Architecture"
    assert aws_result.context == "A guide for security architecture"


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_recommend(mock_client, mock_context):
    """Test the recommend function."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "highlyRated": {
            "items": [
                {
                    "url": "https://docs.aws.amazon.com/security-hub/",
                    "assetTitle": "AWS Security Hub",
                    "abstract": "Security Hub overview",
                }
            ]
        }
    }

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function
    results = await recommend(
        mock_context, "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    )

    # Verify the results
    assert len(results) == 1
    assert results[0].url == "https://docs.aws.amazon.com/security-hub/"
    assert results[0].title == "AWS Security Hub"
    assert results[0].context == "Security Hub overview"
