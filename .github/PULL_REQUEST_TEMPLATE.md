**High level description:**
<!-- High level description of what the PR addresses should be put here. Should be detailed enough to communicate to the client what this PR addresses without diving into the technical nuances. -->

**Technical details:**
<!-- The technical details can be placed here for the knowledge of other developers. Any detailed caveats or specific deployment steps should be outlined here. -->

## Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

# How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration

[x] API Route Tests
- Location: `/backend/app/tests/api/routes/`
  ```bash
  # Run specific test files
  pytest backend/app/tests/api/routes/test_users.py -v
  pytest backend/app/tests/api/routes/test_login.py -v
  pytest backend/app/tests/api/routes/test_equipment.py -v

  # Run all route tests
  bash backend/scripts/test.sh
  ```
- [ ] Test B

### Test Configuration:

- **Environment**: Local Development
- **Database**: PostgreSQL
- **Python Version**: 3.10.10
- **FastAPI Version**: 0.115.0
- **Testing Tools**:
  - pytest 7.4.4

# Checklist:

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published in downstream modules
