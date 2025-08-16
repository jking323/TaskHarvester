# Action Item Extractor

An intelligent application that automatically extracts action items from Outlook emails and Teams conversations, then creates tasks in Wrike using on-device AI.

## System Requirements
- Windows 10/11
- Intel i7 12th gen (or equivalent)
- NVIDIA RTX 4000 (20GB VRAM)
- 32GB System RAM
- 50GB available storage

## Features
- **On-Device AI**: Local processing using Llama 3.1 8B model
- **Outlook Integration**: Automatic email monitoring and parsing
- **Teams Integration**: Meeting transcript and chat analysis
- **Wrike Integration**: Automated task creation and assignment
- **Smart Filtering**: Confidence-based action item detection
- **Review Queue**: Manual approval workflow for extracted items

## Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd action-item-extractor
./setup.sh
```

### 2. Configuration
1. Run the desktop application
2. Complete the setup wizard:
   - Microsoft OAuth (Outlook/Teams)
   - Wrike API connection
   - User mappings and preferences

### 3. First Run
- The application will start monitoring your Outlook and Teams
- Extracted action items appear in the review queue
- Approve items to automatically create Wrike tasks

## Architecture
- **Backend**: Python FastAPI with SQLite
- **Desktop App**: Electron with React
- **AI Engine**: Ollama with Llama 3.1 8B
- **APIs**: Microsoft Graph, Wrike REST API

## Development
See `/docs` for detailed development setup and API documentation.