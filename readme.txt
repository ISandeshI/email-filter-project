on the start of day:
STEP 1 — Open terminal in:
C:\Users\Indra\Downloads\Python Automation\email_filter_project

--------------------------------------------------------------------------------------
Activate Python Virtual Environment: Run
.\venv\Scripts\activate

--------------------------------------------------------------------------------------

After activation you will see:

(venv) at beginning of terminal.

--------------------------------------------------------------------------------------

Run:

python -m uvicorn app.main:app --reload

Backend will run, check this in browser: http://127.0.0.1:8000

--------------------------------------------------------------------------------------

Open SECOND TERMINAL

IMPORTANT: Backend and frontend should run in separate terminals.

Run:
cd frontend

--------------------------------------------------------------------------------------

npm run dev

Frontend will run, check this in browser: http://localhost:5173

-----------------------------------------------------------------------------------------------


you have to activate celery

in separate terminal open and run:
.\venv\Scripts\Activate.ps1
celery -A app.celery_worker worker --loglevel=info --pool=solo




