# Healthcare Product Launch – Income & Spending Survey

**Author:** Brittney Everson  
**Program:** Nexford University – Master of Science in Data Analytics  
**Assignment:** Final Project

A survey tool that collects participants' age, gender, total income and spending, stores it in MongoDB, exports it to CSV through a Python `User` class, and analyzes it in a Jupyter notebook. The charts are exported for a client PowerPoint. The Flask app is hosted on AWS EC2.

**Live app on AWS:** `http://<YOUR-EC2-PUBLIC-IP>`  ← replace with your EC2 address after deploying

---

## Requirement checklist

| # | Requirement | Where it is |
|---|---|---|
| 1 | Flask webpage to collect user data | `app.py`, `templates/index.html` |
| 2 | Store Age, Gender, Total Income and Expenses in MongoDB | `app.py` → `db.py` (collection `participants`) |
| 2 | Checkboxes for utilities, entertainment, school fees, shopping, healthcare, each with an amount textbox | `templates/index.html`, `static/form.js` |
| 3 | Python class named `User` | `user.py` |
| 3 | Loop through collected data and store it in a CSV file | `export_to_csv.py` → `data/survey_data.csv` |
| 3 | Load the CSV into a Jupyter notebook | `analysis/survey_analysis.ipynb` |
| 4 | Show the ages with the highest income | Notebook charts 1 and 2 |
| 4 | Show gender distribution across spending categories | Notebook charts 3 and 4 |
| 4 | Export charts for a client PowerPoint | `charts/*.png` and `presentation/Client_Spending_Insights.pptx` |
| 5 | Host the Flask app on AWS | `deploy/` folder + "Deploy to AWS" below |
| – | README with instructions | This file |

---

## Project structure

```
healthcare-spending-survey/
├── app.py                  # Flask app: survey form, validation, save to MongoDB
├── db.py                   # MongoDB connection (reads MONGO_URI from .env)
├── user.py                 # User class used by the app and the CSV export
├── export_to_csv.py        # Loops through MongoDB, writes data/survey_data.csv
├── seed_sample_data.py     # Optional: adds sample participants for testing
├── requirements.txt
├── .env.example            # Copy to .env and add your own settings
├── templates/              # index.html (form), thank_you.html
├── static/                 # style.css, form.js
├── data/survey_data.csv    # Exported data used by the notebook
├── analysis/survey_analysis.ipynb
├── charts/                 # PNG charts + summary tables for the client
├── presentation/Client_Spending_Insights.pptx
├── deploy/                 # AWS EC2 setup script, Gunicorn service, Nginx config
└── tests/test_app.py       # Automated tests (no database needed)
```

---

## How the data flows

1. A participant fills in the form at `/`.
2. `app.py` builds a `User` object, checks it (age 18–100, valid gender, no negative amounts, every ticked box has an amount) and saves it to MongoDB. Unticked categories are saved as 0.
3. `export_to_csv.py` loops through every MongoDB document, turns each one into a `User`, and writes one CSV row per participant.
4. The notebook loads the CSV, builds the charts and saves them to `charts/`.

Example MongoDB document:

```json
{
  "age": 34,
  "gender": "Female",
  "total_income": 5200.0,
  "expenses": {"utilities": 300.0, "entertainment": 0, "school_fees": 0, "shopping": 220.0, "healthcare": 150.0},
  "submitted_at": "2026-10-27T09:15:00Z"
}
```

CSV columns: `user_id, age, gender, total_income, utilities, entertainment, school_fees, shopping, healthcare, total_expenses, spending_ratio, submitted_at`

---

## Run it locally

**Requirements:** Python 3.10+ and a MongoDB database (a free MongoDB Atlas cluster or MongoDB installed on your computer).

```bash
# 1. Get the code
git clone <your-repo-url>
cd healthcare-spending-survey

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install packages
pip install -r requirements.txt

# 4. Add your settings
cp .env.example .env              # Windows: copy .env.example .env
# open .env and paste your MongoDB connection string into MONGO_URI

# 5. Start the app
python app.py
```

Open http://127.0.0.1:5000 and submit a few responses.

**No database yet?** Set `MONGO_URI=mongomock://localhost` in `.env` to use a temporary in-memory database. Data disappears when the app stops, so use this only for a quick look.

---

## Export the data to CSV

```bash
python export_to_csv.py
# Exported 200 participants to data/survey_data.csv
```

Optional – add sample participants first so the charts have enough data:

```bash
python seed_sample_data.py --n 200
python export_to_csv.py
```

---

## Run the analysis notebook

```bash
cd analysis
jupyter notebook survey_analysis.ipynb
```

Run all cells (Kernel → Restart & Run All). The notebook:

- loads `data/survey_data.csv` and checks it for missing values
- **Chart 1:** top 10 ages by average monthly income
- **Chart 2:** average monthly income by age band
- **Chart 3:** number of participants spending in each category, by gender
- **Chart 4:** average monthly spend per category, by gender
- saves each chart as a 200 dpi PNG in `charts/`, ready to drop into PowerPoint

`presentation/Client_Spending_Insights.pptx` is a ready-made client deck with these results as editable PowerPoint charts.

---

## Run the tests

```bash
python -m pytest -q
```

The tests use an in-memory database, so nothing needs to be running. They check that the form loads, a valid response is saved, a ticked box with no amount is rejected, a bad age is rejected, and the CSV export loops through every record.

---

## Deploy to AWS (EC2 + MongoDB Atlas)

This setup uses the lowest-cost options: a small EC2 instance and the free MongoDB Atlas tier.

### Step 1 – Create the database (MongoDB Atlas)

1. Sign up at https://www.mongodb.com/cloud/atlas and create a **free (M0)** cluster.
2. **Database Access:** add a database user and password.
3. **Network Access:** add your EC2 instance's public IP (you will get it in Step 2). For a quick class demo you can use `0.0.0.0/0`, then remove it after grading.
4. **Connect → Drivers:** copy the connection string. This is your `MONGO_URI`.

### Step 2 – Launch the server (AWS EC2)

1. In the AWS Console open **EC2 → Launch instance**.
2. Name: `healthcare-survey`. Image: **Ubuntu Server 24.04 LTS**. Type: **t3.micro** (or t2.micro).
3. Create a key pair and download the `.pem` file.
4. **Security group:** allow **SSH (22)** from *My IP* and **HTTP (80)** from *Anywhere*.
5. Launch, then copy the instance's **Public IPv4 address**.

### Step 3 – Connect and set up

```bash
# From your computer
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>

# On the server
git clone <your-repo-url> healthcare-spending-survey
cd healthcare-spending-survey
cp .env.example .env
nano .env          # paste your Atlas MONGO_URI and a SECRET_KEY, then save (Ctrl+O, Enter, Ctrl+X)

bash deploy/setup_ec2.sh
```

The script installs Python and Nginx, creates a virtual environment, runs the app with Gunicorn as a background service, and points Nginx at it.

### Step 4 – Check it works

- Open `http://<EC2-PUBLIC-IP>` and submit a response.
- `http://<EC2-PUBLIC-IP>/health` should return `{"status": "ok"}`.
- In Atlas, **Browse Collections → healthcare_survey → participants** should show the new record.
- Update the **Live app** link at the top of this README.

### Useful server commands

```bash
sudo systemctl status survey        # is the app running?
sudo journalctl -u survey -n 50     # app logs
sudo systemctl restart survey       # restart after pulling new code
```

### Avoid charges

Stop or terminate the EC2 instance once your work is graded.

---

## Security notes

- Passwords and connection strings live only in `.env`, which is listed in `.gitignore` and never committed.
- All form input is checked on the server, not just in the browser.
- Jinja2 templates escape user input automatically.

---

## About the data in this repository

`data/survey_data.csv`, the charts and the deck were produced from 200 sample participants created by `seed_sample_data.py`. Sample records pass through the same `User` class and validation as real ones. Once real responses are collected on the live app, run `python export_to_csv.py` and re-run the notebook to refresh every chart.
