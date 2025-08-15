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

from awslabs.aws_sra_mcp_server.server_utils import read_documentation_html


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.server_utils.httpx.AsyncClient")
@patch("awslabs.aws_sra_mcp_server.server_utils.is_html_content")
@patch("awslabs.aws_sra_mcp_server.server_utils.extract_content_from_html")
@patch("awslabs.aws_sra_mcp_server.server_utils.format_result")
async def test_read_documentation_impl_success(
    mock_format, mock_extract, mock_is_html, mock_client, mock_context
):
    """Test successful execution of read_documentation_impl."""
    # Setup mocks
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test content</body></html>"
    mock_response.headers = {"content-type": "text/html"}

    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    mock_is_html.return_value = True
    mock_extract.return_value = "Extracted content"
    mock_format.return_value = "Formatted content"

    # Call the function
    url = "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    max_length = 1000
    start_index = 0
    session_uuid = "test-session-uuid"

    result = await read_documentation_html(mock_context, url, max_length, start_index, session_uuid)

    # Verify the results
    assert result == "Formatted content"
    # The content-type is not passed to is_html_content in the current implementation
    mock_is_html.assert_called_once_with("<html><body>Test content</body></html>", "")
    mock_extract.assert_called_once_with("<html><body>Test content</body></html>")
    mock_format.assert_called_once_with(url, "Extracted content", start_index, max_length)


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.server_utils.httpx.AsyncClient")
async def test_read_documentation_impl_http_error(mock_client, mock_context):
    """Test handling of HTTP errors in read_documentation_impl."""
    # Setup mock to raise an exception
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.side_effect = Exception("HTTP error")
    mock_client.return_value = mock_client_instance

    # Call the function
    url = "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    max_length = 1000
    start_index = 0
    session_uuid = "test-session-uuid"

    # Use try/except to handle the exception
    try:
        result = await read_documentation_html(
            mock_context, url, max_length, start_index, session_uuid
        )
        # Verify the results
        assert "Failed to fetch" in result
        assert "HTTP error" in result
        assert len(mock_context.errors) == 1
        assert "Failed to fetch" in mock_context.errors[0]
    except Exception as e:
        pytest.fail(f"read_documentation_impl should handle exceptions, but raised: {e}")


@pytest.mark.asyncio
@patch("awslabs.aws_sra_mcp_server.server_utils.httpx.AsyncClient")
async def test_read_documentation_impl_status_error(mock_client, mock_context):
    """Test handling of HTTP status errors in read_documentation_impl."""
    # Setup mock to return an error status
    mock_response = MagicMock()
    mock_response.status_code = 404

    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    # Call the function
    url = "https://docs.aws.amazon.com/security-reference-architecture/welcome.html"
    max_length = 1000
    start_index = 0
    session_uuid = "test-session-uuid"

    result = await read_documentation_html(mock_context, url, max_length, start_index, session_uuid)

    # Verify the results
    assert "Failed to fetch" in result
    assert "status code 404" in result
    assert len(mock_context.errors) == 1
    assert "Failed to fetch" in mock_context.errors[0]
