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

from awslabs.aws_sra_mcp_server.util import (
    format_result,
    is_html_content,
    parse_recommendation_results,
)


def test_is_html_content():
    """Test the is_html_content function."""
    # Test with HTML content
    assert is_html_content("<html><body>Test</body></html>", "")
    assert is_html_content("test", "text/html")

    # Test with non-HTML content
    assert not is_html_content("plain text", "text/plain")


def test_format_documentation_result():
    """Test the format_documentation_result function."""
    url = "https://docs.aws.amazon.com/security-reference-architecture/"
    content = "This is a test content for the AWS Security Reference Architecture."

    # Test with normal content
    result = format_result(url, content, 0, 100)
    assert url in result
    assert content in result
    assert "Content truncated" not in result

    # Test with truncated content
    result = format_result(url, content, 0, 10)
    assert url in result
    assert content[:10] in result
    assert "Content truncated" in result

    # Test with start index
    result = format_result(url, content, 10, 100)
    assert url in result
    assert content[10:] in result

    # Test with start index beyond content length
    result = format_result(url, content, 100, 10)
    assert url in result
    assert "No more content available" in result


def test_parse_recommendation_results():
    """Test the parse_recommendation_results function."""
    # Test with empty data
    assert parse_recommendation_results({}) == []

    # Test with highly rated recommendations
    data = {
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
    results = parse_recommendation_results(data)
    assert len(results) == 1
    assert results[0].url == "https://docs.aws.amazon.com/security-hub/"
    assert results[0].title == "AWS Security Hub"
    assert results[0].context == "Security Hub overview"

    # Test with journey recommendations
    data = {
        "journey": {
            "items": [
                {
                    "intent": "Learn about security",
                    "urls": [
                        {
                            "url": "https://docs.aws.amazon.com/security-reference-architecture/",
                            "assetTitle": "AWS Security Reference Architecture",
                        }
                    ],
                }
            ]
        }
    }
    results = parse_recommendation_results(data)
    assert len(results) == 1
    assert results[0].url == "https://docs.aws.amazon.com/security-reference-architecture/"
    assert results[0].title == "AWS Security Reference Architecture"
    assert results[0].context == "Intent: Learn about security"

    # Test with new content recommendations
    data = {
        "new": {
            "items": [
                {
                    "url": "https://docs.aws.amazon.com/security-hub/",
                    "assetTitle": "AWS Security Hub",
                    "dateCreated": "2023-06-01",
                }
            ]
        }
    }
    results = parse_recommendation_results(data)
    assert len(results) == 1
    assert results[0].url == "https://docs.aws.amazon.com/security-hub/"
    assert results[0].title == "AWS Security Hub"
    assert results[0].context == "New content added on 2023-06-01"

    # Test with similar recommendations
    data = {
        "similar": {
            "items": [
                {
                    "url": "https://docs.aws.amazon.com/security-hub/",
                    "assetTitle": "AWS Security Hub",
                    "abstract": "Similar content",
                }
            ]
        }
    }
    results = parse_recommendation_results(data)
    assert len(results) == 1
    assert results[0].url == "https://docs.aws.amazon.com/security-hub/"
    assert results[0].title == "AWS Security Hub"
    assert results[0].context == "Similar content"
