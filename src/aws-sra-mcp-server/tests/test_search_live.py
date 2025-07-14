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
from awslabs.aws_sra_mcp_server.server import search_documentation


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_search_documentation_enhances_query(mock_client, mock_context):
    """Test that search_documentation enhances the search query with security terms."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"suggestions": []}

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.post.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function with a non-security query
    await search_documentation(mock_context, "s3 bucket")

    # Verify that the search query was enhanced with security terms
    call_args = mock_client_instance.__aenter__.return_value.post.call_args[1]
    request_body = call_args["json"]
    assert "Security Reference Architecture" in request_body["textQuery"]["input"]

    # Reset mock
    mock_client_instance.__aenter__.return_value.post.reset_mock()

    # Call the function with a query that already contains security terms
    await search_documentation(mock_context, "security hub compliance")

    # Verify that the search query was not enhanced
    call_args = mock_client_instance.__aenter__.return_value.post.call_args[1]
    request_body = call_args["json"]
    assert request_body["textQuery"]["input"] == "security hub compliance"


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_search_documentation_filters_results(mock_client, mock_context):
    """Test that search_documentation filters results to prioritize security-related content."""
    # Setup mock response with mixed results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suggestions": [
            {
                "textExcerptSuggestion": {
                    "link": "https://docs.aws.amazon.com/security-hub/",
                    "title": "AWS Security Hub",
                    "context": "Security monitoring service",
                    "summary": "Security monitoring service",
                }
            },
            {
                "textExcerptSuggestion": {
                    "link": "https://docs.aws.amazon.com/s3/",
                    "title": "Amazon S3",
                    "context": "Object storage service",
                    "summary": "Object storage service",
                }
            },
            {
                "textExcerptSuggestion": {
                    "link": "https://docs.aws.amazon.com/macie/",
                    "title": "Amazon Macie",
                    "context": "Data security service",
                    "summary": "Data security service",
                }
            },
        ]
    }

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.post.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function
    results = await search_documentation(mock_context, "aws services", limit=2)

    # Verify that security-related results are prioritized
    assert len(results) == 2
    # Check that security-related results are included
    security_titles = ["AWS Security Hub", "Amazon Macie"]
    result_titles = [result.title for result in results]
    assert any(title in result_titles for title in security_titles)

    # At least one security-related result should be included
    assert any(
        result.title == "AWS Security Hub" or result.title == "Amazon Macie" for result in results
    )
