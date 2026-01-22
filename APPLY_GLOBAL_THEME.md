# Apply IntelliJ Islands Dark Theme Globally

This guide explains how to apply the IntelliJ Islands Dark color theme to all your Cursor workspaces.

## Quick Method (Recommended)

1. **Open Cursor Settings:**
   - Press `Ctrl+,` (or `Cmd+,` on Mac) to open Settings
   - Or go to `File > Preferences > Settings`

2. **Open Settings JSON:**
   - Click the `{}` icon in the top-right corner of the Settings tab
   - This opens `settings.json` directly

3. **Copy Settings:**
   - Open the file `cursor-user-settings-template.json` in this directory
   - Copy all its contents
   - Paste into your user `settings.json` file
   - If you already have settings, merge the JSON objects (combine the properties)

4. **Save and Reload:**
   - Save the file (`Ctrl+S`)
   - Reload Cursor window (`Ctrl+Shift+P` → "Reload Window")

## Manual Method

### Windows
1. Navigate to: `%APPDATA%\Cursor\User\settings.json`
2. Open the file in a text editor
3. Copy the contents from `cursor-user-settings-template.json`
4. Merge with your existing settings (if any)
5. Save and reload Cursor

### macOS
1. Navigate to: `~/Library/Application Support/Cursor/User/settings.json`
2. Open the file in a text editor
3. Copy the contents from `cursor-user-settings-template.json`
4. Merge with your existing settings (if any)
5. Save and reload Cursor

### Linux
1. Navigate to: `~/.config/Cursor/User/settings.json`
2. Open the file in a text editor
3. Copy the contents from `cursor-user-settings-template.json`
4. Merge with your existing settings (if any)
5. Save and reload Cursor

## Merging with Existing Settings

If you already have user settings, you need to merge the JSON objects. For example:

**Before:**
```json
{
  "editor.fontSize": 14,
  "files.autoSave": "afterDelay"
}
```

**After (merged):**
```json
{
  "editor.fontSize": 14,
  "files.autoSave": "afterDelay",
  "workbench.colorTheme": "Islands Dark",
  "workbench.colorCustomizations": {
    ...
  },
  "editor.tokenColorCustomizations": {
    ...
  }
}
```

## What This Does

- Applies the IntelliJ Islands Dark color theme to all workspaces
- Customizes editor colors (background, foreground, selection, etc.)
- Adds syntax highlighting for:
  - TypeScript/JavaScript
  - HTML
  - SCSS/CSS
  - Python
  - LaTeX

## Notes

- These settings will apply to **all** Cursor workspaces
- Workspace-specific settings (in `.code-workspace` files) will override these global settings
- You can always revert by removing these settings from your user `settings.json`
