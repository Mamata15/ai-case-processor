# AI Customer Complaint & Case Processing System

This project processes customer complaint documents in `data/` and performs three
separate GenAI stages for each document:

1. Extract structured complaint information into a Pydantic model.
2. Generate a professional customer email from that structured data.
3. Generate a concise internal management case summary.

The batch continues when an individual file cannot be read or processed. Outputs
are written to `output/structured_data/`, `output/customer_emails/`,
`output/case_summaries/`, and `output/final_report.csv`.

## Technology

- Python 3.10+
- Pydantic for structured validation
- OpenAI or Gemini for JSON-generating LLM calls
- PyPDF2 and python-docx for document parsing
- pandas for the consolidated report
- python-dotenv for configuration
- Python `logging` for basic operational logs

## Setup

### Conda on macOS

This is the recommended setup for this project:

```bash
conda create -n ai-case-processor-py310 python=3.10 -y
conda activate ai-case-processor-py310
python --version
pip install -r requirements.txt
cp .env.example .env
```

The version check should show Python 3.10 or newer. In VS Code, use **Python:
Select Interpreter** and choose `ai-case-processor-py310` before running or
debugging the project.

### Standard virtual environment

If Python 3.10+ is installed independently, use:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set one provider and its API key in `.env`:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_key_here
```

For Gemini, use `LLM_PROVIDER=gemini`, set `GEMINI_API_KEY`, and choose an
available Gemini model such as `gemini-3.6-flash`. API keys are never committed
because `.env` is ignored.

## Optional Email Delivery

By default, the system only saves generated emails under
`output/customer_emails/`. To send them through an SMTP server, configure these
settings in `.env`:

```env
SEND_EMAILS=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SENDER_EMAIL=support@example.com
SMTP_USE_TLS=true
```

Set `SENDER_EMAIL` to the support or organization address that should appear in
the generated email preview as `From`. The customer `To` address is extracted
from each complaint document. You can set `SENDER_EMAIL` now and leave
`SEND_EMAILS=false` while reviewing generated messages; no email is sent in
that mode.

When enabled, the workflow sends each email to the address extracted from its
source document. Cases without an email address fail safely for that document
and are recorded in `final_report.csv`. Use a test mailbox during development;
the default `SEND_EMAILS=false` prevents accidental delivery.

## Run

Place `.txt`, `.pdf`, or `.docx` complaint documents in `data/`, then run. The
repository includes sample inputs in all three supported formats:

- `.txt`: `complaint_001` through `complaint_005`
- `.docx`: `complaint_006_delivery.docx`
- `.pdf`: `complaint_007_billing.pdf`

```bash
conda activate ai-case-processor-py310
python run.py
```

The generated JSON, emails, summaries, CSV report, and `processing.log` appear
under `output/`.

## Project Structure

```text
src/
  document_reader.py    TXT/PDF/DOCX ingestion and file-level errors
  extraction.py         structured complaint extraction
  response_generator.py customer email generation
  email_sender.py       optional SMTP delivery
  case_summary.py       internal summary generation
  batch_processor.py    orchestration and output persistence
  llm_client.py         OpenAI/Gemini provider boundary
  models.py             Pydantic schemas
  config.py             environment-driven settings
```

Extraction must complete before email and summary generation because both consume
the validated case model. Email and summary generation are independent after
extraction and could be parallelized with `ThreadPoolExecutor` in a later version.

## Example Output

`output/structured_data/complaint_001_refund.json` contains fields such as:

```json
{
  "customer_name": "Priya Menon",
  "complaint_category": "Refund",
  "issue_description": "Refund for order 45821 has not appeared.",
  "is_complaint": true,
  "case_status": "Open"
}
```

The final CSV combines the source filename, all extracted fields, and any
processing error. A failed file does not stop other documents from completing.

## Tests

```bash
.venv/bin/python -m pytest -q
```

Tests use fake LLM clients, so they do not require an API key or make network
requests.

## Design Decisions and Limitations

- Provider-specific SDK calls are isolated in `llm_client.py`.
- LLM responses are parsed as JSON and validated by Pydantic before being saved.
- Prompts explicitly prohibit inventing customer information, dates, amounts, or
  actions that are absent from the source.
- This version requires an OpenAI or Gemini API key for actual processing; it does
  not include a local LLM runtime.
- Scanned PDFs without an embedded text layer require OCR, which is outside the
  current scope.