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
from awslabs.aws_sra_mcp_server.server import recommend


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_recommend_filters_security_results(mock_client, mock_context):
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
    results = await recommend(
        mock_context, "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    )

    # Verify that security-related results are prioritized
    security_titles = ["AWS Security Hub", "Amazon Macie", "Amazon Inspector"]
    non_security_titles = ["Amazon S3", "Amazon EC2"]

    # Check that all security-related results are included
    for title in security_titles:
        assert any(result.title == title for result in results)

    # Check that non-security results are only included if needed to meet minimum count
    included_non_security = [
        title for title in non_security_titles if any(result.title == title for result in results)
    ]
    assert len(included_non_security) <= max(0, 5 - len(security_titles))


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.aws_documentation.httpx.AsyncClient")
async def test_recommend_error_handling(mock_client, mock_context):
    """Test error handling in the recommend function."""
    # Setup mock to raise an exception
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.side_effect = Exception("HTTP error")
    mock_client.return_value = mock_client_instance

    # Call the function with try/except to handle the exception
    try:
        results = await recommend(
            mock_context, "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
        )

        # Verify the results - should return empty list when error occurs
        assert len(results) == 0
    except Exception as e:
        pytest.fail(f"recommend should handle exceptions, but raised: {e}")
