# Software Requirements Specification

This document specifies the requirements for the PINES Management Processes Reporting System, derived from 20 input documents. It contains 51 requirements and 2 blacklisted (discarded) items. Requirement numbers are unique within this document.

## Input documents

1. D01 — conversations/conv_pines014_material_volume.eml
2. D02 — conversations/conv_pines015_capacity_interface.eml
3. D03 — conversations/conv_pines016_shelf_space.eml
4. D04 — conversations/conv_pines018_item_transfer.eml
5. D05 — conversations/conv_pines019_020_missing_intransit.eml
6. D06 — conversations/conv_pines021_item_purging.eml
7. D07 — conversations/conv_pines022_deletions.eml
8. D08 — conversations/conv_pines023_patron_characteristics.eml
9. D09 — conversations/conv_pines024_inactive_patrons.eml
10. D10 — early_draft_srs_galecia.txt
11. D11 — email_financial_reports.eml
12. D12 — email_report_features.eml
13. D13 — email_staff_login.eml
14. D14 — evergreen_reference_2009.txt
15. D15 — interview_cataloging_2009-05-08.txt
16. D16 — interview_sysadmin_2009-05-10.txt
17. D17 — meeting_minutes/meeting_2009-03-15_minutes.txt
18. D18 — meeting_minutes/meeting_2009-07-20_minutes.txt
19. D19 — meeting_tech_subcommittee_2009-06-30.txt
20. D20 — survey_results_2009.txt

## Priority scale

- **High:** Core to the system's purpose or requested by many stakeholders; the system is not acceptable without it.
- **Medium:** Clearly valuable and requested, but the system can go live without it and add it in a later release.
- **Low:** Nice to have, requested by a single stakeholder or marginal to the core workflows; implement only if time allows.

## Glossary

| Term | Definition |
| --- | --- |
| Management Processes | Reporting, analysis, inventory-management, and administrative capabilities used by library staff and managers. |
| Library system | A consortium member organization or administrative unit containing one or more branches. |
| Branch | A physical or mobile library location that owns, receives, or manages items. |
| Item | A physical copy or other inventory unit associated with a bibliographic record. |
| Bibliographic record | The catalog record describing a title or work and its intellectual content. |
| Patron | A library borrower or other person represented in the library system. |
| Staff member | An employee or authorized worker using Management Processes. |
| Report | A generated, viewable, downloadable, or delivered presentation of selected system data. |
| Query | Selection criteria used to identify or aggregate records for a report or administrative operation. |
| Report template | A reusable report definition containing controlled query and display settings. |
| Canned report | A predefined report supplied by the system and intended to run with limited configuration. |
| On-demand report | A report run at the user's request using predefined or editable criteria. |
| Open-template report | A report built by selecting available fields, filters, and output attributes. |
| Circulation | Check-outs, check-ins, renewals, holds, and related use transactions. |
| Electronic activity | OPAC or patron-account logins, online hold placement, online renewals, and integrated digital-resource access. |
| Transit | The period during which an item is moving between a sending and destination location. |
| Last copy | The only item copy within a specified branch, library system, or consortium scope. |
| Null value | A missing or unpopulated value that must remain distinguishable from a populated value. |
| Report queue | The ordered set of reports waiting to run or currently running. |
| Role | A named security grouping that grants permissions to an individual or staff group. |
| Historical report | A report based on data as it existed at a specified past date or date range. |
| Real-time report | A report based on current operational data at or near the time it is requested. |

## Requirements: High priority

### R001  Consortium-Scale Operation

**Priority:** High. The system supports the core consortium reporting mission and must operate at the stated organizational scale.

The system shall support reporting for a consortium of approximately 286 locations, 17 million annual circulations, 900,000 items purchased or processed annually, approximately 3.5 million patrons, and approximately 9.6 million items, while allowing searches and reports to operate during open hours without disrupting circulation or public services.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R002  Background Report Processing

**Priority:** High. Slow reports currently affect production operations and were repeatedly identified as a critical technical concern.

The system shall execute long-running searches and reports through background processing, a queue, or an equivalent isolation mechanism so that report generation does not materially disrupt circulation clients, the OPAC, or other operational functions during open hours.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R003  Supported Server Environments

**Priority:** High. Linux and Solaris support is an explicit operational constraint for the consortium.

The system shall operate on supported Linux and Solaris server environments, including the consortium's Linux production environment and Solaris secondary or disaster-recovery environment.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R004  Accessible Staff Client

**Priority:** High. Staff require browser or Windows-client access across heterogeneous library environments.

The system shall be accessible through a web browser or a Windows-compatible client; when delivered through a browser, it shall support Microsoft Internet Explorer 6.0 or later and Mozilla Firefox 2.0 or later.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R005  Assistive Technology Accessibility

**Priority:** High. Accessibility is a legal and institutional requirement for public libraries.

The system and its reports shall be usable with screen readers, screen magnification software, and other assistive technologies, including tools such as JAWS, NVDA, and ZoomText, and shall provide appropriately structured accessible output.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R006  Relational Data Access

**Priority:** High. Management reporting depends on joining bibliographic, item, patron, transaction, and financial records.

The system shall use and support a fully relational database model capable of querying and joining the relevant bibliographic, item, patron, circulation, hold, staff, and financial records without requiring users to manage implementation-specific data structures.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R007  Standards-Compliant Output

**Priority:** High. Standards-compliant HTML supports browser compatibility and accessibility.

The system shall produce standards-compliant HTML for the staff interface, help content, and browser-displayed reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R008  Role-Based Access Control

**Priority:** High. Security and appropriate access to reports and administrative operations are essential.

The system shall control user rights and privileges through assignable roles or security groups that support individuals, workgroups, and arbitrary staff groups, including distinct permissions for staff, managers, local administrators, and global administrators.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D13 (email_staff_login.eml), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R009  Streamlined Staff Login

**Priority:** High. Faster login is needed at shared service terminals, while individual accountability must be preserved.

The system shall support optional streamlined staff login, such as an employee card or badge swipe, and shall also support individual username-and-password login as a fallback; either method shall identify the individual staff member and apply that person's assigned roles.

**Sources:** D10 (early_draft_srs_galecia.txt), D13 (email_staff_login.eml), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R010  Query Builder

**Priority:** High. A general query facility is foundational to the requested reports and administrative workflows.

The system shall provide staff with a user-friendly query builder for supported bibliographic, item, patron, transaction, hold, financial, and staff records, including field selection, value picklists, regular-expression options, Boolean operators, and administrator-controlled access to fields and record types.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D06 (conversations/conv_pines021_item_purging.eml), D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R011  Report Templates and Cloning

**Priority:** High. Templates are heavily requested and ensure consistent results across branches.

Authorized administrators shall be able to create, publish, clone, and manage reusable report templates; staff shall be able to run authorized templates as supplied or modify only the filters and display fields permitted by the template owner.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R012  Report Permission Administration

**Priority:** High. Fine-grained report permissions were requested by most survey respondents and are needed to protect sensitive data.

The system shall permit administrators to separately control who may create, clone, modify, run, or share reports, shall provide shared folders or equivalent access groups, and shall update effective permissions when a user's role assignment changes.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D13 (email_staff_login.eml), D16 (interview_sysadmin_2009-05-10.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R013  Report Queue Visibility

**Priority:** High. Staff need to distinguish queued reports from failed reports and reduce unnecessary support calls.

For each submitted report, the system shall display its queue position or number of reports ahead, submission time, priority, and status at least as waiting, running, completed, or failed.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R014  Report Scheduling and Cancellation

**Priority:** High. Recurring reports and operational control are required for board, audit, and management workflows.

Authorized users shall be able to run reports immediately or schedule them hourly, daily, weekly, monthly, or yearly, and shall be able to cancel a scheduled or currently running report when permitted.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R015  Report Output Formats

**Priority:** High. Staff require interoperable output for spreadsheets, web viewing, and data exchange.

The system shall produce report results in HTML, CSV, and Excel-compatible formats and shall preserve the selected data fields and values consistently across those formats.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R016  Report Criteria and Metadata

**Priority:** High. Showing the criteria makes results auditable and prevents ambiguity.

Each report result shall identify the report name, selected date range, and selection criteria used to produce it, and shall display all null and blank values rather than silently excluding records.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R017  Historical and Real-Time Reporting

**Priority:** High. Managers need both current operational information and past-state comparisons.

The system shall support real-time reports over current data and historical reports for a specified past date or date range, including historical values needed to compare collection, transaction, financial, and location conditions over time.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R018  Online Help and Error Feedback

**Priority:** High. Staff must be able to use and troubleshoot the system without depending on IT.

The system shall provide searchable, hierarchical, cross-linked online HTML help describing system functions, and shall provide meaningful high-level errors and query-specific diagnostic feedback to authorized administrators when a report or operation fails.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R019  Material Volume Report

**Priority:** High. Collection volume reporting is a recurring board and collection-management need.

The system shall report material volume for a selected branch, library system, or historical point in time, separately showing newly acquired items, checked-in items, checked-out items, and their total, with breakdowns by configurable categories such as total items, holds, adult fiction, board books, genre, and format.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R020  Branch Capacity Dashboard

**Priority:** High. Branch capacity visibility supports immediate allocation and transfer decisions.

The system shall provide a dashboard showing capacity metrics for all branches at once, allow users to drill into an individual branch, and indicate capacity condition using configured thresholds such as under capacity, approaching capacity, and at or over capacity.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R021  Shelf Space Utilization Report

**Priority:** High. Shelf-space analysis is required for collection allocation and branch comparison.

For each selected genre and format, the system shall compare the percentage of total circulations, percentage of the collection, and percentage of total shelf space, with views available by branch, library system, and date range.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R022  Batch Item Transfer

**Priority:** High. Moving groups of items between branches is a core collection-management workflow.

Authorized staff shall be able to select item candidates using a query, save and reuse the query, manually select a subset of results, preview the proposed changes, and change the selected items' destination location in a single controlled transfer operation.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D20 (survey_results_2009.txt)

### R023  Transfer Logistics and Reversion

**Priority:** High. Temporary transfers require practical movement documentation and reliable return handling.

The transfer utility shall generate pull lists and printable transit labels, support time-based and configured event-based reversion to the original location, and provide an undo operation for an accidental transfer when the transfer remains eligible for reversal.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R024  Transfer Audit and Alerts

**Priority:** High. Transfer history is needed for accountability and identifying repeatedly misplaced items.

The system shall record each transfer and its participating items, locations, user, and time; shall provide transfer-history reports; and shall support notifications for configured transfer delays or exceptions.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt)

### R025  Missing and Damaged Items Report

**Priority:** High. Branch-level missing and damaged inventory is required for audits and collection decisions.

The system shall provide a report of missing and damaged items grouped by branch, including item condition notes when available and supporting date-range filtering for audit and trend analysis.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R026  In-Transit Items Report

**Priority:** High. Delivery delays and lost items are a significant operational problem.

The system shall provide one combined report of items in transit to or from a branch or library system when transit exceeds a configurable number of days, defaulting to seven days where no other value is configured, and shall support sorting by due date or age.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R027  Item Purge Candidate Reports

**Priority:** High. Weeding staff need safe, flexible identification of records for removal.

The system shall identify item records for possible purge using combinable status-based, time-based, and activity-based criteria, including missing or discard/weed status, time in status, last circulation age, damage, and other administrator-approved fields, and shall present candidates in a read-only report before deletion.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R028  Batch Status Conversion

**Priority:** High. Batch status conversion substantially reduces repetitive cataloging work.

Authorized staff shall be able to select item candidates and convert their statuses in batch, such as changing missing items to discard/weed, while previewing the affected items before confirmation.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R029  Last Copy Report

**Priority:** High. Preventing accidental deletion of a consortium's only copy is critical.

The system shall identify last copies within a selected branch, library system, facility, or consortium scope, including copies already deleted where historical data permits, so catalogers can review them before deletion and update external catalog records such as WorldCat.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R030  Safe Record Cleanup

**Priority:** High. Cleanup must remove orphaned structures without allowing uncontrolled destructive actions.

Authorized staff shall be able to delete volume entries with their associated copy entries and delete bibliographic records with no attached items, subject to a separate confirmation step, permission checks, and audit logging.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R031  Deletion Audit Reporting

**Priority:** High. Deletion traceability is required for compliance, accountability, and troubleshooting.

The system shall record and report deletion events for item, patron, bibliographic, and other configured record types, including record identifier, record type, deletion timestamp, deleting user, user location, and available pre-deletion context, with aggregation by date range, location, system, user, and type.

**Sources:** D07 (conversations/conv_pines022_deletions.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R032  Patron Characteristic Analysis

**Priority:** High. Demographic analysis is used for programming, purchasing, and service planning.

The system shall allow patron reports to filter and group by configurable age range, ZIP code, county, home branch, patron type, and preferred language, including combined AND/OR filters and null-valued records.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R033  Inactive Patrons Report

**Priority:** High. Inactive-patron reporting supports database maintenance and outreach.

The system shall list patrons with no physical circulation or defined electronic activity during a configurable number of preceding days, support grouping by system, home library, county, or another authorized organizational level, include current mailing addresses, identify patrons with outstanding fines separately, allow configured exclusions such as staff or opt-outs, and export results.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt)

### R034  Transaction Classification Reports

**Priority:** High. Survey respondents require detailed operational statistics by transaction method and location.

The system shall count and report check-ins separately and cumulatively by book drop, staff terminal, staff user, and self-service; check-outs and renewals by staff, self-service, online, and OPAC method; and holds by placement method including staff desk, public computer, and remote placement.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R035  Transaction Aggregation

**Priority:** High. Transaction trends are needed for staffing, executive reporting, and service evaluation.

The system shall aggregate transactions by hour, terminal, branch, library system, county, patron, selected groups of libraries, and transaction type, including check-ins, check-outs, renewals, holds placed, holds filled, fines collected, and patron registrations.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R036  Transaction Retention and Privacy

**Priority:** High. The system must balance historical analysis with patron privacy and legal retention obligations.

The system shall retain transaction history for a configurable period, retain monthly and annual aggregates indefinitely, and archive retained transaction data in a form that supports required demographic statistics without retaining personally identifying patron information beyond authorized legal and policy limits.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R037  Patron Behavior Statistics

**Priority:** High. Stakeholders need to understand and predict use of library materials.

The system shall provide anonymized statistics describing patron behavior and material use, including average return time, renewal likelihood, and the proportion of check-outs that are renewals, with results aggregatable by authorized demographic or organizational dimensions.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R038  Financial Value Reports

**Priority:** High. Item value reporting supports financial and collection-management decisions.

The system shall report the aggregate value of the entire collection or a selected subset of items using item-record value data, with filtering by status, format, collection, branch, shelving location, or other authorized item attributes.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R039  Financial Reports

**Priority:** High. Financial reporting is required for reconciliation, budgeting, and oversight.

The system shall report patron account balances by patron, home library, and system; fines and charges by time period and charge type; fines waived by time period and branch; and payments by time period, collecting library, and payment method.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D20 (survey_results_2009.txt)

### R040  Financial Ledger and Updates

**Priority:** High. Every payment must be traceable to support reconciliation.

The system shall maintain a ledger linking each patron payment to the specific charge or charges it settles, record payment method and collecting location, and make authorized financial updates available to reports immediately after they are committed.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R041  Financial Compliance and Retention

**Priority:** High. Financial data must satisfy public-sector audit and retention obligations.

The system shall support standard accounting practices and applicable state, county, and municipal auditing requirements, including configurable retention policies for financial reports and archived financial data.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R042  Executive and Board Reports

**Priority:** High. Directors and boards require dependable predefined summaries.

The system shall provide predefined executive reports containing collection, traffic, circulation, holds, and volume statistics, with cross-tabulation by terminal, branch, library system, hour, patron age range, patron type, patron location, and other configured management dimensions.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R043  Development, Training, and Migration

**Priority:** High. Configuration changes must be tested safely before production use.

The system shall provide separate development, training, and production environments, shall prevent training activities from damaging production data, and shall support export and import of report templates, saved queries, role settings, and other supported configuration between environments.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R044  OPAC and Operational Independence

**Priority:** High. Public catalog availability must not be degraded by management reporting.

The Management Processes system shall operate without constraining or materially slowing the OPAC, circulation client, or other patron-facing functionality, including while resource-intensive reports are running.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

## Requirements: Medium priority

### R045  Uncataloged Material Tracking

**Priority:** Medium. Uncataloged-material tracking is valuable for collection control but is not required for the primary reporting launch.

The system shall allow authorized staff to register and track uncataloged materials such as paperback and board books with minimal branch labor, support rapid distribution, identify their use, and include their transactions in circulation statistics.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R046  Data Quality Reports

**Priority:** Medium. Data quality reports improve catalog maintenance but can follow core operational reporting.

The system shall provide reports identifying invalid item types, long call numbers, bibliographic records without item or volume records, missing required MARC fields, and other configured data-quality exceptions.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R047  Item Edit and Circulation Dates

**Priority:** Medium. Separating edit activity from circulation improves data-quality and collection analysis.

Item reports shall provide the last bibliographic or item edit date separately from the last circulation date, and shall not update the edit date merely because an item circulates.

**Sources:** D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R048  Report Delivery

**Priority:** Medium. Email delivery and address management improve recurring-report workflows but are not required for initial operation.

Authorized users shall be able to deliver completed reports to configured email addresses and maintain a reusable address book for commonly used recipients.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R049  Report Prioritization

**Priority:** Medium. Queue prioritization is useful for executive and time-sensitive reports but is a later enhancement.

Authorized users shall be able to assign or configure report priorities so that eligible reports, such as board reports, can be processed ahead of lower-priority resource-intensive reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt)

### R050  Advanced Report Presentation

**Priority:** Medium. Pivoting and comparative presentation improve analysis but are not essential to core report generation.

The system shall support pivot-table output, comparative period columns and percentage differences, configurable display fields, and retrieval of selected MARC fields on a single report row where the underlying data permits.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R051  Report Input and Descriptions

**Priority:** Medium. These features improve usability for complex or frequently reused reports.

The system shall allow authorized users to upload text files containing identifiers such as barcodes or TCNs as query input, shall provide descriptions or tooltips for canned reports, and shall support filtering by survey name without requiring users to enter an internal survey identifier.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

## Requirements: Low priority

None.

## Blacklist

### B01  Report Directly on the Production Database Without Isolation

**Priority:** High. The underlying goal of timely reporting is high priority, but this implementation constraint conflicts with operational requirements.

The discarded statement would require the reporting system to use the live production database directly for complex analytical queries and would reject a reporting replica, warehouse, or equivalent isolation mechanism.

**Sources:** D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

**Reason:** It conflicts with R002 and R044, which require background or isolated processing that does not disrupt circulation or the OPAC. R006 requires relational data access but does not require all reports to execute against the production workload.

### B02  Automatic Reversion When an Item Is Checked Out at the Destination

**Priority:** Low. Event-based reversion was suggested as a possible transfer rule, but it is semantically inconsistent with the stated workflow.

The discarded statement would automatically return an item to its original location when it is checked out at the destination branch.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

**Reason:** The source discussion states that an item checked out at the destination should remain there, while unused items should return. Automatic reversion on checkout would therefore contradict the intended transfer behavior.

## Open issues

- **Capacity definition** (R020): Stakeholders have not agreed whether capacity means item count, shelf space, configured physical limits, circulation load, processing capacity, or a combination.
- **Shelf-space measurement** (R021): The source data does not directly track shelf space; stakeholders must decide whether to collect dimensions, configure estimates, or use item count as a proxy.
- **Electronic activity scope** (R033): Integrated digital-resource access is requested where available, but the specific external systems and event types to include remain unresolved.
- **Retention periods** (R036, R041): Exact transaction and financial retention durations must be defined by applicable law and institutional policy.
- **Historical data availability** (R017, R029, R047): The system must establish which past states, deleted records, and item dates are available for historical reporting.

## Coverage

| Document | Path | Requirements | Blacklist |
| --- | --- | --- | --- |
| D01 | conversations/conv_pines014_material_volume.eml | R017, R019 |  |
| D02 | conversations/conv_pines015_capacity_interface.eml | R015, R020 |  |
| D03 | conversations/conv_pines016_shelf_space.eml | R017, R021, R050 |  |
| D04 | conversations/conv_pines018_item_transfer.eml | R008, R010, R022, R023, R024 | B02 |
| D05 | conversations/conv_pines019_020_missing_intransit.eml | R025, R026 |  |
| D06 | conversations/conv_pines021_item_purging.eml | R027, R028, R029, R030 |  |
| D07 | conversations/conv_pines022_deletions.eml | R031 |  |
| D08 | conversations/conv_pines023_patron_characteristics.eml | R016, R032 |  |
| D09 | conversations/conv_pines024_inactive_patrons.eml | R015, R033 |  |
| D10 | early_draft_srs_galecia.txt | R001, R002, R003, R004, R005, R006, R007, R008, R009, R010, R011, R012, R013, R014, R015, R016, R017, R018, R019, R020, R021, R022, R023, R025, R026, R027, R028, R029, R030, R031, R032, R033, R034, R035, R036, R037, R038, R039, R040, R041, R042, R043, R044, R045, R046, R048, R049, R050, R051 | B01 |
| D11 | email_financial_reports.eml | R038, R039, R040, R041 |  |
| D12 | email_report_features.eml | R011, R012, R013, R014, R016, R018, R042, R049 |  |
| D13 | email_staff_login.eml | R008, R009, R012 |  |
| D14 | evergreen_reference_2009.txt | R001, R002, R004, R005, R006, R007, R008, R010, R011, R013, R014, R015, R016, R017, R018, R029, R031, R032, R034, R036, R042, R043, R044, R046, R047, R048, R049, R050, R051 | B01 |
| D15 | interview_cataloging_2009-05-08.txt | R019, R021, R022, R023, R025, R026, R027, R028, R029, R030, R031, R045, R046, R047 |  |
| D16 | interview_sysadmin_2009-05-10.txt | R001, R002, R003, R004, R005, R006, R007, R008, R009, R012, R018, R043, R044 | B01 |
| D17 | meeting_minutes/meeting_2009-03-15_minutes.txt | R019, R020, R022, R042 |  |
| D18 | meeting_minutes/meeting_2009-07-20_minutes.txt | R001, R002, R003, R004, R005, R006, R007, R008, R013, R018, R019, R021, R025, R026, R042, R043, R044, R046 |  |
| D19 | meeting_tech_subcommittee_2009-06-30.txt | R002, R005, R006, R007, R008, R010, R011, R012, R016, R017, R018, R043, R044, R049, R051 | B01 |
| D20 | survey_results_2009.txt | R001, R002, R008, R011, R012, R013, R014, R015, R016, R026, R032, R034, R035, R036, R037, R042, R047, R048, R049, R050 |  |