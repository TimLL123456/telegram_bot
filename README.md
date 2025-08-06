# Personal Finance Telegram Bot

A sophisticated Telegram bot for personal finance management that uses AI-powered natural language processing to extract transaction details from user messages. Built with Flask, integrated with Supabase database, and deployable via Docker.

## 🚀 Features

### Core Functionality
- **AI-Powered Transaction Parsing**: Uses LLM (DeepSeek) to extract transaction details from natural language input
- **Multi-Language Support**: Supports English and Chinese transaction inputs
- **Automatic Categorization**: Intelligently categorizes transactions into Income/Expense with subcategories
- **Currency Support**: Multi-currency support with automatic detection
- **Date Recognition**: Flexible date parsing (relative dates like "yesterday", "last Friday")

### Transaction Management
- **Natural Language Input**: "Spent 50 HKD on 7-11 today" → Structured transaction data
- **Manual Transaction Entry**: Structured command-based input for precise control
- **Transaction History**: View, edit, and delete past transactions
- **Category Management**: Custom categories for better organization

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │────│   Flask API     │────│   Supabase DB   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   LLM Service   │
                       │   (DeepSeek)    │
                       └─────────────────┘
```

### Components
- **Flask Application**: Main API server handling Telegram webhooks
- **Telegram Bot**: User interface via Telegram messaging
- **Supabase Database**: PostgreSQL database for data persistence
- **LLM Integration**: AI-powered transaction parsing
- **Streamlit Dashboard**: Web-based analytics interface
- **Docker Support**: Containerized deployment

## 📋 Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Telegram Bot Token
- Supabase Account
- DeepSeek API Key

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # LLM API Keys
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   
   # Database Configuration
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   
   # Optional APIs
   COINMARKETCAP_API=your_coinmarketcap_api_key_here
   ```

4. **Database Setup**
   Run the SQL scripts in `Database Design.md` to set up your Supabase database:
   - Create tables (Users, Categories, Transactions, Transaction_History)
   - Set up triggers and functions
   - Insert default categories

### Docker Setup

1. **Build the Flask application**
   ```bash
   docker build -f ./Docker/dockerfile.flask -t flask-app .
   ```

2. **Build the Streamlit dashboard**
   ```bash
   docker build -f ./Docker/dockerfile.streamlit -t streamlit-app .
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose -f ./Docker/docker-compose.yml up
   ```

## ⚙️ Configuration

### Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Set webhook URL (for production) or use polling (for development)

### Database Schema

The application uses a PostgreSQL database with the following main tables:
- `Users`: User information and preferences
- `Categories`: Transaction categories (Income/Expense)
- `Transactions`: Financial transactions with soft delete support
- `Transaction_History`: Immutable audit trail

See `Database Design.md` for complete schema and setup instructions.

## 🚀 Usage

### Starting the Bot

**Production (Webhook)**
```bash
python draft/scr_v2/app.py
```

### Bot Commands

- `/start` - Initialize the bot and register user
- `/ai <transaction>` - Parse transaction using AI
- `/monthlysummary` - Get monthly financial summary
- `/help` - Show available commands

### Example Interactions

```
User: /ai Spent 50 HKD on 7-11 today
Bot: ✅ Transaction recorded:
     📅 Date: 2025-08-05
     🏪 Description: 7-11
     💰 Amount: 50.00 HKD
     📂 Category: Other (Expense)

User: /ai mike 120蚊
Bot: ✅ Transaction recorded:
     📅 Date: 2025-08-05
     🏪 Description: Mike
     💰 Amount: 120.00 HKD
     📂 Category: Other (Expense)
```

## 🚀 Deployment

### AWS Deployment

1. **Build and push Docker images to ECR**
   ```bash
   # Build image
   docker build -f ./Docker/dockerfile.flask -t flask-app .
   
   # Tag for ECR
   docker tag flask-app 345345405651.dkr.ecr.ap-southeast-1.amazonaws.com/testing:flask-app
   
   # Push to ECR
   docker push 345345405651.dkr.ecr.ap-southeast-1.amazonaws.com/testing:flask-app
   ```

2. **Deploy on EC2**
   ```bash
   # Pull image
   docker pull 345345405651.dkr.ecr.ap-southeast-1.amazonaws.com/testing:flask-app
   
   # Run container
   docker run -p 5000:5000 flask-app
   ```

3. **Set up Ngrok for webhook**
   ```bash
   ngrok http http://localhost:5000
   ```

See `AWS Deploy Tutorial.md` for detailed deployment instructions.

### Local Development with Ngrok

1. **Start the Flask application**
   ```bash
   python draft/scr_v2/app.py
   ```

2. **Start Ngrok**
   ```bash
   ngrok http 5000
   ```

3. **Set Telegram webhook**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<NGROK_URL>"
   ```

## 🧪 Development

### Project Structure

```
telegram_bot/
├── draft/                # Development versions
│   ├── scr_v2/           # Latest webhook version
│   └── Run_polling_version/ # Polling version
├── Docker/               # Docker configuration
├── Database Design.md    # Database schema
├── AWS Deploy Tutorial.md # Deployment guide
└── requirements.txt      # Python dependencies
```

### Key Components

- **LLM Integration**: `llm_tools.py` - Transaction parsing using DeepSeek
- **Database Layer**: `supabase_api.py` - Database operations
- **Telegram API**: `telegram_api.py` - Bot communication
- **Command Handling**: `command_manager.py` - Bot command processing
- **Callback Management**: `callback_manager.py` - Inline keyboard handling

### Logging

The application uses structured logging with different levels:
- **DEBUG**: Detailed function entry/exit logs
- **INFO**: General application flow
- **ERROR**: Error conditions and exceptions

Logs are written to both console and `app.log` file.
