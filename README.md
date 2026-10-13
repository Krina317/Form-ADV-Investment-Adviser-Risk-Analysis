# Investment Adviser Risk & Compliance Analytics (SEC Form ADV)

**Course:** Data Analysis and Visualisation (DAV) · **Domain:** Finance – Financial Risk Analytics & Regulatory Compliance
**Tools:** Python (pandas) for data preparation · Tableau (3 dashboards) · ML plan (scikit-learn)

---

## 1. What is this project about?

Every investment adviser in the US that manages client money must register with the SEC (or a state) and file **Form ADV**. It is a public disclosure document in which the firm states:

- who it is (name, office, legal structure),
- how big it is (employees, assets under management, number of clients),
- what it does (financial planning, portfolio management, pension consulting, ...),
- how it charges (% of assets, hourly, commissions, performance fees, ...),
- whether it holds client money (**custody**), and
- whether it has a **disciplinary history** (Item 11: criminal, regulatory, SRO, civil/judicial events).

Separately, the SEC publishes **DRP (Disclosure Reporting Page)** records: one row per regulatory event with details such as who brought the action, the allegations, the sanction, and the fine.

**The project question:** *Do a firm's size, services, fees and custody arrangements relate to its regulatory disclosure/enforcement risk, and what does the regulatory landscape (who enforces, where, how severe, how fast) look like?*

The two goals are:

1. **Descriptive (Tableau):** show the enforcement landscape, the profile of advisers, and the outcomes and penalties of cases.
2. **Predictive / analytical (ML):** predict which firms are more likely to carry disclosures, and group firms into risk-relevant segments.

### Important caveat
A disclosure is **not proof of wrongdoing**. Item 11 captures events (including affiliates' events and old, resolved, minor ones). Any model built here is a *screening / prioritisation* tool, not a verdict on a firm.

---

## 2. Stakeholders and how the project helps them

| Stakeholder | What they need | How this project helps |
|---|---|---|
| **Investors / individuals choosing an adviser** | Is this adviser's profile unusual? Do firms like it tend to have disciplinary events? | Peer comparison, disclosure rates by firm type, due-diligence flags |
| **Institutional allocators, pension funds, consultants** | Manager due diligence at scale | Risk-score ranking of thousands of firms; cluster profiles |
| **Regulators (SEC, state securities regulators, FINRA)** | Where to point limited examination resources | Which firm types, regions and services concentrate events; enforcement trends and who is most active |
| **Advisory firms' compliance officers** | Benchmarking against peers; early-warning on risky practices | Compare own profile (fees, custody, size) to peers with/without disclosures |
| **Custodians, platforms, insurers (E&O), M&A buyers of advisory firms** | Onboarding and underwriting risk | A transparent, data-based risk screen |
| **Academics, journalists, policy analysts** | Evidence on enforcement patterns | Sanction mix, penalty distribution, resolution time, geography |

---

## 3. Repository contents and how the data was built

```
dataset/                          (raw SEC bulk files, not included - too large)
  IA_ADV_Base_A_20111105_20241231.csv     firm-level filing data (Items 1-11 ...)
  IA_ADV_Base_B_20111105_20241231.csv     Schedule D / org structure (Item 3 ...)
  IA_DRP_Regulatory_20210101_20241231.csv regulatory disciplinary events

filter_adv.py        Step 1  keep filings submitted in 2023-2024 (Base A) and the matching Base B rows
final_select.py      Step 2  pick ~50 useful columns, give readable names, merge A+B on FilingID
                             -> adv_final_trimmed.csv        (84,620 rows x 52 cols)
process_drp.py       Step 3  pick/rename DRP columns, keep events initiated in 2023-2024
                             -> drp_regulatory_2023_2024.csv (8,834 rows x 21 cols)
rename_columns.py    (earlier iteration - renames everything; superseded by final_select.py)
select_columns.py    (earlier iteration - older, smaller column list; superseded by final_select.py)
formADVriskanalysis.twb   Tableau workbook (3 dashboards, 19 sheets)
Summary_1.pages           Practical 1 report (domain overview and applications)
```

**Run order:** `filter_adv.py` → `final_select.py` → `process_drp.py` (the DRP step is independent of the first two).

**Housekeeping suggestions**
- The scripts have hard-coded `/Users/krinashah/...` paths. Put a single `BASE_DIR` at the top (or use `pathlib` and relative paths) so a teammate or examiner can run them.
- `rename_columns.py` and `select_columns.py` can be moved to an `archive/` folder; `final_select.py` replaces them (and it overwrites the same output file).
- `final_select.py` already prints a `missing_a` list. Keep it, because it is your check that a column code really exists in the source file.

**Tableau data model:** the two CSVs are connected with a **relationship on `FilingID`** (not a physical join). That is why the workbook uses `COUNTD(EventID)` and `COUNTD(FilingID)`: counts are computed per table at the level of the sheet.

---

## 4. The datasets in detail

### 4.0 Size and grain (read this first)

| | `adv_final_trimmed.csv` | `drp_regulatory_2023_2024.csv` |
|---|---|---|
| Rows × columns | 84,620 × 52 | 8,834 × 21 |
| **Grain (one row =)** | one **filing** (an annual or other amendment) | one event **as reported in one filing** |
| Distinct entities | **17,703 firms** (`CRD_Number`), ~4.8 filings per firm (median 4, max 271) | **3,840 distinct events** (`EventID`) in **2,317 filings** (2.7% of ADV filings) |
| Time | `DateSubmitted` 2023-01-03 → 2024-12-31 (42,036 filings in 2023; 42,584 in 2024) | `DateInitiated` in 2023 (6,307 rows) and 2024 (2,527 rows) |
| Key | `FilingID` | `FilingID` (all 8,834 rows match an ADV filing), `EventID` |

> Because a firm files several times and an event is repeated in every filing that reports it, **never use a plain row count**. Use `COUNTD(CRD_Number)` for firms and `COUNTD(EventID)` for events. For ML, reduce to one row per firm (see section 6).

### 4.1 `adv_final_trimmed.csv` – every column

Values: `Y/N` flags are strings. "Missing" is the share of empty cells.

#### Identity and location
| Column | Meaning | Data / values | Why it matters |
|---|---|---|---|
| `FilingID` | Unique ID of the filing | integer, 84,620 unique | Join key to DRP |
| `DateSubmitted` | When the filing was submitted | timestamp (saved as text; parse with `pd.to_datetime`) | Time trends; pick the latest filing per firm |
| `LegalName` | Registered legal name (Item 1A) | text, 18,305 unique | Display / lookup. Names change, so identify firms by CRD |
| `BusinessName_Primary` | "Doing business as" name (1B1) | text, 18,430 unique | Display only |
| `CRD_Number` | Central Registration Depository number, the firm's permanent ID (1E1) | integer, 17,703 unique | **The correct firm identifier**; use it for grouping and train/test splits |
| `Office_City` | Principal office city | text, 2,197 unique, 6.2% missing | Geography |
| `Office_State` | Principal office state | 53 values (NY 12,371, CA 9,301, FL 5,146, TX 5,092 ...), 11% missing (non-US firms have none) | State-level map and regional risk |
| `Office_Country` | Principal office country | 63 values, 89% United States, then UK, Canada, Hong Kong, Switzerland | Global map; domestic vs foreign |
| `Office_Postal` | Postal code | text, 6.7% missing | Fine geography (not used yet) |
| `OrgForm` | Legal structure (Item 3A) | LLC 65%, Corporation 25%, LP 6.7%, Other 1.7%, LLP 0.9%, Sole proprietorship 0.3%, Partnership 0.2% | Liability and complexity of the firm |
| `StateOfOrg` | State where incorporated | 53 values, 4.6% missing | Often Delaware for larger firms |
| `CountryOfOrg` | Country where organised | 59 values | Foreign-affiliated firms |
| `HasWebsite_Flag` | Firm reports a website (1I) | Y 92% / N 8% | Weak transparency signal |

#### Size
| Column | Meaning | Data / distribution | Why it matters |
|---|---|---|---|
| `NumEmployees` | Total employees (5A) | integer; median 10, mean 192, max 36,687 (**heavy right tail**) | **Strongest simple predictor of disclosures** in a baseline (bigger firm → more chances for an event). Use `log1p` |
| `NumEmployees_Advisory` | Employees performing advisory functions (5B1) | integer; median 6, max 27,045 | Advisory share = `Advisory / Total` is a useful ratio |
| `HasRegulatoryAUM_Flag` | Firm reports "regulatory assets under management" (5F1) | Y 96.9% / N 3.1% | When `N`, all AUM fields are empty |
| `Discretionary_AUM` | USD managed with discretion (5F2a) | float; median $363M, mean $13.5B, max $11.5T; 3.1% missing | Discretion = more control over client money |
| `NonDiscretionary_AUM` | USD managed without discretion (5F2b) | float; median $0 (75% of firms have none) | |
| `Total_AUM_USD` | Total regulatory AUM (5F2c) | float; median $428M, mean $15.9B; 3.1% missing | **Primary size measure.** Always `log1p` or bucket it |
| `Total_NumAccounts` | **See data-quality issue D1 below: this column does not hold account counts** | float, values up to 1.26 × 10¹² | Fix before using |
| `NumClients_Bucket` | Number-of-clients range (5H) | `0`, `1-10`, `11-25`, `26-50`, `51-100`, `101-250`, `251-500`, `More than 500`; **37% missing** | Ordinal; treat "missing" as its own category |

#### Services offered (Item 5G; Y/N, a firm can tick several)
| Column | Share Y | Meaning |
|---|---|---|
| `Service_FinancialPlanning` | 51.9% | Financial planning |
| `Service_PortfolioMgmt_Individuals` | 70.7% | Portfolio management for individuals/small businesses |
| `Service_PortfolioMgmt_InvestmentCompanies` | 9.6% | ... for investment companies (mutual funds) |
| `Service_PortfolioMgmt_PooledVehicles` | 34.4% | ... for pooled vehicles (hedge/private funds) |
| `Service_PortfolioMgmt_Businesses` | 41.9% | ... for businesses/institutions |
| `Service_PensionConsulting` | 25.9% | Pension consulting |
| `Service_SelectionOfOtherAdvisers` | 36.5% | Selecting other advisers |
| `Service_Publications` | 6.1% | Periodicals / newsletters |
| `Service_SecurityRatings` | 0.2% | Security ratings or pricing |
| `Service_MarketTiming` | 0.3% | Market timing |
| `Service_EducationalSeminars` | 13.0% | Seminars / workshops |
| `Service_Other` | 17.7% | Other |

*Significance:* the service mix describes the business model. Fund managers (pooled vehicles) face different risks from retail planners. `SecurityRatings` and `MarketTiming` are almost always `N`; drop or merge them for ML.

#### Fee structure (Item 5E; Y/N, can tick several)
| Column | Share Y | Meaning as currently labelled |
|---|---|---|
| `Fee_PercentAUM` | 95.6% | Percentage of assets under management |
| `Fee_Hourly` | 34.3% | Hourly charges |
| `Fee_FixedFee` | 1.6% | Labelled "fixed fee" **(see D2: probably subscription fees)** |
| `Fee_Commission` | 51.7% | Labelled "commission" **(see D2: probably fixed fees)** |
| `Fee_PerformanceBased` | 3.3% | Labelled "performance-based" **(see D2: probably commissions)** |
| `Fee_Other` | 15.8% | Other |

*Significance:* the fee model creates conflicts of interest (commissions and performance fees are the classic ones) and so is a natural risk feature.

#### Custody (Item 9A)
| Column | Share Y | Meaning |
|---|---|---|
| `Custody_ClientFunds_Flag` | 46.2% | Firm has custody of client **cash** |
| `Custody_ClientSecurities_Flag` | 40.9% | Firm has custody of client **securities** |

*Significance:* custody is the highest-risk operational privilege (misappropriation risk), which is why the SEC has a dedicated Custody Rule.

#### Disclosure flags (Item 11, the regulatory history; Y/N)
| Column | Share Y (filings) | As currently labelled |
|---|---|---|
| `HasDisclosure_Overall_Flag` | **8.0%** | Overall "has disclosure" flag. **See D3: not fully consistent with the detail columns** |
| `Disclosure_CriminalFelony_Firm` | 0.9% | Felony (firm) |
| `Disclosure_CriminalFelony_Affiliate` | 1.8% | Felony (affiliate) |
| `Disclosure_CriminalMisdemeanor_Firm` | 0.7% | Misdemeanor (firm) |
| `Disclosure_CriminalMisdemeanor_Affiliate` | 0.6% | Misdemeanor (affiliate) |
| `Disclosure_RegulatoryAction1` | 3.1% | SEC/CFTC regulatory action |
| `Disclosure_RegulatoryAction2` | 7.2% | SEC/CFTC regulatory action (second question) |
| `Disclosure_SROAction1` | 3.3% | Self-regulatory organisation action |
| `Disclosure_CivilJudicial1` | 1.2% | Civil / judicial action |
| `Disclosure_Bankruptcy_Flag` | 0.8% | Bankruptcy |
| `Disclosure_Bond_Flag` | 1.7% | Bond / surety |

*Significance:* these are the **risk outcome** of the project. Item 11 is self-reported by the firm under penalty of law, so it is a good proxy for "has a disciplinary history", but see D3 and D4 for labelling caveats.

### 4.2 `drp_regulatory_2023_2024.csv` – every column

| Column | Meaning | Data / values | Why it matters |
|---|---|---|---|
| `FilingID` | Filing that reported the event | int; links to ADV | Join key |
| `EventID` | Event reference ID (from `ReferenceID`) | int; 3,840 distinct among 8,834 rows | **Use `COUNTD(EventID)`**, the same event repeats across filings |
| `Initiator_Type` | Kind of authority | SRO 3,010 · State 1,684 · Foreign 1,492 · SEC 1,357 · Other Federal 1,037; 2.9% missing | Who polices advisers |
| `Initiated_By` | Name of the authority | text; top: SEC, FINRA, Bloomberg SEF, CFTC, CFPB, CME Group... **same body appears under several spellings** (see D6) | Leading regulators chart |
| `Principal_Sanction` | Main penalty | Civil/administrative penalty or fine 5,143 (58%) · Cease & Desist 1,283 · Censure 716 · Other 640 · Reprimand 212 · Suspension 54 · Undertaking 52 · Restitution 19 · Disgorgement 18 · Revocation 11 · Bar 10; 7.6% missing | Severity ladder |
| `Other_Sanctions` | Free-text secondary sanctions | 67.6% missing | Low value |
| `DateInitiated` | When the action began | date; 2023 and 2024 only (by construction) | Time trend; start of resolution clock |
| `CaseNumber` | Regulator's case number | text, 7.4% missing | Lookup only |
| `Allegations` | What the firm was accused of | free text (upper case) | NLP opportunity: topic of misconduct |
| `Status` | Case status | By distinct event: Final 3,154 (82%) · Pending 355 · On Appeal 51 · missing 280 (rows: 8,081 / 414 / 59) | Only final cases have reliable penalties and resolution times |
| `Resolution` | How it ended | Order 2,466 · Consent 1,978 · AWC 1,608 · Other 718 · Settled 567 · Decision 545 · ...; 7.8% missing | Settled vs imposed |
| `ResolutionDate` | Date resolved | date; 7.8% missing | Resolution time |
| `HasMonetarySanction_Flag` | Was there a fine? | Y 7,569 · N 1,048 | Filter for penalty analysis |
| `MonetaryAmount` | Fine in USD | float; **median $164K, mean $13.9M, max $1.3B**, 14% missing | Extremely skewed; use median/log scale |
| `Sanction_Revocation` / `_Bar` / `_Suspension` | Flags for the most severe sanctions | Y: 22 / 13 / 68 (60%+ blank) | Rare; only useful as a combined "severe sanction" flag |
| `Sanction_Censure` | Censure flag | Y 3,575 | |
| `Sanction_Disgorgement` | Disgorgement/restitution flag | Y 1,250 | Investor-harm indicator |
| `Sanction_CeaseDesist` | Cease & desist / injunction flag | Y 2,841 | |
| `Summary` | Narrative of the event | free text, 11% missing | NLP; longer than Allegations |

---

## 6. Machine learning plan

### 6.1 What is Y?

You have several valid targets; pick **one primary** and keep the others as extensions.

| # | Task | Y (target) | Unit of analysis | Type | Comment |
|---|---|---|---|---|---|
| **A (primary)** | **Disclosure-risk classification** | `Y = 1` if the firm has an Item 11 disclosure (`HasDisclosure_Overall_Flag == 'Y'`, or your derived `any_disclosure`, see D3) | one row per firm (latest filing) | Binary classification | Matches your report's goal. ~5.3% positives at firm level → **imbalanced** |
| B | Enforcement-event prediction | `Y = 1` if the firm has ≥1 DRP event in 2023-24 (join on `FilingID`/`CRD`) | firm | Binary classification | Even rarer (2.7% of filings); a harder, more "hard-outcome" label |
| C | Penalty severity | `Y = log1p(MonetaryAmount)` or `Y = penalty ≥ $1M` | one row per distinct event | Regression / classification | Uses DRP features + firm features (via join) |
| D | Sanction type | `Y = Principal_Sanction` grouped (Penalty / Cease & Desist / Censure-Reprimand / Other) | event | Multiclass | Good for the "what happens when…" story |
| E | Firm segmentation | none | firm | **Unsupervised** clustering | Your "cluster advisers by business characteristics" application |
| F | Allegation themes | none | event | NLP / topic modelling | Cluster `Allegations` + `Summary` text |

### 6.2 Features (X) for the primary task A

Keep (after cleaning): `log1p(Total_AUM_USD)`, `log1p(Discretionary_AUM)`, `log1p(NonDiscretionary_AUM)`, `log1p(NumEmployees)`, `log1p(NumEmployees_Advisory)`, advisory share, AUM per employee, `NumClients_Bucket` (ordinal + missing flag), all `Service_*` flags and a `num_services` count, all `Fee_*` flags and `num_fee_types`, both custody flags, `OrgForm`, US-vs-foreign, `Office_State` (grouped or target-encoded; many levels), `HasWebsite_Flag`, `HasRegulatoryAUM_Flag`, an `aum_missing` indicator.

**Do NOT include (leakage):** any `Disclosure_*` column, `HasDisclosure_Overall_Flag` (that is Y), anything from the DRP table, and identifiers (`FilingID`, `CRD_Number`, names, postal code).

### 6.3 Method

1. **Collapse to firm level** (latest filing per `CRD_Number`), or keep filings but split by firm.
2. **Split by firm, never by row**: a firm has ~5 near-identical filings; a random row split puts the same firm in train and test and inflates scores. Use `GroupShuffleSplit` / `StratifiedGroupKFold` with `groups=CRD_Number`.
3. **Baselines:** Logistic Regression (scaled, `class_weight='balanced'`) → Random Forest → Gradient Boosting (HistGradientBoosting / XGBoost / LightGBM).
4. **Imbalance:** class weights first; SMOTE only inside cross-validation folds if used at all.
5. **Metrics:** **PR-AUC (average precision)**, ROC-AUC, recall and precision at the top 5/10% of ranked firms, F2. **Do not report accuracy**: predicting "no disclosure" for everyone is 94.7% accurate.
6. **Explainability:** permutation importance and SHAP, plus a partial-dependence plot on firm size. This is what regulators and due-diligence users will actually ask for.
7. **Unsupervised:** log-transform and scale the numerical features, run K-Means / Gaussian Mixture (choose *k* with silhouette and elbow), visualise with PCA or UMAP, then **profile each cluster** (size, fee model, services, custody, disclosure rate). A cluster with a high disclosure rate becomes a "higher-risk business model".

### 6.4 What results to expect (I ran a quick baseline)

On the firm-level table (17,703 firms, stratified 75/25 split, HistGradientBoosting, firm-level features only, no leakage):

| Metric | Value | Reading |
|---|---|---|
| Base rate of Y | 5.3% | |
| ROC-AUC | **0.72** | Moderate signal |
| PR-AUC | **0.275** | About **5× better than random** (random = 0.053) |
| Top driver | `NumEmployees` (by a wide margin), then advisory headcount, AUM, client bucket | Larger, more complex firms have more disclosures |

So the honest framing for your report: *firm profile alone gives a useful but moderate screening signal, dominated by size; fee type and custody add little on their own.* That is a valid finding. Do not over-claim causality.

---

## 7. Tableau work, dashboard by dashboard

The workbook has **3 dashboards and 19 worksheets**, built on one data source: `adv_final_trimmed.csv` related to `drp_regulatory_2023_2024.csv` on `FilingID`. Every sheet on a dashboard is a **filter action source** ("use as filter"), so clicking a bar, bubble, tile or state filters the other sheets on that dashboard.

**Calculated fields built:**
- 0/1 counters for every service, fee, custody and disclosure flag (so `SUM` gives a count and `AVG` gives a percentage of filings);
- `AUM Size Category` (5 buckets);
- `Resolution days` (end date minus start date, only when end ≥ start);
- `Resolution Time Category` (5 buckets; defined but **not used on any sheet yet**);
- a $10,000-wide bin on `MonetaryAmount`.

**How to read each sheet below:** *What it shows* · *Data used and why* · *Comparison made* · *Why this chart (and what else could have been used)* · *Why it matters* · *Issue and fix*. Where a mark is set to "Automatic" in the XML, I describe the chart type you can see in the screenshots.

**Which table feeds which dashboard**

| Dashboard | Question | Main table | Unit counted |
|---|---|---|---|
| 1 – Enforcement landscape | Who enforces, how often, how, where, against whom? | DRP (with firm name/location from ADV) | distinct **events** |
| 2 – Adviser profile | What do advisers look like, and how do those with disclosures differ? | ADV | **filings** |
| 3 – Outcomes and penalties | How do cases end, how severe, how fast? | DRP | distinct **events** |

---

### 7.1 Dashboard 1 – Enforcement landscape (1400 × 900)

Dashboard 1 uses almost entirely the **enforcement table**; AUM, fees and services are not used here. The ADV table only contributes the firm's name and office location, joined through `FilingID`.

**Sheet 1.1 – Enforcement Activity Over Time (line chart)**
- **What it shows:** number of distinct events per month, one line per `Initiator_Type`.
- **Data used:** `CNTD(EventID)` (a distinct count, because an event repeats in every filing that reports it), `MONTH(Date Initiated)`, `Initiator_Type` as colour.
- **Comparison:** across months (seasonality, spikes) and across regulator types (who drives the spikes). Largest spikes: SEC in September (about 395), Foreign in February (about 310), State in March (about 205).
- **Why a line:** ordered time axis plus several series. A bar chart per month would be too busy, and a pie has no time axis.
- **Why it matters:** shows whether enforcement is steady or comes in waves (sweeps against many firms at once).
- **Issue and fix:** `MONTH()` is month-of-year, so January 2023 and January 2024 are **added together** (the axis stops at December). Use a continuous month-and-year axis (as you did on sheet 3.2). The "Null" initiator (254 events) also appears as its own line.

**Sheet 1.2 – Sanctions and Event Count (treemap)**
- **What it shows:** one tile per `Principal_Sanction`; tile area = number of events, tile colour = total fine in dollars.
- **Data used:** `CNTD(EventID)` (size), `SUM(Monetary Amount)` (colour), `Principal_Sanction` (label).
- **Comparison:** how often each sanction is used (area) versus how much money it carries (colour).
- **Why a treemap:** part-to-whole for about 12 categories with two measures. Civil and administrative penalties take about 54% of events (about 2,060 of 3,840), then Cease and Desist, Other, Censure, Reprimand.
- **Why it matters:** shows enforcement is mostly fines and stop orders; the harshest sanctions are rare (Bar 10 events, Revocation 11).
- **Issue and fix:** the colour legend runs to "80B", which is **inflated**. `SUM(Monetary Amount)` adds the same fine once for every filing that reports it. For civil penalties it gives about $79.6B by rows against about $47.4B by distinct event (all sanctions: $105B versus $58B). See D10 for the fix.

**Sheet 1.3 – Leading Regulatory Authorities (packed bubbles)**
- **What it shows:** one bubble per authority (`Initiated_By`); size and colour = number of events.
- **Comparison:** how authorities rank against each other, concentrated in a few bodies or spread widely.
- **Why bubbles:** many named categories at once. A map is wrong because authorities are not places.
- **Issue and fix:** the bubbles have **no labels**, so you cannot tell which authority is which. The colour legend runs only from 7 to 15, so the chart shows 36 mid-sized authorities (of 298 in total), not the leading ones. The real leaders are missing: the SEC (about 560 events after merging its two spellings), Frankfurt Public Prosecutor (147), Mississippi Secretary of State (121), UAE Securities and Commodities Authority (109), Bloomberg SEF (108). Check the `Initiated_By` member filter and the `CNTD(EventID)` range filter, add `Initiated_By` to Label, or switch to a top-15 bar chart (after fixing duplicate names, D6).

**Sheet 1.4 – Regulatory Actions by Sanction Type (highlight table)**
- **What it shows:** `Initiator_Type` in rows, `Principal_Sanction` in columns, event count in each cell with a blue colour scale.
- **Comparison:** who imposes what. Biggest cells: Foreign with civil penalties (637), SEC civil penalties (445), SRO civil penalties (389), Other Federal civil (300), State and SEC cease-and-desist (297 and 293), State civil (292); foreign authorities also issue most reprimands (175). Row totals match the distinct events per initiator type (Foreign 1,045; SEC 793; State 764; SRO 609; Other Federal 375; no type 254).
- **Why a table:** two categorical dimensions plus a count is a heat table. A stacked bar would hide the small cells.
- **Why it matters:** each regulator has its own toolkit: State and SEC lean on cease-and-desist, SROs on fines, foreign bodies on reprimands.
- **Issue and fix:** the 637 cell dominates the colour scale, so most numbers appear in pale blue text that is hard to read. Use a darker palette or show percentage of row.

**Sheet 1.5 – Geographic Enforcement Concentration (US state map)**
- **What it shows:** US states shaded by number of events tied to firms whose office is in that state.
- **Data used:** `Office_State`, `Office_Country` (from ADV), `CNTD(EventID)` (from DRP).
- **Comparison:** state against state. New York is far darker at 1,385 events (about 36% of all 3,840); then Illinois 245, California 240, Florida 144, Massachusetts 98.
- **Why a map:** the question is geographic and a map shows clustering a bar chart cannot.
- **Why it matters:** shows where repeatedly disciplined firms are based. It does **not** show where the action took place.
- **Issue and fix:** New York stands out partly because large brokerages and asset managers are headquartered there. A rate (events per 1,000 firms in the state) is fairer. The "63 unknown" tag is places Tableau could not match.

**Sheet 1.6 – Global Enforcement Activity (world map)**
- **What it shows:** the same measure by country of the firm's office.
- **Comparison:** the US has 2,801 events (about 73%), against the UK 287, China 212, Australia 166, Germany 160.
- **Why a separate map:** it shows the international dimension; foreign regulators initiate 1,045 events, the largest group by initiator type.
- **Issue and fix:** the US sets the top of the colour scale, so every other country looks equally pale. Use a log or binned scale.

**Sheet 1.7 – Advisers with Highest Regulatory Activity (bar chart)**
- **What it shows:** top 15 firms by `CNTD(EventID)` with a dashed reference line at the average of the bars (122).
- **Comparison:** firm against firm. Merrill Lynch 285; then DWS Alternatives 208, DWS Hong Kong 183, DWS Investment Management Americas 180, DWS International 173, RREEF America 159, DWS Australia 156, DBX Advisors 152; then a sharp drop to Oppenheimer 63, Goldman Sachs 60, Gladstone 50, BofA 48, Raymond James 45, Credit Suisse 36, Wells Fargo 35.
- **Why a horizontal bar:** the standard chart for a ranked list, and long names fit on the left. Treemaps and bubbles are poor for ranking.
- **Why it matters:** identifies repeat names. The pattern is itself a finding: six DWS/DBX group entities report 1,052 distinct events (27% of all events), so this is a group-level effect.
- **Issue and fix:** it ranks by number of events, not severity. Pair it with median fine. Identify firms by `CRD_Number` because names change.

**Dashboard 1 takeaways:** SEC, SRO, State and Foreign authorities all matter, with foreign the largest initiator group; civil penalties are about 54% of events; New York hosts about 36% of events and US-based advisers about 73%; the top 8 entities (6 DWS/DBX plus Merrill Lynch and RREEF) account for about 39% of all events.

---

### 7.2 Dashboard 2 – Adviser profile (1000 × 1200) · *to be improved*

Dashboard 2 uses only the **ADV table** and counts **filings**, not firms (each firm files about 4.8 times).

**Sheet 2.1 – Adviser AUM Size (horizontal bar)**
- **What it shows:** number of filings in each `AUM Size Category`: $0–10M, $10M–100M, $100M–1B, $1B–10B, >$10B.
- **Data used:** `Total_AUM_USD` (AUM = assets under management, the standard size measure for advisers), turned into buckets by your calculated field, and `CNTD(FilingID)`.
- **Comparison:** how the adviser population is distributed by size. As Tableau computes it: $100M–1B 44,375 filings (the clear majority), $1B–10B 18,857, >$10B 11,350, $10M–100M 5,054, $0–10M 4,984.
- **Why a bar of buckets:** AUM spans ten orders of magnitude, so raw values cannot be plotted as a histogram; buckets make the shape readable.
- **Why it matters:** sets the context for everything else. Most advisers are mid-sized (median about $428M).
- **Issue and fix:** (1) the ">$10B" bar is inflated. `IF [Total_AUM_USD] < 10000000 ...` returns nothing for a missing AUM, so Tableau falls through to the `ELSE` branch and puts the **2,643 filings with no AUM** into ">$10B". The true figure is 8,707 plus a separate "No AUM reported" group (D11). (2) It counts filings, so use `COUNTD(CRD_Number)` on the latest filing per firm.

**Sheet 2.2 – AUM vs Account Scale (scatter)**
- **What it shows:** x = `Total NumAccounts`, y = total AUM, colour = `NumClients_Bucket`, size = number of employees, one mark per filing.
- **Comparison:** intended: does having more accounts mean more assets? How do clients and staff scale with it?
- **Why a scatter:** two continuous variables and a possible relationship.
- **Issue and fix:** **the x-axis is not accounts.** It runs to 1,300B (dollars), see D1. The marks pile up against the left axis because most firms have a 0 in that field, the linear scales hide almost all points in the lower-left corner, and 4 encodings on 84k points are unreadable (">3K nulls" are filings without AUM). Fix D1 first, then use log axes and a sample, or replace with a binned heat-map.

**Sheet 2.3 – Adviser Service Mix (bar chart of counts)**
- **What it shows:** how many filings tick each of 7 services (Measure Values on Rows).
- **Data used:** the 0/1 service counters, summed. Counts: portfolio management for individuals 59,815; financial planning 43,926; portfolio management for businesses 35,449; pooled vehicles 29,131; pension consulting 21,944; educational seminars 10,977; investment companies 8,086.
- **Comparison:** which services are common and which are niche.
- **Why bars:** comparing counts across categories; a pie would be wrong because firms can tick several services (the parts do not sum to 100%).
- **Why it matters:** the service mix describes the business model (retail planner versus fund manager), which changes both the risk and the regulator's interest.
- **Issue and fix:** truncated labels ("Portfolio Management — ..") cannot be told apart; the label style is inconsistent ("Financial Planning Count" versus "PooledVehicles"); some services are missing (selecting other advisers 30,864, other 15,006, publications 5,133). Show **% of firms**, sorted, with all services.

**Sheet 2.4 – Fee Structures (bar chart of counts)**
- **What it shows:** how many filings tick each of 6 fee types. The workbook total of 171,187 matches the sum of the six bars.
- **Data used:** fee counters. Counts: percentage of AUM 80,918; "commission" 43,751; hourly 28,997; other 13,400; "performance-based" 2,758; "fixed" 1,363.
- **Comparison:** how advisers charge. Almost all use a percentage of AUM (about 96%).
- **Why it matters:** commissions and performance fees create conflicts of interest, so the fee model is a natural risk feature.
- **Issue and fix:** **the labels are probably shifted by one** (D2): your "commission" at 52% looks like fixed fees, and your "performance-based" at 3% looks like commissions. Fix the mapping before presenting. Show % of firms instead of counts.

**Sheet 2.5 – Disclosure & Custody Indicators (sized tiles)**
- **What it shows:** the average of nine 0/1 flags (i.e. the percentage of filings with each): custody of client funds 46.15%; custody of securities 40.87%; overall disclosure 8.04%; SRO action 3.32%; regulatory action 3.05%; criminal felony (affiliate) 1.84%; civil judicial 1.22%; criminal felony (firm) 0.94%; bankruptcy 0.81%.
- **Comparison:** how common each operational risk (custody) and each type of disclosed event is.
- **Why square tiles with colour and size:** a compact "rate per indicator" display; size and colour both encode the same value, which gives the funnel shape.
- **Why it matters:** custody is the highest-risk privilege (it enables misappropriation), and the disclosure rates show how rare each event type is.
- **Issue and fix:** two different concepts (custody about 45%, disclosures 1-8%) share one colour scale, so the rare ones look nearly empty. Split them into two charts, and check the Item 11 labels (D4).

**Sheet 2.6 – Adviser Peer Comparison (scatter)**
- **What it shows:** x = total AUM (log scale), y = average employees, colour = disclosure Y/N, size = `Total NumAccounts`, one mark per filing.
- **Comparison:** where firms with disclosures (orange) sit compared with firms without (blue), by size.
- **Why a scatter:** peer positioning on two size measures with the outcome as colour. This is the best idea on the dashboard.
- **What it shows in your screenshot:** nearly every point above about 10,000 employees is orange. Disclosures cluster in the largest, most complex firms, which is also the main result of the ML baseline.
- **Why it matters:** it is the closest thing in the dashboard to the project question (is risk related to firm profile?).
- **Issue and fix:** the x-axis is already logarithmic (good), but the y-axis is linear, so most points sit on the floor; use log or `log1p` employees. The bubble size uses the wrong field (D1). The ">4K negative" tag means about 3,700 filings with $0 AUM cannot be drawn on a log axis. Use firm-level points (latest filing).

**Why Dashboard 2 feels weak, and how to fix it**
1. It describes the population but only one sheet (2.6) shows the outcome. *Every chart should be split by disclosure Y/N or show the disclosure rate.*
2. It counts filings instead of firms, mixes scales and has data bugs (D1, D2, D11).
3. The six sheets are not tied together by a question.

**Suggested redesign (reuse your sheets, change what they encode):**
- **KPI strip:** firms, % with disclosure, median AUM, % with custody (firm-level, latest filing).
- **Disclosure rate by AUM bucket** (bars, small to large, with "No AUM reported" separate). The size gradient is the main finding.
- **Disclosure rate by employee band.**
- **Fee model versus disclosure rate:** a dot plot with a reference line at the overall rate (after fixing D2).
- **Service-by-size heat-map** (rows services, columns AUM buckets, colour % of firms), replacing 2.3.
- **Custody × disclosure:** two bars or a 2×2, separate from the other disclosure tiles.
- **Peer scatter (2.6):** log-log, firm level, three encodings at most.
- **One shared filter set** (AUM bucket, country, service).

---

### 7.3 Dashboard 3 – Case outcomes and penalties (2000 × 2000)

Dashboard 3 uses only the **DRP table** and counts distinct events (3,840).

**Sheet 3.1 – Case status (horizontal bar)**
- **What it shows:** number of distinct events by `Status`: Final about 3,154, Pending 355, no status 280, On Appeal 51.
- **Comparison:** how many cases are finished versus still open. About 82% of events are final, 9% pending, 1% on appeal, 7% unknown.
- **Why a bar:** four categories, easy to compare. A pie would also work for so few slices, but bars are more precise.
- **Why it matters:** only final cases have reliable penalties and resolution times; pending ones can still change.
- **Issue and fix:** the "Null" bar (280) should be labelled "Unknown". Consider showing this as a KPI tile ("82% final") so that it does not use a whole chart.

**Sheet 3.2 – Resolution Time (line chart)**
- **What it shows:** average `Resolution days` per month of `Date Initiated` (continuous axis, 2023-2024).
- **Data used:** your calculated `Resolution days` = `DATEDIFF('day', Date Initiated, Resolution Date)`, only when the end date is not before the start (this removes 25 bad rows).
- **Comparison:** whether cases are getting faster. The line peaks just under 100 days around mid-2023 and falls below about 10 days for most of 2024, reaching about 0 by the end of 2024.
- **Why a line:** a measure over an ordered time axis.
- **Why it matters:** speed of enforcement and the cost of waiting for firms and investors.
- **Issue and fix:** the fall is **partly an artefact.** The typical case is resolved the same day (for resolved events: median 0 days, 70% resolved on day 0, 80% within 30 days, mean about 46 days), so the average is driven by a few long cases, and unresolved cases are missing, so recent months look fast. Use the median, or the **Resolution Time Category** field you already built, and show the count of unresolved cases.

**Sheet 3.3 – Sanction Types (treemap)**
- **What it shows:** tiles of `Principal_Sanction`; size and colour = distinct events (legend maximum 2,063; tooltip shows Other = 238).
- **Comparison:** how common each sanction type is, among the cases in the dashboard filter.
- **Why a treemap:** many categories with very unequal size; this works when one category dominates (civil penalties, about 54%).
- **Why it matters:** shows the "severity ladder": penalties and stop orders are common, the harshest sanctions are rare.
- **Issue and fix:** this almost duplicates sheet 1.2. Keep one version, or make this one a sorted bar with percentage labels, because small tiles (Suspension, Restitution) cannot be read.

**Sheet 3.4 – Monetary Penalties (histogram)**
- **What it shows:** number of fined events per $10,000 bin of `Monetary Amount`; filter `HasMonetarySanction = Y`.
- **Comparison:** the distribution of fine sizes. In the screenshot: 290 events under $10K and 277 between $10K and $20K, then spikes at about $50K, $70K, $160-170K and $300K (round-number fines that regulators and SROs use repeatedly).
- **Why a histogram:** the right chart type for the shape of one numeric variable.
- **Why it matters:** shows that most fines are modest while a few are huge. Across the 2,770 fined events the median is about $183K but the mean is about $21M.
- **Issue and fix:** with $10K bins the chart needs hundreds of bars to reach a maximum of $1.3B (note the scroll bar), so you cannot see the tail. Use **log-spaced buckets**. By distinct event: up to $10K 363, $10-100K 716, $100K-1M 618, $1-10M 532, $10-100M 366, over $100M 175.

**Sheet 3.5 – Penalty Size by Sanction Type (horizontal bar)**
- **What it shows:** `MEDIAN(Monetary Amount)` per `Principal_Sanction`. In the screenshot, Cease and Desist is about $6M, far above everything else (Undertaking about $0.46M, Disgorgement about $0.4M, Censure about $0.33M, Civil penalty about $0.09M).
- **Comparison:** typical fine by sanction type.
- **Why the median:** the fines are extremely skewed (mean about $21M against median about $183K), so the median is the robust statistic. Right choice.
- **Why it matters:** tells you which sanction carries real money.
- **Issue and fix:** **the ranking is distorted by repeated events.** Median is computed over rows, and large events appear in many filings (up to 68 rows for one event). Counted once per event, the Cease and Desist median is about **$375K** (not $6M) and the civil penalty median about **$175K** (not $90K); Undertaking (n = 9) becomes about $268M. Fix with an event-level table (D10) and show `n` next to each bar. Categories with a handful of events (Revocation 1, Disgorgement 2, Undertaking 9) are unreliable.

**Sheet 3.6 – Penalty vs Resolution (scatter)**
- **What it shows:** x = resolution days, y = average fine (log scale), colour = `Principal_Sanction`, one mark per event.
- **Comparison:** do bigger fines take longer to resolve? Visible answer: **no.** The huge fines (up to about $1B) sit at 0 days, and the slow cases (200-600 days) are mostly fines of $10K-$1M. Across events with both values the rank correlation is about -0.23 (slightly negative), and 94% of fines of $1M or more were resolved on day 0.
- **Why a scatter with a log y-axis:** two numeric variables with a very skewed fine. The log axis is the right choice.
- **Why it matters:** the largest penalties come from negotiated settlements (consent orders agreed on the day the action is announced), while contested cases take long and end with small fines.
- **Issue and fix:** the vertical stripe at 0 days hides overlapping points; add transparency or jitter, or replace with a box plot of fines by `Resolution Time Category`. The "4 nulls" are events without a resolution date.

**Dashboard 3 takeaways:** about 82% of events are final; resolution is usually immediate (settlement); the median fine is about $183K but the mean is about $21M because of a heavy tail (175 fines above $100M); the biggest fines are settled immediately, while slow cases carry small fines.

---

### 7.4 Charts deliberately not used (and why)
- **Pie / donut:** too many categories (12 sanctions, 20+ regulators) and very unequal shares (54-61% in one slice).
- **Stacked bars for services/fees:** a firm can tick several at once, so parts do not sum to 100%. Use separate bars or a heat-map.
- **Sankey (firm type → sanction → penalty):** attractive, but needs a flow reshape and is hard to read on skewed data. A possible extension.
- **Box plots (fines):** the right statistical chart for penalty analysis; suggested for 3.5 and 3.6.
- **Linear-scale scatter on AUM or fines:** unreadable across ten orders of magnitude, so use log axes (you did on 2.6 and 3.6).

### 7.5 Fix list for the workbook (in priority order)
1. **Event-level DRP table (D10):** fixes 1.2 and 3.5, and makes every event count and median correct.
2. **Sheet 2.1 (D11):** add a "No AUM reported" bucket.
3. **Sheet 1.3:** add labels and correct the filters, or use a top-15 bar.
4. **D1 and D2** in `final_select.py`, then rebuild 2.2, 2.4 and 2.6.
5. **Sheet 1.1:** continuous month axis; **1.4, 1.6:** better colour scales.
6. **Dashboard 2 redesign** as described in 7.2.
7. **3.2 and 3.4:** use the median / resolution categories and log buckets.

---

## 9. Data source and licence
SEC Investment Adviser Public Disclosure, Form ADV bulk filing data (2011-11-05 to 2024-12-31) and DRP regulatory records, both public. Check the SEC's terms of use before redistributing the raw files.
