# Database Configuration System

This system provides environment-based database schema management and test data population.

## Configuration File: `database_setup.json`

Located in the project root, this file controls:
- **Environment**: `PRODUCTION` or `TEST`
- **Schema Mapping**: Which schema to use for each environment
- **Test Data**: Predefined data for populating test tables

### Structure

```json
{
  "environment": "TEST",
  "schemas": {
    "PRODUCTION": "SKYFAL",
    "TEST": "TESTFAL"
  },
  "test_data": {
    "TABLE_NAME": [
      {"column1": "value1", "column2": "value2"},
      ...
    ]
  }
}
```

## Usage

### Switching Environments

Edit `database_setup.json` and change the `environment` field:

**For Production:**
```json
{
  "environment": "PRODUCTION",
  ...
}
```

**For Testing:**
```json
{
  "environment": "TEST",
  ...
}
```

The system will automatically:
- Use the correct schema (SKYFAL for production, TESTFAL for test)
- Load the appropriate connection string
- Make test data available (only in TEST mode)

### Populating Test Data

**Option 1: Command Line Utility**
```bash
python populate_test_data.py
```

This interactive script will:
1. Verify you're in TEST environment
2. Warn about data deletion
3. Clear existing test data
4. Insert predefined test data from config
5. Report results

**Option 2: Programmatic Access**
```python
from main.backend.db_pool import db_pool

# Check environment
if db_pool.is_test_environment():
    # Get test data for a specific table
    bun_data = db_pool.get_test_data("TBBUN_TYPES")
    
    # Populate all test data
    results = db_pool.populate_test_data()
```

### Adding New Test Data

Edit `database_setup.json` and add entries to the `test_data` object:

```json
{
  "test_data": {
    "TBNEW_TABLE": [
      {"ID": 1, "NAME": "Test Item", "PRICE": 5.99},
      {"ID": 2, "NAME": "Another Item", "PRICE": 7.99}
    ]
  }
}
```

Column names must match the actual database column names exactly.

## Safety Features

1. **Environment Protection**: `populate_test_data()` can ONLY run in TEST environment
2. **Confirmation Prompt**: The utility script asks for confirmation before deleting data
3. **Automatic Rollback**: Database operations use transactions with automatic rollback on error

## Integration with Connection Pool

The `db_pool` singleton automatically:
- Reads the config on initialization
- Sets the correct schema in connection strings
- Provides helper methods for environment detection

All DAOs and server code automatically use the correct schema without modification.

## Testing Workflow

1. Set `"environment": "TEST"` in `database_setup.json`
2. Run `python populate_test_data.py` to reset test database
3. Run tests: `python main/backend/server_test.py`
4. Database is now in a known state with predictable data

## Production Deployment

1. Set `"environment": "PRODUCTION"` in `database_setup.json`
2. Deploy application
3. Test data population is automatically blocked in PRODUCTION mode

## API Reference

### db_pool Methods

- `get_environment()` - Returns current environment string
- `get_schema()` - Returns current schema name
- `is_test_environment()` - Returns True if in TEST mode
- `get_test_data(table_name=None)` - Get test data for table(s)
- `populate_test_data()` - Populate all tables with test data (TEST only)

## Supported Tables

Current test data is defined for:
- `TBBUN_TYPES` - Bun types with stock
- `TBPATTY_TYPES` - Patty types with stock
- `TBTOPPINGS` - Burger toppings with stock
- `TBFRY_SIZES` - Fry portion sizes (no stock)
- `TBFRY_TYPES` - Fry types with stock
- `TBFRY_SEASONINGS` - Fry seasonings with stock
- `TBCUSTOMER` - Test customers
- `TBORDERS` - Empty (populated by order creation)
- `TBORDER_ITEMS` - Empty (populated by order creation)
- `TBBURGER_ITEMS` - Empty (populated by order creation)
- `TBBURGER_TOPPINGS` - Empty (populated by order creation)
- `TBFRY_ITEMS` - Empty (populated by order creation)
