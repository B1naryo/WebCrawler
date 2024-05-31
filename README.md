# WebCrawler
Project Description:

WebCrawler is a web crawling tool designed for bug hunting and security testing purposes. This tool allows users to crawl websites within specified depth and domain constraints, extracting and analyzing links for potential vulnerabilities. Built with JavaScript and leveraging the Fetch API, SecureCrawler provides a user-friendly interface for initiating crawls and visualizing results.

Key Features:

Customizable Crawling: Specify the depth of traversal and domain scope to focus on specific areas of a website.
Rate Limiting: Implements rate limiting to prevent excessive requests and potential server overload.
Error Handling: Provides detailed error messages for failed requests and exceptions encountered during crawling.
Export Functionality: Allows users to export crawled links to a text file for further analysis or reporting.
Security Focus: Prioritizes security by sanitizing inputs, validating URLs and domains, and avoiding potentially dangerous actions.
User Interface: Offers a clean and intuitive interface for easy interaction and result visualization.
SecureCrawler is suitable for security researchers, bug bounty hunters, and developers seeking to analyze website structures, identify potential vulnerabilities, and enhance overall web security.

Feel free to adjust or expand upon this description as needed for your project!

# WebCrawler in go:
go run main.go -d http://testphp.vulnweb.com/ -depth 1 \
go run main.go -f urls.txt -depth 1

# WebCrawler in python:
python3 WebCrawler -f urls.txt -t 10 \
python3 WebCrawler -f urls.txt -t 10 -p 10 \
python3 WebCrawler -d http://testphp.vulnweb.com/ -t 10 \
python3 WebCrawler -f http://testphp.vulnweb.com/ -t 10 -p 10



