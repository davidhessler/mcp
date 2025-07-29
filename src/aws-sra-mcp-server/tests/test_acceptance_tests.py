import json
import os

import pytest
from fastmcp import Client

from awslabs.aws_sra_mcp_server.server import MCP

client = Client(MCP)


@pytest.mark.asyncio
async def test_search_security_and_compliance_best_practices_content_unauthenticated():
    async with client:
        result = await client.call_tool(
            "search_security_and_compliance_best_practices_content",
            {"search_phrase": "Security Hub"},
        )
        assert len(result.content) > 0
        expected_url = [
            "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
            "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/architecture.html",
            "https://github.com/aws-samples/aws-security-reference-architecture-examples/issues/233",
        ]
        found_urls = 0
        for c in json.loads(result.content[0].text):
            if c["url"] in expected_url:
                found_urls += 1
        assert found_urls == len(expected_url)


@pytest.mark.skipif(
    os.environ.get("GITHUB_TOKEN") is None,
    reason="Code Search requires authenticated API calls. This tests ensure code results are "
    "returned in the result. So, this test will only successed if GITHUB_TOKEN environment "
    "variable to be set with a personal access token",
)
@pytest.mark.asyncio
async def test_search_security_and_compliance_best_practices_content_authenticated():
    async with client:
        result = await client.call_tool(
            "search_security_and_compliance_best_practices_content",
            {"search_phrase": "Security Hub"},
        )
        assert len(result.content) > 0
        expected_url = [
            "https://github.com/awslabs/sra-verify/blob/af737628e43a16f755f0aa45cb15474009819f73/sraverify/sraverify/services/securityhub/checks/sra_securityhub_10.py",
            "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
            "https://github.com/aws-samples/aws-security-reference-architecture-examples/blob/3b1e1e0af9b407030283e0b5b2ff07bf78a322f1/aws_sra_examples/terraform/solutions/security_hub/README.md",
            "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/architecture.html",
        ]
        found_urls = 0
        for c in json.loads(result.content[0].text):
            if c["url"] in expected_url:
                found_urls += 1
        assert found_urls == len(expected_url)


@pytest.mark.asyncio
async def test_read_security_and_compliance_best_practices_content_prescriptive_guidance():
    """Tests search documentation"""
    async with client:
        result = await client.call_tool(
            "read_security_and_compliance_best_practices_content",
            {
                "url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
                "start_index": 0,
            },
        )
        assert len(result.content) > 0
        text_result = result.content[0].text
        assert text_result.startswith("AWS Security Reference Architecture Documentation")


@pytest.mark.asyncio
# ruff: noqa: E501
async def test_read_security_and_compliance_best_practices_content_prescriptive_guidance_no_more_content():
    """Tests search documentation"""
    async with client:
        result = await client.call_tool(
            "read_security_and_compliance_best_practices_content",
            {
                # noqa: E501
                "url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
                "start_index": 99999,
            },
        )
        assert len(result.content) > 0
        text_result = result.content[0].text
        assert "No more content available" in text_result


@pytest.mark.asyncio
async def test_read_security_and_compliance_best_practices_content_github_issues():
    """Tests search documentation"""
    async with client:
        result = await client.call_tool(
            "read_security_and_compliance_best_practices_content",
            {
                "url": "https://github.com/aws-samples/aws-security-reference-architecture-examples/issues/225",
                "start_index": 0,
            },
        )
        assert len(result.content) > 0
        text_result = result.content[0].text
        assert text_result.startswith(
            "AWS Security Reference Architecture GitHub Issue from https://github.com/aws-samples/aws-security-reference-architecture-examples/issues/225:\n\n"
        )


@pytest.mark.asyncio
async def test_read_security_and_compliance_best_practices_content_github_pr():
    """Tests search documentation"""
    async with client:
        url = "https://github.com/aws-samples/aws-security-reference-architecture-examples/pull/167"
        result = await client.call_tool(
            "read_security_and_compliance_best_practices_content", {"url": url, "start_index": 0}
        )
        assert len(result.content) > 0
        text_result = result.content[0].text
        if text_result.startswith(f"AWS Security Reference Architecture Pull Request from {url}"):
            assert True
        else:
            print(text_result)


@pytest.mark.asyncio
async def test_read_security_and_compliance_best_practices_content_github_code():
    """Tests search documentation"""
    async with client:
        result = await client.call_tool(
            "read_security_and_compliance_best_practices_content",
            {
                "url": "https://github.com/aws-samples/aws-security-reference-architecture-examples/blob/main/aws_sra_examples/modules/guardduty-org-module/templates/sra-guardduty-org-solution.yaml",
                "start_index": 0,
            },
        )
        assert len(result.content) > 0
        text_result = result.content[0].text
        assert "# SPDX-License-Identifier: MIT-0" in text_result
        assert (
            "Description: Installs the AWS SRA GuardDuty solution.  If needed, the AWS SRA common "
            "prerequisite solution is also installed.  (sra-1u3sd7f8m)" in text_result
        )


@pytest.mark.asyncio
async def test_recommendations():
    async with client:
        result = await client.call_tool(
            "recommend",
            {
                "url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html",
                "limit": 10,
            },
        )
        assert len(result.content) > 0
        json_result = json.loads(result.content[0].text)
        titles = [r["title"] for r in json_result]
        assert "Security concepts and best practices for AWS" in titles
