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
