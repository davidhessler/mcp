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
from awslabs.aws_sra_mcp_server import __version__

SECURITY_KEYWORDS = [
    "security",
    "compliance",
    "governance",
    "audit",
    "protection",
    "sra",
    "reference architecture",
    "securityhub",
    "iam",
    "identity",
    "permission",
    "encryption",
    "kms",
    "guard",
    "firewall",
    "waf",
    "shield",
    "detective",
    "inspector",
    "macie",
]

DEFAULT_USER_AGENT = (
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like "
    f"Gecko) Chrome/91.0.4472.124 Safari/537.36 ModelContextProtocol/{__version__}"
    f" (AWS Security Reference Architecture Server)"
)

# AWS Search API URLs
SEARCH_API_URL = "https://proxy.search.docs.aws.amazon.com/search"
RECOMMENDATIONS_API_URL = "https://contentrecs-api.docs.aws.amazon.com/v1/recommendations"


# Maximum number of concurrent requests
MAX_CONCURRENT_REQUESTS = 5

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# SRA GitHub repositories to search
SRA_REPOSITORIES = [
    "awslabs/sra-verify",
    "aws-samples/aws-security-reference-architecture-examples",
]
