# Virtual Economy Application

## Project Overview

This is a FastAPI-based virtual economy application that provides a platform for managing virtual goods, user inventories, and transactions. The application features a modern architecture with support for asynchronous operations, background tasks, caching, and analytics.

### Key Technologies
- **FastAPI**: Web framework for building APIs with automatic OpenAPI documentation
- **SQLAlchemy**: Database ORM with async support
- **PostgreSQL**: Primary database for persistent data storage
- **Redis**: Caching layer and message broker for background tasks
- **Celery**: Distributed task queue for background processing
- **Alembic**: Database migration management
- **Docker & Docker Compose**: Containerization and orchestration

### Architecture Components
- **API Layer**: FastAPI endpoints for user interactions, purchases, and inventory management
- **Database Layer**: SQLAlchemy async models with PostgreSQL backend
- **Background Services**: Celery workers for processing tasks and Celery Beat for scheduled tasks
- **Caching Layer**: Redis for temporary data storage and task queuing
- **Middlewares**: Request processing and security layers

### Core Features
- User inventory management
- Product purchase handling
- Product usage tracking
- Fund management for users
- Popular products analytics
- Health checking endpoints

## Building and Running

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (if running without Docker)
- Redis (if running without Docker)

### Development Setup
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r dev.requirements.txt  # For development tools
   ```

2. **Environment Configuration**:
   - Copy `.example.env` to `.env` and configure your settings
   - Set up database connection parameters
   - Configure Redis and Celery settings as needed

3. **Run in Development**:
   ```bash
   # Direct Python execution (requires external PostgreSQL and Redis)
   python dev_run.py
   
   # Or using Docker Compose
   docker-compose up --build
   ```

4. **Database Migrations**:
   ```bash
   # Run migrations manually (if not using Docker)
   alembic upgrade head
   ```

### Production Deployment
1. Build the Docker image:
   ```bash
   docker build -t virtual-economy .
   ```

2. Deploy with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### API Endpoints
- `/api/v1/health` - Health check endpoint
- `/api/v1/products/purchase` - Product purchase functionality
- `/api/v1/products/use` - Product usage tracking
- `/api/v1/users/inventory` - User inventory management
- `/api/v1/users/add-funds` - Add funds to user account
- `/api/v1/analytics/popular-products` - Popular products analytics

### Background Tasks
The application uses Celery for handling background tasks:
- Worker service: `celery-worker` container
- Scheduled tasks: `celery-beat` container
- Message broker: Redis
- Result backend: Redis

### Database Structure
- Migrations are managed through Alembic
- Async SQLAlchemy models are used for database operations
- PostgreSQL is the primary database backend

### Recommended Database Indexes
For optimal performance, the following indexes should be added to the database:

1. **Inventory Table**:
   - Composite index on (user_id, product_id) for efficient lookups in purchase service
   - Single index on user_id for retrieving user inventories

2. **Transaction Table**:
   - Index on status for filtering completed transactions
   - Index on created_at for date range queries in analytics
   - Index on product_id for grouping transactions by product
   - Composite index on (status, created_at) for popular products analytics

3. **Product Table**:
   - Index on is_active for filtering active products

## Development Conventions

### Code Structure
- `app/` - Main application source code
- `app/api/` - API endpoints and handlers
- `app/database/` - Database models and connection logic
- `app/redis/` - Redis client and configuration
- `app/background/` - Background task definitions (Celery)
- `app/services/` - Business logic services
- `app/schemas/` - Pydantic models for request/response validation
- `app/repositories/` - Data access layer
- `app/utils/` - Utility functions
- `app/middlewares/` - Request processing middlewares

### Environment Variables
The application uses environment variables for configuration:
- Database connection settings (`DB_*`)
- Redis settings (`RADIS_*`)
- Celery settings (`CELERY_*`)
- API settings (`API_*`)

### Testing
Tests are located in the `tests/` directory. To run tests:
```bash
pytest
```

### Configuration Management
- Settings are managed through Pydantic models in `app/settings.py`
- Environment-specific configurations are loaded from `.env` files
- Different settings modules exist for API, database, and Redis components