# ERRORS

## [ERR-20260403-001] logind drop-in apply (sudo mkdir missing)

**Logged**: 2026-04-03T05:19:00+09:00
**Priority**: low
**Status**: resolved
**Area**: config

### Summary
Attempted to create /etc/systemd/logind.conf.d without sudo and got permission denied.

### Error
mkdir: cannot create directory '/etc/systemd/logind.conf.d': Permission denied

### Context
Ran mkdir as normal user before sudo tee path setup.

### Suggested Fix
Use `sudo mkdir -p` for system directories before writing drop-in files.

### Resolution
- **Resolved**: 2026-04-03T05:19:00+09:00
- **Notes**: Re-ran with sudo mkdir.

---
