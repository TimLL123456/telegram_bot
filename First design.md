1. System Architecture

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Telegram Bot│     │ Web Frontend │     │  Database   │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       │                   │                    │
┌──────▼───────────────────▼──────┐      ┌──────▼──────┐
│          Backend API            │      │   LLM API   │
│        (Node.js/Python)         │      │ (OpenAI/etc)│
└─────────────────────────────────┘      └─────────────┘
```

2. Core Components
    
    A. User Authentication

    1. Web Registration/Login:
        
        * Email/password or OAuth (Google/GitHub)
        * JWT token generation
        * Verification email system

    2. Telegram Linking:
        * Connect Telegram account to web account
        * Store Telegram user ID with user profile

    B. Telegram Bot Features

    1. Natural Language Processing:
        * `/spent` $15 on lunch at Cafe Central
        * Add expense: 45.50 transportation Uber
        * Record: 200 groceries at Walmart
        
    2. Commands:
        * `/start` - Initial setup/help
        * `/report` - Generate expense reports
        * `/categories` - Manage spending categories
        * `/budget` - Set budget limits

    C. LLM Integration

    1. Prompt Engineering Example:
        ```text
        Parse this expense entry: "Spent $25.50 on dinner with friends at Italian restaurant"
        Output JSON:
        {
        "amount": 25.50,
        "currency": "USD",
        "category": "Food & Dining",
        "description": "Dinner with friends",
        "merchant": "Italian Restaurant",
        "date": "2023-07-20"
        }
        ```

    2. Error Handling:
        * Fallback to structured input if LLM fails
        * Validation layer before database insertion

    D. Database Design
    ```sql
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE,
        telegram_id BIGINT UNIQUE,
        password_hash VARCHAR(255),
        created_at TIMESTAMP
    );

    CREATE TABLE expenses (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        amount DECIMAL(10,2),
        currency VARCHAR(3),
        category VARCHAR(50),
        description TEXT,
        merchant VARCHAR(100),
        created_at TIMESTAMP
    );

    CREATE TABLE categories (
        user_id INTEGER REFERENCES users(id),
        name VARCHAR(50),
        budget_limit DECIMAL(10,2)
    );
    ```

3. Technology Stack Recommendation

    A. Backend
    * Python (FastAPI/Django)
    * PostgreSQL/MySQL
    * Redis (for caching)

    B. NLP Processing
    * OpenAI API (gpt-3.5-turbo)
    * OR Hugging Face (Mistral-7B for self-hosted)

    C. Telegram Bot
    * python-telegram-bot library
    * Webhook setup

    D. Web Frontend
    * React.js/Next.js
    * Tailwind CSS
    * Axios for API calls

4. Workflow Sequence

    1. User Registration:
        
        Web → Email verification → Telegram linking

    2. Expense Recording:

        ```text
        User → Bot: "Spent $15.50 on coffee at Starbucks"
        Bot → LLM: Parse message
        LLM → Bot: Structured JSON
        Bot → DB: Store validated data
        Bot → User: "✅ Added $15.50 under Food & Beverage"
        ```

    3. Data Retrieval:

        ```text
        User → Bot: "/report week"
        Bot → DB: Query data
        Bot → User: Visual chart + CSV export
        ```

5. Security Considerations
    1. Data Encryption:
        * TLS for all communications
        * Encrypt sensitive database fields

    2. Authentication:
        * JWT expiration (1 hour)
        * Refresh tokens
        * Rate limiting

    3. Validation:
        * LLM output sanitization
        * User-based access control

6. Advanced Features Roadmap
    1. Multi-currency support
    2. Receipt image recognition (OCR + LLM)
    3. Automated spending insights
    4. Shared expenses (group features)
    5. Budget alerts/notifications

7. Development Milestones
    1. Phase 1 (Core MVP - 2 weeks)
        * User authentication system
        * Basic Telegram bot integration
        * LLM parsing prototype

    2. Phase 2 (Data Management - 3 weeks)
        * Expense CRUD operations
        * Basic reporting
        * Category management

    3. Phase 3 (Polish - 1 week)
        * Error handling
        * Notifications
        * Documentation
