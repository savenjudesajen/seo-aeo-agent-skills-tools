# Taking control of the screen (desktop crawler UI)

## When to use the screen

Use the desktop UI only for what no tool or command line does:
- Mode > List and Upload > From a File, when your automation cannot start a list crawl
- Config > API Access screens (connect accounts, pick property and data stream)
- Request API Data, Crawl Analysis > Start
- Opening a menu or dropdown (background clicks often cannot)

Everything else goes through the crawler's automation (MCP server or command line) and the shell:
starting crawls, reading progress, exports and writing files.

## When not to use it

- While the user is running a crawl in the same window. Read progress only and wait.
- To type long text. Write a file and pick it through the dialog.

## Access flow

1. Say what you are about to do and why before taking control.
2. Request access to the app through your desktop-control tool, then full-screen control when menus are
   needed. Wait for the user's approval each time.
3. Clipboard write may not be granted. Use the file picker for uploads: in the macOS open dialog press
   Cmd+Shift+G, type the path, Enter.
4. Large, scaled screens: zoom into a region before reading small text or clicking a small button, and
   convert zoom coordinates back to screen coordinates (region origin plus zoom position times region
   width over zoom width).
5. Dialogs need focus: the first click on an inactive dialog may do nothing. Click the dialog title, then
   the button.
6. Take a screenshot after every state-changing click. Verify Connected, Completed 100 percent or the row
   count before moving on.
7. Release control when the UI steps are done.

## Rules

- Never click browser dialogs or consent prompts the user has not approved.
- A blocked data source (not signed in, key missing) is a stop-and-report moment. Say what is blocked and
  what is needed.
- Do not start, clear or modify a crawl the user started.
