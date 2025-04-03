## User Registration & Information Updates

### Key Functionality
1. **User Registration**
   - Automatically captures user information when a new user initiates the bot via `/start` command
   - Stores: Telegram username, first name, last name, and user ID

2. **Information Updates**
   - Tracks changes to user profile data over time (username, first name, last name)
   - Updates database records when profile changes are detected

### Implementation Details
- **First-Time Registration** (`/start` handler):
  - Creates new user record in database
  - Captures initial profile information

- **Profile Update Logic**:
  - Compares current profile data with stored values
  - Updates database when changes are detected
  - Maintains historical records of profile changes
  - State-aware checking to determine when verification occurs

### Technical Considerations
- Uses Telegram's user object for profile data
- Implements change detection before updates
- Maintains data consistency across registration and update flows