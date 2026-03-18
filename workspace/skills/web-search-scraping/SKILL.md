# Web Search & Scraping Skill

## Description
Enables autonomous web searching and content scraping using multiple search engines (DuckDuckGo, SearxNG) and web scraping capabilities for StackOverflow, documentation, and technical resources.

## Capabilities
- **Multi-engine search**: DuckDuckGo, SearxNG, Brave Search fallback
- **Technical content extraction**: StackOverflow, GitHub docs, official documentation
- **Smart query routing**: Automatically selects best search engine based on query type
- **Content summarization**: Extracts and summarizes relevant information from search results
- **Error troubleshooting**: Specialized for technical error messages and debugging

## Usage Patterns
- When encountering unknown errors: search StackOverflow + official docs
- For technical documentation: search official sources first
- For general knowledge: use DuckDuckGo or SearxNG
- For Chinese content: prioritize Chinese search engines when available

## Dependencies
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing  
- `lxml` - XML/HTML parsing
- `duckduckgo-search` - DuckDuckGo API
- `searxng` - SearxNG client (optional)

## Security
- Respects robots.txt
- Rate limiting to avoid overwhelming servers
- No JavaScript execution (static content only)
- Content filtering for safety