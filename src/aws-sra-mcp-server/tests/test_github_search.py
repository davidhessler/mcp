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

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from awslabs.aws_sra_mcp_server.github import SRA_REPOSITORIES, search_github


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.github.httpx.AsyncClient")
async def test_search_github(mock_client, mock_context):
    """Test the search_github function."""
    # Setup mock responses for code search
    mock_code_response = MagicMock()
    mock_code_response.status_code = 200
    mock_code_response.json.return_value = {
        "items": [
            {
                "name": "example.py",
                "path": "src/example.py",
                "html_url": "https://github.com/awslabs/sra-verify/blob/main/src/example.py",
            }
        ]
    }

    # Setup mock responses for issues search
    mock_issues_response = MagicMock()
    mock_issues_response.status_code = 200
    mock_issues_response.json.return_value = {
        "items": [
            {
                "title": "Security issue example",
                "html_url": "https://github.com/awslabs/sra-verify/issues/1",
                "body": "This is an example security issue",
            }
        ]
    }

    # Setup mock client to return different responses for different URLs
    mock_client_instance = AsyncMock()

    def mock_get(url, **kwargs):
        if "search/code" in url:
            return mock_code_response
        elif "search/issues" in url:
            return mock_issues_response
        return MagicMock()

    mock_client_instance.__aenter__.return_value.get.side_effect = mock_get
    mock_client.return_value = mock_client_instance

    # Call the function
    results = await search_github(mock_context, "security", limit=10)

    # Verify the results
    assert len(results) >= 1

    # Check that we have both code and issue results
    code_results = [r for r in results if "[Code]" in r.title]
    issue_results = [r for r in results if "[Issue]" in r.title]

    assert len(code_results) >= 1
    assert len(issue_results) >= 1

    # Verify code result
    code_result = code_results[0]
    assert "example.py" in code_result.title
    assert "sra-verify" in code_result.title
    assert code_result.url == "https://github.com/awslabs/sra-verify/blob/main/src/example.py"

    # Verify issue result
    issue_result = issue_results[0]
    assert "Security issue example" in issue_result.title
    assert "sra-verify" in issue_result.title
    assert issue_result.url == "https://github.com/awslabs/sra-verify/issues/1"


@pytest.mark.asyncio
async def test_sra_repositories_constant():
    """Test that the SRA_REPOSITORIES constant contains the expected repositories."""
    assert "awslabs/sra-verify" in SRA_REPOSITORIES
    assert "aws-samples/aws-security-reference-architecture-examples" in SRA_REPOSITORIES


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.github.httpx.AsyncClient")
async def test_search_github_with_token(mock_client, mock_context):
    """Test the search_github function with GitHub token."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function with a token
    await search_github(mock_context, "security", limit=10, github_token="test-token")

    # Verify that the Authorization header was set
    calls = mock_client_instance.__aenter__.return_value.get.call_args_list
    for call in calls:
        headers = call[1].get("headers", {})
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.github.httpx.AsyncClient")
async def test_search_github_error_handling(mock_client, mock_context):
    """Test error handling in search_github function."""
    # Setup mock client to raise an exception
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.side_effect = Exception("API Error")
    mock_client.return_value = mock_client_instance

    # Call the function - it should handle errors gracefully
    results = await search_github(mock_context, "security", limit=10)

    # Should return empty list when errors occur
    assert isinstance(results, list)
    assert len(results) == 0
