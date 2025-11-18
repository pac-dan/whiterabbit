# Momentum Clips - Test Suite

## Overview

This directory contains the test suite for the Momentum Clips application.

## Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Pytest fixtures and configuration
├── test_models.py        # Database model tests
├── test_routes.py        # Route/view tests
└── README.md             # This file
```

## Running Tests

### Install Test Dependencies

First, make sure pytest is installed:

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_models.py
pytest tests/test_routes.py
```

### Run Specific Test Class

```bash
pytest tests/test_models.py::TestUserModel
```

### Run Specific Test Function

```bash
pytest tests/test_models.py::TestUserModel::test_create_user
```

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

## Test Coverage

Current test coverage includes:

### Models
- ✅ User model (creation, password hashing, admin users)
- ✅ Package model (creation, active packages)
- ✅ Video model (creation, YouTube URLs, view counting)
- ✅ Testimonial model (creation, featured testimonials)

### Routes
- ✅ Main routes (homepage, about, gallery, packages, etc.)
- ✅ Auth routes (login, register, logout flow)
- ✅ Booking routes (index, authentication requirements)
- ✅ Admin routes (dashboard access control)
- ✅ Video routes (detail pages)

## Fixtures Available

See `conftest.py` for all available fixtures:

- `app` - Flask application instance
- `client` - Test client
- `runner` - CLI runner
- `sample_user` - Regular user
- `admin_user` - Admin user
- `sample_package` - Test package
- `sample_video` - Test video
- `sample_testimonial` - Test testimonial

## Writing New Tests

### Example Test

```python
def test_my_feature(client, sample_user):
    """Test description"""
    response = client.get('/my-route')
    assert response.status_code == 200
    assert b'Expected Content' in response.data
```

### Test Organization

- Group related tests in classes
- Use descriptive test names starting with `test_`
- Use fixtures to avoid code duplication
- Test both success and failure cases
- Test authentication/authorization requirements

## CI/CD Integration

These tests can be integrated into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest --cov=app --cov-report=xml
```

## Future Additions

Consider adding tests for:

- [ ] Form validation
- [ ] API endpoints
- [ ] Email sending
- [ ] Payment processing (with mocks)
- [ ] File uploads
- [ ] Integration tests
- [ ] End-to-end tests with Selenium

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/latest/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

