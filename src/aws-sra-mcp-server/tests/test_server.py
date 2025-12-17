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
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp import McpError


@pytest.mark.asyncio
async def test_get_github_token_from_env():
    """Test get_github_token when token is in environment."""
    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = MagicMock()

    with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}):
        token = await get_github_token(mock_ctx)
        assert token == "test-token"


@pytest.mark.asyncio
async def test_get_github_token_accepted_elicitation():
    """Test get_github_token when user provides token via elicitation."""
    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = AsyncMock()
    mock_ctx.elicit.return_value = AcceptedElicitation(data="user-provided-token")

    with patch.dict(os.environ, {}, clear=True):
        token = await get_github_token(mock_ctx)
        assert token == "user-provided-token"
        mock_ctx.warning.assert_called_once()


@pytest.mark.asyncio
async def test_get_github_token_declined_elicitation():
    """Test get_github_token when user declines to provide token."""
    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = AsyncMock()
    mock_ctx.elicit.return_value = DeclinedElicitation()

    with patch.dict(os.environ, {}, clear=True):
        token = await get_github_token(mock_ctx)
        assert token == ""
        mock_ctx.warning.assert_called_once()


@pytest.mark.asyncio
async def test_get_github_token_cancelled_elicitation():
    """Test get_github_token when user cancels elicitation."""
    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = AsyncMock()
    mock_ctx.elicit.return_value = CancelledElicitation()

    with patch.dict(os.environ, {}, clear=True):
        token = await get_github_token(mock_ctx)
        assert token is None
        mock_ctx.warning.assert_called_once()


@pytest.mark.asyncio
async def test_get_github_token_mcp_error():
    """Test get_github_token when McpError occurs."""
    from mcp.types import ErrorData

    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = AsyncMock()
    error_data = ErrorData(code=-1, message="Elicitation not supported")
    mock_ctx.elicit.side_effect = McpError(error_data)

    with patch.dict(os.environ, {}, clear=True):
        token = await get_github_token(mock_ctx)
        assert token is None
        mock_ctx.warning.assert_called_once()


@pytest.mark.asyncio
async def test_get_github_token_other_mcp_error():
    """Test get_github_token when other McpError occurs."""
    from mcp.types import ErrorData

    from awslabs.aws_sra_mcp_server.server import get_github_token

    mock_ctx = AsyncMock()
    error_data = ErrorData(code=-1, message="Other error")
    mock_ctx.elicit.side_effect = McpError(error_data)

    with patch.dict(os.environ, {}, clear=True):
        token = await get_github_token(mock_ctx)
        assert token is None
        mock_ctx.warning.assert_called_once()
        mock_ctx.error.assert_called_once()


# Note: The MCP tool functions are decorated and not directly testable
# They are tested through integration tests in other test files


def test_url_validation_patterns():
    """Test URL validation regex patterns used in read_content function."""
    import re

    # Define the patterns used in the server
    aws_sra_pattern = r"^https://docs\.aws\.amazon\.com/prescriptive-guidance/latest/security-reference-architecture"
    github_sra_examples_pattern = r"^https://github\.com/aws-samples/aws-security-reference-architecture-examples"
    github_sra_verify_pattern = r"^https://github\.com/awslabs/sra-verify/"

    # Test valid AWS SRA documentation URLs
    valid_aws_urls = [
        "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html",
        "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
        "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/index.html",
    ]

    # Test valid GitHub URLs
    valid_github_sra_examples_urls = [
        "https://github.com/aws-samples/aws-security-reference-architecture-examples/issues/225",
        "https://github.com/aws-samples/aws-security-reference-architecture-examples/blob/main/README.md",
        "https://github.com/aws-samples/aws-security-reference-architecture-examples/pull/167",
    ]

    valid_github_sra_verify_urls = [
        "https://github.com/awslabs/sra-verify/blob/main/README.md",
        "https://github.com/awslabs/sra-verify/issues/1",
        "https://github.com/awslabs/sra-verify/pull/5",
    ]

    # Test invalid URLs
    invalid_aws_urls = [
        "https://docs.aws.amazon.com/ec2/latest/userguide/concepts.html",  # Wrong AWS docs path
        "https://docs.aws.amazon.com/s3/latest/userguide/Welcome.html",  # Wrong AWS service
        "https://docs.aws.amazon.com/prescriptive-guidance/latest/other-guide/welcome.html",  # Wrong guide
    ]

    invalid_github_urls = [
        "https://github.com/aws/aws-cli/blob/main/README.rst",  # Wrong GitHub repo
        "https://github.com/other-org/other-repo/blob/main/file.py",  # Wrong GitHub org/repo
        "https://github.com/aws-samples/other-repo/blob/main/file.py",  # Wrong repo name
        "https://github.com/awslabs/other-repo/blob/main/file.py",  # Wrong repo name
    ]

    invalid_domain_urls = [
        "https://example.com/some-page.html",  # Wrong domain
        "http://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html",  # HTTP instead of HTTPS
    ]

    # Test valid AWS URLs
    for url in valid_aws_urls:
        assert re.match(aws_sra_pattern, url), f"Valid AWS URL {url} should match pattern"

    # Test valid GitHub SRA examples URLs
    for url in valid_github_sra_examples_urls:
        assert re.match(github_sra_examples_pattern, url), f"Valid GitHub SRA examples URL {url} should match pattern"

    # Test valid GitHub SRA verify URLs
    for url in valid_github_sra_verify_urls:
        assert re.match(github_sra_verify_pattern, url), f"Valid GitHub SRA verify URL {url} should match pattern"

    # Test invalid AWS URLs
    for url in invalid_aws_urls:
        assert not re.match(aws_sra_pattern, url), f"Invalid AWS URL {url} should not match pattern"

    # Test invalid GitHub URLs
    for url in invalid_github_urls:
        assert not re.match(github_sra_examples_pattern, url), f"Invalid GitHub URL {url} should not match SRA examples pattern"
        assert not re.match(github_sra_verify_pattern, url), f"Invalid GitHub URL {url} should not match SRA verify pattern"

    # Test invalid domain URLs
    for url in invalid_domain_urls:
        assert not re.match(aws_sra_pattern, url), f"Invalid domain URL {url} should not match AWS pattern"
        assert not re.match(github_sra_examples_pattern, url), f"Invalid domain URL {url} should not match GitHub SRA examples pattern"
        assert not re.match(github_sra_verify_pattern, url), f"Invalid domain URL {url} should not match GitHub SRA verify pattern"


def test_main():
    """Test main function."""
    from awslabs.aws_sra_mcp_server.server import MCP

    with patch.object(MCP, "run") as mock_run:
        from awslabs.aws_sra_mcp_server.server import main

        main()
        mock_run.assert_called_once()
