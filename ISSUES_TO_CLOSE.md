# Issues Recommended for Closure

The following issues have been triaged and found to be already resolved, not actionable from this repository, or no longer relevant.

## Already Fixed in Codebase

| # | Title | Reason |
|---|-------|--------|
| 282 | AlarmSeverity not reset on reconnect | Fixed in current code — `connection_changed` sends `ALARM_NONE` on reconnect (`base.py:757`) |
| 594 | Trace disappears with logY | Fixed by pyqtgraph 0.14 — `autoRange` now handles NaN from `log10(0)` correctly |
| 1239 | Crosshair labels not cleared when disabled | Fixed in PR #1256 (commit `369e8b14`) |
| 1265 | Qt Designer incorrectly sets penStyle | Fixed in commits `9b345b0a` and `e4655950` |
| 1267 | PyDMShellCommand RuntimeError on PySide6 | Fixed in commit `a70719ac` — internal timer now stops on object destroy |

## No Longer Relevant

| # | Title | Reason |
|---|-------|--------|
| 611 | Installation fails with PySide2 due to qRound | `qRound` is no longer used in the codebase, and PySide2 is EOL. Only PyQt5 and PySide6 are supported. |
| 853 | PyDM doesn't work with newest PyQt 5.15.4 | Resolved — test suite passes on PyQt5 5.15.11 with no version pin required. |

## Not Actionable / Not a Bug

| # | Title | Reason |
|---|-------|--------|
| 1083 | Macros don't propagate via PyDMEDMDisplayButton | `PyDMEDMDisplayButton` is from an external EDM converter package, not part of pydm. The built-in `PyDMRelatedDisplayButton` already propagates parent macros correctly via `find_parent_display().macros()`. |
| 1305 | EDM screens don't launch on first click | Cannot reproduce per maintainer comment. Appears to be an external EDM server race condition, not a pydm issue. |
| 1320 | asyn_record.ui won't launch from home directories | Not a bug — the file is not in the default search path. Use the `-r` flag for recursive search or set the `PYDM_DISPLAYS_PATH` environment variable to include the directory containing the file. |
