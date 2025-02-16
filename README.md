# File Manager with AI Agent

A Python-based file management system with an AI agent that automatically organizes and compresses files based on their types.


![image](https://github.com/user-attachments/assets/33d2e3a6-2b8f-4df7-a3a0-dc0da0460456)


## Features

- Automatic file organization by type (PDF, JPG, PNG)
- Multiple compression methods support:
  - TinyPNG for image compression
  - ConvertAPI for PDF compression
  - ZIP compression as fallback
- AI-powered task planning and execution
- Configurable file types and compression methods
- Comprehensive error handling and logging

## Prerequisites

- Python 3.8 or higher
- API keys for:
  - Google Gemini AI
  - TinyPNG
  - ConvertAPI

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-manager.git
cd file-manager
```

2. Install dependencies:
```bash
pip install -r src/requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```bash
API_KEY=your_google_gemini_api_key
TINYPNG_API_KEY=your_tinypng_api_key
CONVERTAPI_API_KEY=your_convertapi_api_key
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/file-manager.git
cd file-manager
```

2. Create a `.env` file as described above.

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

Or use Docker directly:
```bash
docker build -t file-manager .
docker run -v $(pwd)/data:/app/data -v $(pwd)/.env:/app/.env file-manager
```

## Project Structure
```
├── data/
│ ├── input_folder/ # Place files to be organized here
│ └── output_folder/ # Organized files will be here
├── src/
│ ├── agent_file_manager.py # AI agent implementation
│ ├── file_manager.py # Core file management functions
│ ├── prompts.py # AI system prompts
│ ├── file_manager_config.yml # File manager configuration
│ └── agentic_config.yml # AI agent configuration
│ └── test_file_manager.py # Unit tests
└── README.md
```

## Configuration

### File Manager Configuration (file_manager_config.yml)

```yaml
compression_method:
- PDF: "convertapi"
- JPG: "tinypng"
- PNG: "tinypng"
file_types:
- PDF
- JPG
- PNG
```

### AI Agent Configuration (agentic_config.yml)
```yaml
llm:
model: gemini-2.0-flash
temperature: 0.1
max_output_tokens: 10000
functions_file_path: "src/file_manager.py"
input_folder_path: "data/input_folder"
output_folder_path: "data/output_folder"
```

## Usage

1. Place files to be organized in the `data/input_folder` directory

2. Run the file manager:
```bash
python src/agent_file_manager.py
```

3. Check the `data/output_folder` directory for organized and compressed files

The system will:
1. Scan the input folder for files
2. Create type-specific folders in the output directory
3. Move files to their respective folders
4. Compress files using the configured compression method

## Testing

Run the test suite:

```bash
pytest src/test_file_manager.py
```

## Core Functions

- `load_config()`: Load configuration from YAML file
- `folder_scanner()`: Scan directory for files
- `file_type_identifier()`: Identify file types
- `folder_creator()`: Create organized folders
- `file_mover()`: Move files to appropriate folders
- `file_compressor()`: Compress files using configured methods

## AI Agent Features

- Task decomposition
- Function sequence planning
- Error handling and recovery
- Execution monitoring

## Error Handling

The system includes comprehensive error handling for:
- Missing or invalid files
- API failures
- Permission issues
- Configuration errors
- Compression failures

## Acknowledgments

- TinyPNG for image compression
- ConvertAPI for PDF compression
- Google Gemini AI for intelligent task planning

## Docker Usage

The Docker setup provides the following features:
- Isolated environment with all dependencies
- Mounted volumes for input/output folders
- Environment variables through .env file
- Persistent data storage

### Using Docker Compose

1. Start the service:
```bash
docker-compose up
```

2. Place files in the `data/input_folder` directory

3. The service will automatically process files

4. Check `data/output_folder` for results

### Using Docker Directly

1. Build the image:
```bash
docker build -t file-manager .
```

2. Run the container:
```bash
docker run -v $(pwd)/data:/app/data -v $(pwd)/.env:/app/.env file-manager
```

### Docker Development Mode

For development, you can mount the source code directory:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
