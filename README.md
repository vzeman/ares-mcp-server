# ARES MCP Server

A Model Context Protocol (MCP) server that provides access to the Czech ARES (Administrativní registr ekonomických subjektů) API.

## Features

- Search for economic subjects by IČO, name, or address
- Get detailed information about specific companies
- Retrieve business register extracts
- Validate IČO (Czech company identification numbers)
- Built-in rate limiting to respect API constraints
- Full async/await support

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Option 1: Automated Setup (Recommended)

The easiest way to get started is using the automated setup script:

#### macOS/Linux
```bash
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server
./run.sh
```

#### Windows
```bash
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server
run.bat
```

The script will automatically:
- Check Python version
- Create virtual environment
- Install all dependencies
- Create configuration file
- Optionally start the server

### Option 2: Manual Setup

If you prefer manual installation:

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ares-mcp-server.git
cd ares-mcp-server
```

#### 2. Create Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with system packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Or install the package in development mode
pip install -e .
```

## Running the Server

### Quick Start

The easiest way to run the server:

```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

### Manual Start

To run the server directly:

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Run the server
python -m ares_mcp_server.server
```

### Integration with Claude Desktop

Add the server to your Claude Desktop configuration:

#### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ares": {
      "command": "/path/to/ares-mcp-server/venv/bin/python",
      "args": ["-m", "ares_mcp_server.server"],
      "cwd": "/path/to/ares-mcp-server"
    }
  }
}
```

#### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ares": {
      "command": "C:\\path\\to\\ares-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["-m", "ares_mcp_server.server"],
      "cwd": "C:\\path\\to\\ares-mcp-server"
    }
  }
}
```

**Note**: Make sure to use the full path to the Python executable in your virtual environment.

## Configuration

The server can be configured using environment variables. Create a `.env` file in the project root:

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your preferences
```

Available configuration options:

- `ARES_RATE_LIMIT_REQUESTS`: Maximum requests per time window (default: 100)
- `ARES_RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)
- `ARES_REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

## Available Tools

### ares_search_subject
Search for economic subjects in the ARES registry.

Parameters:
- `ico` (optional): Company identification number (8 digits)
- `name` (optional): Company name or part of it
- `address` (optional): Company address or part of it

At least one parameter must be provided.

### ares_get_subject
Get detailed information about a specific economic subject.

Parameters:
- `ico` (required): Company identification number (8 digits)

### ares_get_extract
Get business register extract for a company.

Parameters:
- `ico` (required): Company identification number (8 digits)
- `extract_type` (optional): Type of extract - "standard" (default), "complete", or "basic"

### ares_validate_ico
Validate if IČO is correctly formatted and exists in ARES.

Parameters:
- `ico` (required): Company identification number to validate

## Example Usage in Claude

Once configured, you can use the ARES tools in Claude:

```
Search for a company by name:
Use ares_search_subject with name "Microsoft"

Get details about a specific company:
Use ares_get_subject with ico "12345678"

Validate a company ID:
Use ares_validate_ico with ico "12345678"
```

## Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux

# Run tests with pytest
pytest tests/

# Run tests with coverage
pytest tests/ --cov=ares_mcp_server --cov-report=html

# Run specific test file
pytest tests/test_api_client.py
```

### Code Quality

```bash
# Format code with black
black ares_mcp_server/

# Check code style with flake8
flake8 ares_mcp_server/

# Sort imports with isort
isort ares_mcp_server/

# Type checking with mypy
mypy ares_mcp_server/
```

### Running Examples

```bash
# Activate virtual environment
source venv/bin/activate

# Run the example script
python examples/usage_example.py
```

## Project Structure

```
ares-mcp-server/
├── ares_mcp_server/
│   ├── __init__.py
│   ├── server.py       # Main MCP server implementation
│   ├── api_client.py   # ARES API client with rate limiting
│   └── tools.py        # MCP tool definitions
├── tests/
│   └── test_api_client.py
├── examples/
│   └── usage_example.py
├── .env.example        # Example configuration
├── .gitignore
├── pyproject.toml      # Package configuration
├── requirements.txt    # Python dependencies
└── README.md
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'mcp'**
   - Make sure you've activated the virtual environment
   - Run `pip install -r requirements.txt`

2. **Rate limit errors**
   - The server implements automatic rate limiting
   - Adjust `ARES_RATE_LIMIT_REQUESTS` in `.env` if needed

3. **Connection timeouts**
   - Check your internet connection
   - Increase `ARES_REQUEST_TIMEOUT` in `.env`

4. **Virtual environment not found**
   - Ensure you've created it: `python3 -m venv venv`
   - Check the path in Claude Desktop configuration

## API Rate Limiting

The ARES API has usage limits. This server implements:

- Automatic rate limiting (default: 100 requests per minute)
- Request queuing when limits are reached
- Graceful error handling for API errors

## Error Handling

The server provides comprehensive error handling:

- HTTP errors are caught and formatted with details
- Network timeouts are handled gracefully
- Invalid parameters return descriptive error messages
- All errors are returned in JSON format

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support

For issues or questions:
- Create an issue on GitHub
- Check the ARES API documentation at https://ares.gov.cz/swagger-ui/

## Acknowledgments

This server integrates with the Czech ARES API provided by the Ministry of Finance of the Czech Republic.