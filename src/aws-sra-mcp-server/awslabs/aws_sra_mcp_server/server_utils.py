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
import httpx
from awslabs.aws_sra_mcp_server import DEFAULT_USER_AGENT
from awslabs.aws_sra_mcp_server.util import (
    extract_content_from_html,
    format_documentation_result,
    is_html_content,
)
from importlib.metadata import version
from loguru import logger
from mcp.server.fastmcp import Context
from typing import Callable, Optional


try:
    __version__ = version("awslabs.aws-sra-mcp-server")
except Exception:
    from . import __version__


async def _fetch_url(ctx: Context, url_str: str, session_uuid: str) -> tuple[str, Optional[str]]:
    """Fetch URL content and return (content, error_msg)."""
    logger.debug(f"Fetching documentation from {url_str}")
    
    url_with_session = f"{url_str}?session={session_uuid}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url_with_session,
                follow_redirects=True,
                headers={
                    "User-Agent": DEFAULT_USER_AGENT,
                    "X-MCP-Session-Id": session_uuid,
                },
                timeout=30,
            )
        except Exception as e:
            error_msg = f"Failed to fetch {url_str}: {str(e)}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return "", error_msg

        if response.status_code >= 400:
            error_msg = f"Failed to fetch {url_str} - status code {response.status_code}"
            logger.error(error_msg)
            await ctx.error(error_msg)
            return "", error_msg

        return response.text, None


def _log_truncation(content: str, start_index: int, max_length: int) -> None:
    """Log if content was truncated."""
    if len(content) > start_index + max_length:
        logger.debug(
            f"Content truncated at {start_index + max_length} of {len(content)} characters"
        )


async def _read_documentation_base(
    ctx: Context,
    url_str: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
    content_processor: Callable[[str, str], str],
) -> str:
    """Base function for reading documentation with custom content processing."""
    raw_content, error_msg = await _fetch_url(ctx, url_str, session_uuid)
    if error_msg:
        return error_msg

    content = content_processor(raw_content, "")
    result = format_documentation_result(url_str, content, start_index, max_length)
    _log_truncation(content, start_index, max_length)
    
    return result


def _process_html_content(raw_content: str, content_type: str) -> str:
    """Process HTML content by extracting text if it's HTML."""
    if is_html_content(raw_content, content_type):
        return extract_content_from_html(raw_content)
    return raw_content


def _process_markdown_content(raw_content: str, content_type: str) -> str:
    """Process markdown content (no processing needed)."""
    return raw_content


def _process_code_content(raw_content: str, content_type: str) -> str:
    """Process code content by wrapping in code blocks."""
    return f'```\n{raw_content}\n```'


async def read_documentation_html(
    ctx: Context,
    url_str: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
) -> str:
    """The implementation of the read_documentation tool for HTML content."""
    return await _read_documentation_base(
        ctx, url_str, max_length, start_index, session_uuid, _process_html_content
    )


async def read_documentation_markdown(
    ctx: Context,
    url_str: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
) -> str:
    """The implementation of the read_documentation tool for markdown content."""
    return await _read_documentation_base(
        ctx, url_str, max_length, start_index, session_uuid, _process_markdown_content
    )


async def read_code(
    ctx: Context,
    url_str: str,
    max_length: int,
    start_index: int,
    session_uuid: str,
) -> str:
    """The implementation of the read_documentation tool for code content."""
    return await _read_documentation_base(
        ctx, url_str, max_length, start_index, session_uuid, _process_code_content
    )