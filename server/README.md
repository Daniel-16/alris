# Alris Server

A FastAPI-based server that powers Alris's automation engine, transforming natural language commands into executable tasks through both REST and WebSocket endpoints.

## Architecture

Alris follows a layered architecture with three distinct layers:

### 1. LangChain Agent Layer

- **Purpose**: The intelligent core that interprets and plans task execution.
- **Responsibilities**:
  - Uses language models to understand user intent
  - Breaks commands into actionable steps
  - Coordinates the use of tools via the MCP Layer
- **Components**: `AgentOrchestrator`, `BrowserAgent`, etc.

### 2. MCP (Model Context Protocol) Layer

- **Purpose**: A connector that links agents to external tools.
- **Responsibilities**:
  - Provides standardized access to tools like Playwright for browser automation
  - Manages tool invocation
- **Components**: `MCPConnector`, `AlrisMCPClient`

### 3. External Services Layer

- **Purpose**: Executes the tasks in the real world.
- **Responsibilities**:
  - Handles actions like browser navigation, form filling, or API calls
  - Includes services for browser automation, email, etc.
- **Components**: `BrowserService`, `EmailService`, etc.

## Features

- Real-time communication via WebSocket
- Browser automation capabilities
- Google Calendar event scheduling
- REST API endpoints
- AI agent integration
- Cross-Origin Resource Sharing (CORS) support
- **Enhanced Form Automation**: Alris can now extract, infer, and fill web forms from natural language commands, intelligently handling missing fields and prompting the user for clarification when needed.

## Prerequisites

- Python 3.x
- Virtual environment (recommended)

## Dependencies

Major dependencies include:

- FastAPI
- Uvicorn
- Pydantic
- Playwright
- LangChain
- Google Generative AI
- MCP (Model Context Protocol)
- WebSockets

## Installation

1. Clone the repository
2. Create and activate a virtual environment:

```bash
python -m venv myenv
source myenv/bin/activate  # On Linux/Mac
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:

```bash
playwright install
```

5. Configure environment variables in a .env file:

```
# Google Apps Script for Calendar Integration
GOOGLE_APPS_SCRIPT_CALENDAR_URL="your-google-apps-script-url"
```

## Running the Server

### Option 1: Using the start script (Recommended)

The simplest way to start the Alris server with proper MCP service initialization is to use the provided start script:

```bash
# From the server directory
./start_alris.py
```

This script will:

1. Start the MCP server as a separate process
2. Wait for it to initialize
3. Start the main Alris application with proper connections

If you encounter any issues with calendar features, this is the recommended way to start the server.

### Option 2: Manual startup

Start the server using:

```bash
python run.py
```

The server will start on the default host and port (typically localhost:8000).

## Example Usage

Here's an example of how Alris processes the command "Fill out the form on example.com with name 'John'":

1. **LangChain Agent Layer**:
   - Interprets the command and plans steps: navigate to URL, find name field, input "John", submit
   - **NEW:** Extracts and infers all required form fields (e.g., name, email, country, gender), using defaults or user profile if not specified. Prompts the user if required fields are missing.
2. **MCP Connector Layer**:
   - Provides tools to the agent:
     - `navigate_to_url("https://example.com")`
     - `fill_form({"name": "John", "country": "Nigeria", "gender": "male"})`
     - `click_button("#submit")`
3. **External Services Layer (Playwright)**:
   - Executes the actions in a browser:
     - Loads the webpage
     - Inputs the extracted/inferred data in the form fields
     - Submits the form
   - If the form has errors (e.g., required fields missing), Alris requests the necessary information and retries.

Another example, scheduling a calendar event:

1. **LangChain Agent Layer**:
   - Interprets the command "Schedule a meeting with the team tomorrow at 3pm for 1 hour"
   - Identifies date/time and converts to ISO format
2. **MCP Connector Layer**:
   - Provides tools to the agent:
     - `schedule_calendar_event(title="Team Meeting", start_time="2025-04-21T15:00:00", end_time="2025-04-21T16:00:00")`
3. **External Services Layer**:
   - Makes an API call to the Google Apps Script
   - The script creates the event in Google Calendar

## API Endpoints

### WebSocket Endpoint

- `/ws` - WebSocket endpoint for real-time communication

### REST Endpoints

- `GET /health` - Health check endpoint

## Browser Automation

The server includes browser automation capabilities through the following tools:

- General browser actions (navigation, form filling, clicking)
- YouTube search functionality
- Web navigation

## Calendar Integration

The server supports Google Calendar integration through Google Apps Script. This allows Alris to schedule events in your Google Calendar directly from natural language commands.

### Setup Instructions

1. **Create a Google Apps Script:**

   - Go to [Google Apps Script](https://script.google.com/home) and create a new project
   - Replace the default code with the calendar integration script found in `config/calendar_setup.md`
   - Deploy the script as a web app (Execute as yourself, Anyone can access)
   - Copy the Web App URL

2. **Configure Environment Variables:**

   - Add the Google Apps Script URL to your `.env` file:
   `    GOOGLE_APPS_SCRIPT_CALENDAR_URL=https://script.google.com/macros/s/your-unique-deployment-id/exec
`
   <!--

3. **Testing the Integration:**
   - Run the test script to verify the calendar integration:
     ```bash
     python test_calendar.py
     ```
   - If successful, you should see a test event created in your Google Calendar -->

### Using Calendar Commands

Once set up, you can use natural language commands to schedule events:

- "Schedule a meeting for tomorrow at 3pm"
- "Create an event called Team Standup for today at 9am"
- "Add a calendar appointment titled Doctor visit for Friday at 2:30pm"
- "Remind me about my dentist appointment on December 15th at 10am"

The system will automatically:

1. Detect the calendar intent
2. Parse the date, time, and title information
3. Create the event in your Google Calendar
4. Provide confirmation that the event has been scheduled

### Troubleshooting

If you encounter issues with the calendar integration:

1. Check that the `GOOGLE_APPS_SCRIPT_CALENDAR_URL` is correctly set in your environment
2. Ensure your Google Apps Script is deployed as a web app with appropriate permissions
3. Check the server logs for detailed error messages
4. Make sure your Google account has permission to create events in your calendar

The system includes a fallback mechanism that will use a simpler direct HTTP approach if the MCP server connection fails. This ensures calendar functionality works even when there are MCP configuration issues.

For more detailed setup instructions, see `config/calendar_setup.md`.

<!-- ## Error Handling

The server implements comprehensive error handling for both WebSocket and REST endpoints, providing clear error messages in case of failures. -->

## Security

- CORS is enabled with appropriate middleware
- Input validation using Pydantic models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Copyright (c) 2025 Daniel Toba

This project is licensed under the Apache License, Version 2.0 - see http://www.apache.org/licenses/LICENSE-2.0 for details.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
