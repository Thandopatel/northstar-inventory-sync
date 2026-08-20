# Learning & Blocker Journal

> Fill this in as you actually work through Days 1–2 (and beyond).
> Real timestamps, real dead ends — this is the evidence of your own
> troubleshooting process, not a summary written after the fact.

## Tool assigned
- **Tool/concept**Tool/concept:** Webhook verification
- **Prior familiarity:**  _No prior knowledge
- **Time-box:** _(4 hours for Days 1–2)_

## Log
Add one entry per blocker or learning moment, in the order they happened.

### Entry 1
- **Time:**19 August 2026, 14:35
- **What I was trying to do **I was trying to understand how the inventory sync service would work and how a webhook could be used to send stock changes to my application instead of relying only on repeatedly checking the warehouse API.
- **What broke / what I didn't understand:**I initially understood the webhook as simply an API endpoint that receives information, but I did not understand how the application could determine whether the incoming request was actually from the warehouse system and not just a random request.
- **What I tried:**I broke the problem down into smaller parts. I looked at the difference between a normal API request and a webhook request, then worked through the idea of a webhook endpoint receiving a payload. I also tried to connect this to the Northstar inventory requirement, where stock information needs to remain accurate.
- **Outcome:**I understood that receiving the webhook is only one part of the problem. I also need to verify the request before trusting the stock update. This helped me understand why webhook verification is important for an inventory system.

### Entry 2
- **Time:**19 August 2026, later in the afternoon
- **What I was trying to do:**I was trying to translate what I had learned into something that could actually fit into the Northstar inventory-sync prototype, rather than just understanding the concept theoretically.
- **What broke / what I didn't understand:**I became stuck on how the pieces should fit together. I was thinking about the frontend, backend, inventory data and webhook as separate pieces instead of thinking about the complete flow from a stock change to the support tool receiving the updated information.
- **What I tried:**I mapped the process out conceptually: warehouse/inventory system → webhook request → verification → update inventory data → support tool queries the current stock. I also compared this with the original Northstar requirement, which initially uses polling and caching. The assignment later requires the team to replace polling with a webhook push model, so understanding this early was useful
- **Outcome:**I had a clearer picture of the architecture. The biggest learning was that I should focus on the data flow first instead of immediately trying to write all the code. I also realised that security/verification cannot be treated as an extra step after the prototype is finished.
### Entry 3
- **Time:**19 August 2026, later in the evening 
- **What I was trying to do:**I was trying to organise the prototype work and make sure that the work I produced could eventually be placed
- **What broke / what I didn't understand:**I was still getting used to how the technical work, documentation and GitHub evidence needed to connect. I initially thought getting the code working was the main goal, but the assignment also requires evidence of troubleshooting and time-to-completion.
- **What I tried:**I worked through the project structure and thought about what would need to be committed and documented. From my earlier Northstar work, I also learned that GitHub work needs to be organised rather than simply uploading files without explaining what changed.
- **Outcome:**I realised that the prototype and the learning journal need to tell the same story. My commits, documentation and troubleshooting notes should show what I actually attempted, what failed, and how I corrected it.
Entry 4
- **Time:**19 August 2026, later in the afternoon
- **What I was trying to do:**I was trying to get more comfortable with the backend side of the inventory-sync problem because my previous experience has been stronger with general computer applications and documentation than with building backend services from scratch
- **What broke / what I didn't understand:**initially found it difficult to know which part I should build first. There were several concepts involved—API requests, inventory data, the backend, the frontend and eventually webhook communication.
- **What I tried:**Instead of trying to build everything at once, I separated the problem into smaller pieces and focused on understanding the purpose of each component before connecting them.
- **Outcome:**This reduced the confusion. I learned that when I do not understand a technical system, breaking it into smaller flows is more effective than trying to solve the whole application at once.

Entry 5
- **Time:**19 August 2026, 6:05 PM
- **What I was trying to do:**Launch the FastAPI backend server using Uvicorn and run the project prototype.
- **What broke / what I didn't understand:** Running py -m uvicorn backend.main:app --reload resulted in a ModuleNotFoundError: No module named 'backend' error, followed by syntax errors when attempting to run Python import statements directly inside the PowerShell terminal prompt.
- **What I tried:** I executed python code inside the terminal instead of shell commands, and attempted relative vs. package-level imports across main.py, models.py, inventory.py, and webhook.py.
- **Outcome:**Identified that running Uvicorn from the root folder requires consistent absolute package imports (from backend import ...). Fixed all relative import paths in models.py (from backend.database import Base) and inventory.py, and added missing response models (WebhookResponse, StockCheckResponse) to webhook.py. The server started successfully on [http://127.0.0.1:8000](http://127.0.0.1:8000).
<!-- Add more entries as needed -->I should have broken down this task in a matter of two days however due to personal reasons i had to do all of this work on one day.

Entry 6
- **Time:**19 August 2026, 6:35 PM
- **What I was trying to do:** Connect the HTML/JS frontend dashboard to the FastAPI backend and view the live working prototype in the browser.
- **What broke / what I didn't understand:**Opening index.html directly via the file system (file:///...) blocked API fetch calls to the backend running on [http://127.0.0.1:8000](http://127.0.0.1:8000) due to CORS rules and browser security restrictions.
- **What I tried:** Enabled CORSMiddleware inside backend/main.py allowing all origins, created dedicated index.html, style.css, and script.js files inside the frontend/ folder, and served the frontend via a local HTTP server (py -m http.server 5500).
- **Outcome:**  The frontend successfully connected to the backend. Form submissions sent live webhook inventory updates (POST /api/v1/webhooks/inventory) and queried stock levels (GET /api/v1/stock/{sku}) with real-time UI updates. All updated code was committed and pushed to GitHub via Git.
## Time-box vs. actual time
- **Planned:**4 hours across Days 1–2.
- **Actual:**Approximately 4 hours of active work, with additional time spent thinking through the architecture and troubleshooting.
- **Reflection:**The biggest lesson for me was that I should not expect to understand a completely unfamiliar technical concept immediately. I initially wanted to get straight to the code, but I realised that I needed to understand the flow first. I also learned that getting stuck is part of the process, as long as I record what I tried and what I learned from it. The exercise made me more comfortable with troubleshooting independently rather than immediately asking someone else for the answer. I still need to improve my confidence with backend development and webhook implementation, but I now have a better understanding of how the concept connects to the Northstar inventory-sync requirement.

Day 3
**Entry 7**
**What I was trying to do:**
Implement the original Day 3 polling specification:

Build a background poller that fetches inventory from a warehouse API every 5 minutes

Create a mock warehouse client (since there's no real API to test against)

Cache the stock data in a shared database

Expose a GET /api/v1/stock query endpoint

Make sure the poller and existing webhook both write to the same cache

Write tests to verify everything works
**What broke/What i didnt understand**
Problem 1: Python command not found

When I tried to run python --version, I got "python was not found"

I didn't understand why Python wasn't recognized even though it was installed

Problem 2: Uvicorn not recognized

After creating all files, uvicorn command wasn't found

I didn't understand the difference between python and py on Windows

Problem 3: SQLAlchemy compatibility with Python 3.14

I got an error: AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly...

I didn't understand that Python 3.14 is brand new and some packages aren't fully compatible yet

Problem 4: Import errors

ImportError: cannot import name 'sync_stock_item' from 'backend.inventory'

ImportError: cannot import name 'get_db_connection' from 'backend.database'

I didn't realize my files were empty or missing the required functions

Problem 5: Folder structure confusion

I had multiple inventory.py and database.py files in different folders

I wasn't sure which files were being used
**What i tried**
Fix 1: Used py instead of python

Found out py is the Python launcher on Windows

Used py --version and it worked!

Installed packages with py -m pip install

Fix 2: Updated SQLAlchemy

Ran py -m pip install --upgrade sqlalchemy

Upgraded from version 2.0.52 to 2.0.35 (downgraded to a stable version)

Fix 3: Wrote the missing functions

Added sync_stock_item() to inventory.py

Added get_db_connection() to database.py

Made sure each file had the correct code

Fix 4: Created __init__.py

Added __init__.py in the backend folder to make it a Python package

This fixed the import issues

Fix 5: Cleaned up the folder structure

Made sure the correct database.py was in the backend folder

Deleted duplicate files in wrong locations

Fix 6: Wrote comprehensive tests

Created tests/test_api_client.py with 7 tests

Ran py -m pytest tests/ -v to verify everything

Got 7 passed tests (with 203 deprecat
**Outcome**
What I achieved:

Poller runs every 5 minutes - Successfully polls the mock warehouse

Inventory is cached in SQLite - Data is stored in inventory.db

Query endpoint works - GET /api/v1/stock returns all cached inventory

Manual poll trigger - POST /api/v1/poll-now forces an immediate poll

All 7 tests pass - Proves the API client works correctly

Shared cache - Both webhook and poller use the same sync_stock_item() function
**Planned:** 2hour
- **Actual:**1.49 
- **Reflection:** The biggest lesson for me today was that technical problems often have simple solutions once you understand what's actually going wrong. When I got errors like "python was not found" or "cannot import name," I initially felt stuck and frustrated. But by breaking each problem down, trying different solutions, and asking for help when needed, I was able to solve every issue.

I learned several practical things today:

On Windows, use py instead of python - This simple fix solved most of my command issues

Python 3.14 is brand new - Some packages (like SQLAlchemy) need updates or downgrades to work properly

__init__.py files matter - They tell Python that a folder is a package that can be imported

VS Code's Problems tab is helpful - It showed me exactly which functions were missing

Tests give confidence - Seeing "7 passed" was reassuring and proved my code actually works

The exercise made me more comfortable with troubleshooting independently. Instead of immediately asking for help, I started reading error messages more carefully, checking my files, and trying logical solutions. I still need to improve my confidence with backend development, but I now have a much better understanding of how the poller, warehouse client, and cache work together.

I was surprised by how many small things could break (Python path issues, missing functions, import errors), but I learned that each error teaches you something valuable. The process of getting stuck, trying things, and eventually solving the problem is actually how you learn best.


