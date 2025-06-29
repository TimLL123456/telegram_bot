# Basic Bookkeeping Telegram Bot Features

- [x] [1-transaction-input-and-extraction-by-llm](#1-transaction-input-and-extraction-by-llm)
- [x] Database Design
- [x] Deploy Database
- [ ] [2. Simple Statistical Report](#2-simple-statistical-report)
- [ ] [3-user-interaction-and-management](#3-user-interaction-and-management)
- [ ] [4-basic-security-and-data-management](#4-basic-security-and-data-management)
- [ ] [5-telegram-specific-features)](#5-telegram-specific-features)

## 1. Transaction Input and Extraction by LLM
   - **Description**: Allow users to input transactions via natural language messages (e.g., "Spent $50 on groceries yesterday" or "Earned $200 from freelance work on May 1").
   - **LLM Extraction Features**:
     - **Date**: Extract the transaction date (default to current date if not specified).
     - **Category**: Identify whether it’s Income or Expense and assign a subcategory (e.g., Income: Salary, Freelance; Expense: Groceries, Utilities).
     - **Description**: Capture a brief description of the transaction.
     - **Price**: Extract the amount with currency support (default to a user-set currency, e.g., USD).
   - **Manual Override**: Allow users to confirm or edit extracted details before saving (e.g., via inline buttons: "Confirm", "Edit Date", "Edit Category").
   - **Command-Based Input**: Support a structured command for quick entry (e.g., `/add Expense Groceries $50 "Bought food" 2025-05-01`).

* **Example**

  1. Paid $25 for a taxi ride this afternoon

  2. Bought concert tickets for 80 dollars yesterday

  3. Spent 12 on coffee and a donut this morning

  4. Got groceries for $45.50 on 2025-05-10

  5. Went to the movies last night and spent 30

  6. Bought a new shirt for 20 bucks today

  7. Had dinner at a restaurant for $75 last Friday

  8. Subscribed to a streaming service for 15 dollars this month

  9. Filled up gas for 40 on 2025-05-08

  10. Bought a book today

## 2. Simple Statistical Report
   - **Income/Expense by Category**:
     - Display a breakdown of total income and expenses per category (e.g., "Groceries: $150, Salary: $1000").
     - Support time filters (e.g., daily, weekly, monthly, custom range).
   - **Total Income/Expense**:
     - Show total income, total expenses, and net balance (Income - Expenses) for a selected period.
   - **Visualization**:
     - Generate simple text-based charts (e.g., ASCII bar charts) or image-based charts (e.g., pie chart for category distribution) sent as Telegram messages.
     - Example: Pie chart showing percentage of expenses by category (Groceries: 40%, Utilities: 30%, etc.).
   - **Command**: Use commands like `/report monthly` or `/summary 2025-05` to trigger reports.

## 3. User Interaction and Management
   - **Start Command**: Provide a `/start` command to welcome users, explain bot functionality, and prompt for initial setup (e.g., default currency).
   - **Help Command**: Include a `/help` command to list available commands and examples of usage.
   - **Currency Support**: Allow users to set a default currency (e.g., USD, EUR) and convert amounts if needed (optional for basic version, can be static).
   - **Transaction History**:
     - Store transactions in a database (e.g., SQLite for simplicity) linked to the user’s Telegram ID.
     - Allow users to view recent transactions (e.g., `/history` to show last 10 transactions).
     - Support deletion or editing of transactions (e.g., `/delete <transaction_id>`, `/edit <transaction_id>`).
   - **Feedback Mechanism**: Include inline buttons or a command (e.g., `/feedback`) for users to confirm or correct LLM-extracted data.

## 4. Basic Security and Data Management
   - **User Authentication**: Tie data to the user’s Telegram ID to ensure privacy and prevent cross-user access.
   - **Data Persistence**: Use a lightweight database (e.g., SQLite) to store transactions securely.
   - **Backup and Export**: Allow users to export their transaction data as a CSV file (e.g., `/export`) for external use.
   - **Error Handling**: Provide clear error messages for invalid inputs (e.g., "Please specify an amount" if price is missing).

## 5. Telegram-Specific Features
   - **Inline Keyboard**: Use Telegram’s inline keyboards for interactive input (e.g., selecting categories, confirming transactions).
   - **Notifications**: Send reminders or alerts (e.g., "You’ve spent $200 this week on groceries") based on user preferences.
   - **Message Formatting**: Use Markdown or HTML for clean, readable messages (e.g., bold categories, monospace amounts).
   - **Rate Limiting**: Prevent abuse by limiting the frequency of commands or large data requests.

## Implementation Notes
- **Language**: Python is recommended for Telegram bot development due to libraries like `python-telegram-bot` and LLM integration (e.g., via Hugging Face or OpenAI APIs).
- **LLM**: Use a lightweight LLM for extraction (e.g., fine-tuned BERT for NER or a small GPT model) to keep costs and latency low.
- **Hosting**: Deploy on a cloud service (e.g., Heroku, AWS) with a webhook for Telegram updates.
- **Visualization**: Use `matplotlib` or `seaborn` for generating charts, saved as images for Telegram delivery.