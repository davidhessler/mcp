# AWS Security Reference Architecture MCP Server

The AWS SRA is a holistic set of guidelines for deploying the full complement of AWS security services in a multi-account environment. Use it to help design, implement, and manage AWS security services so that they align with AWS recommended practices. he recommendations are built around architecture that includes AWS security services—how they help achieve security objectives, where they can be best deployed and managed in your AWS accounts, and how they interact with other security services.

The SRA consists of content in both prescriptive guidance, CloudFormation and Terraform code examples, and assessment tooling to determine how compliant an AWS environment.

The AWS SRA MCP Server enables


## Overview

The AWS Security Reference Architecture MCP Server is a specialized MCP server that focuses on providing access to AWS security documentation, with an emphasis on the AWS Security Reference Architecture (SRA). It helps AI assistants provide accurate and up-to-date information about AWS security services, compliance frameworks, and security best practices.

## What is AWS Security Reference Architecture?

The AWS Security Reference Architecture (SRA) is a holistic set of guidelines for deploying the full complement of AWS security services in a multi-account environment. It provides prescriptive guidance on how to architect a security foundation across AWS accounts and AWS Organizations.

## Features

- **Security-focused documentation search**: Search AWS documentation with an emphasis on security and compliance content
- **Documentation reading**: Read and parse AWS security documentation pages
- **Related content recommendations**: Get recommendations for related security documentation

## Installation

```bash
pip install awslabs.aws-sra-mcp-server
```

## Usage

### Starting the server

```bash
aws-sra-mcp-server
```

### Using with MCP clients

Configure your MCP client to connect to the server at the default address `http://localhost:8080`.

## Tools

The server provides the following tools:

### search_documentation

Search AWS Security Reference Architecture documentation using the official AWS Documentation Search API.

```python
search_documentation(search_phrase: str, limit: int = 10) -> List[SearchResult]
```

### read_documentation

Fetch and convert an AWS Security Reference Architecture documentation page to markdown format.

```python
read_documentation(url: str, max_length: int = 5000, start_index: int = 0) -> str
```

### recommend

Get security content recommendations for an AWS Security Reference Architecture documentation page.

```python
recommend(url: str) -> List[RecommendationResult]
```

## License

This project is licensed under the Apache-2.0 License.
