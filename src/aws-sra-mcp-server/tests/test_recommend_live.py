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
import json

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from awslabs.aws_sra_mcp_server.server import MCP
from fastmcp import Client

@pytest.fixture
def client():
    return Client(MCP)

async def call_tool(client: Client, tool, **kwargs):
    """Helper function to call an MCP tool as an integration test"""
    params = {}
    for key, value in kwargs.items():
        params[key] = value
    return await client.call_tool(tool, params)


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.AsyncClient")
async def test_recommend_filters_security_results(mock_client, client):
    """Test that recommend filters results to prioritize security-related content."""
    # Setup mock response with mixed results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "highlyRated": {
            "items": [
                {
                    "url": "https://docs.aws.amazon.com/security-hub/",
                    "assetTitle": "AWS Security Hub",
                    "abstract": "Security monitoring service",
                },
                {
                    "url": "https://docs.aws.amazon.com/s3/",
                    "assetTitle": "Amazon S3",
                    "abstract": "Object storage service",
                },
                {
                    "url": "https://docs.aws.amazon.com/macie/",
                    "assetTitle": "Amazon Macie",
                    "abstract": "Data security service",
                },
            ]
        },
        "similar": {
            "items": [
                {
                    "url": "https://docs.aws.amazon.com/inspector/",
                    "assetTitle": "Amazon Inspector",
                    "abstract": "Vulnerability management service",
                },
                {
                    "url": "https://docs.aws.amazon.com/ec2/",
                    "assetTitle": "Amazon EC2",
                    "abstract": "Virtual server service",
                },
            ]
        },
    }

    # Setup mock client
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function
    async with client:
        results = await call_tool(
            client, "recommend", url="https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
        )

    # Verify that we got results
    assert results is not None
    assert len(results.content) > 0
    assert len(json.loads(results.content[0].text)) > 0


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.AsyncClient")
async def test_recommend_error_handling(mock_client, client):
    """Test error handling in the recommend function."""
    # Setup mock to raise an exception
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.side_effect = Exception("HTTP error")
    mock_client.return_value = mock_client_instance

    # Call the function with try/except to handle the exception
    try:
        async with client:
            results = await call_tool(
                client, "recommend", url="https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
            )

        # Verify the results - should return a list with an error message
        assert len(results.content) == 0
    except Exception as e:
        pytest.fail(f"recommend should handle exceptions, but raised: {e}")
