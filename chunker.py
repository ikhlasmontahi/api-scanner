import requests
import re
import argparse

patterns = {
    'api_keys': r"[\'"](?:[A-Za-z0-9-]{32,})[\'"]|[A-Za-z0-9-]{32,40}|AIza[0-9A-Za-z-_]{35}|AKIA[0-9A-Z]{16}|[0-9a-zA-Z/+]{40}",
    'urls': r"https?://[^\s/$.?#].[^\s]*",
    'endpoints': r"/[a-zA-Z0-9.%+-]+(?:/[a-zA-Z0-9.%+-]+)*",
    'ipv4': r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    'ipv6': r"\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
    'basic_auth': r"Basic\s[0-9a-zA-Z+/=]{20,}",
    'jwt': r"eyJ[0-9a-zA-Z-]+\.[0-9a-zA-Z-]+\.[0-9a-zA-Z-_]+",
    'credentials': r"\"username\":\s*\"[^\s]+\"|\"password\":\s*\"[^\s]+\"",
    'secret_keys': r"(?i)(?:api[-]?key|access[-]?key|client[-]?secret|auth[-]?token|bearer[-]?token|x-api-key|x-access-token)[\'\":\s]*[0-9a-zA-Z\-/]{32,}",
    'emails': r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    'phone_numbers': r"\+?[1-9]\d{1,14}$",
    'aws_keys': r"AKIA[0-9A-Z]{16}|[A-Z0-9]{20}|[0-9a-zA-Z/+]{40}",
    'sensitive_files': r"\b(?:config|secret|key|credentials|auth)\b",
    'error_messages': r"(error|failed|unauthorized|invalid|forbidden|exception|warning|fatal)\b",
    'database_connection_strings': r"(?i)(?:mysql|postgresql|mssql|oracle|sqlite|mongodb|redis)[\w\W]?//[^s]\b",
    'cloud_storage_keys': r"(?i)(?:aws[-]?s3|azure[-]?storage|google[-]?cloud)[\'\":\s]*[0-9a-zA-Z\-/]{32,}",
}

# Function to fetch and process URLs
def fetch_urls_from_file(file_path):
    results = {}
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    results[url] = response.text
            except requests.RequestException as e:
                print(f"Error accessing {url}: {e}")
    return results

# Function to extract data using patterns
def extract_data(html_content):
    extracted_data = {key: set(re.findall(pattern, html_content)) for key, pattern in patterns.items()}
    return extracted_data

# Function to generate a dark-mode HTML report
def generate_html_report(results):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scan Results</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #121212;
                color: #ffffff;
            }
            .section {
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid #444;
                background-color: #1e1e1e;
                border-radius: 5px;
            }
            h1, h2, h3 {
                color: #ffa500;
            }
            a {
                color: #00bcd4;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Scan Results</h1>
    """
    for url, data in results.items():
        html_content += f"<div class='section'><h2>Results for {url}</h2>"
        for key, items in data.items():
            html_content += f"<h3>{key.capitalize().replace('_', ' ')}</h3><ul>"
            for item in items:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
        html_content += "</div>"
    html_content += "</body></html>"
    return html_content

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chunk Scanner Script")
    parser.add_argument("-f", "--file", required=True, help="Path to the file containing JavaScript chunk URLs")
    args = parser.parse_args()

    # Fetch URLs and extract data
    print("Fetching and analyzing JS chunks...")
    raw_results = fetch_urls_from_file(args.file)
    processed_results = {url: extract_data(content) for url, content in raw_results.items()}

    # Generate HTML report
    print("Generating HTML report...")
    report = generate_html_report(processed_results)
    with open("scan_results.html", "w", encoding="utf-8") as f:
        f.write(report)
    print("Scan results saved to scan_results.html")

    print("\nHow to Use This Script:")
    print("1. Collect JavaScript chunk URLs using one of these methods:")
    print("   a. Use 'waybackurls' to fetch archived URLs for the target domain.")
    print("   b. Browse the target site thoroughly, monitor all paths and features.")
    print("   c. Use Burp Suite to capture requests, filter JS chunks, and save the URLs in a text file.")
    print("2. Save the collected URLs to a file (e.g., 'urls-js.txt').")
    print("3. Run the script with:")
    print("   python3 chunk_scanner.py -f urls-js.txt")
    print("4. View the results in the 'scan_results.html' file generated in the same directory.")
