# Software Requirements Specification

This document specifies the requirements for the library management and reporting system, derived by an agentic refinement network from 20 input documents. It contains 126 requirements and 0 blacklisted (discarded) items. Requirement numbers are assigned in document order, are unique within this document and are not stable across runs.

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
| branch | A physical library service point or other managed library location. |
| library system | The organization or consortium that contains and manages multiple branches. |
| item | A physical or uncataloged material record managed by the system. |
| patron | A person with a library account. |
| report | A generated presentation or export of queried system data. |
| circulation | A transaction involving checkout, check-in, renewal, hold activity, or related material use. |
| hold | A patron request to reserve or obtain an item. |
| status | The operational condition assigned to an item or record, such as missing, damaged, or discard/weed. |
| OPAC | The Online Public Access Catalog through which patrons access catalog, hold, and circulation functions. |
| MARC | The machine-readable cataloging data format used for bibliographic fields. |
| TCN | A title control number used to identify a bibliographic record. |
| WorldCat | An external union catalog used for bibliographic and holdings updates. |
| CSV | A comma-separated values file format used for data export. |
| role | A named security assignment that determines a user's permissions. |
| library automation system | The enterprise system providing acquisitions, cataloging, circulation, and related library records. |

## Requirements: High priority

### R001  Collection And Material Use Reports

**Priority:** High. Seven source documents call for collection and material-use analysis, and managers depend on it to plan, evaluate, and oversee collections.

The reports interface must enable authorized managers, administrators, and staff to analyze collections and material use for planning, evaluation, and oversight.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D03 (conversations/conv_pines016_shelf_space.eml), D05 (conversations/conv_pines019_020_missing_intransit.eml), D06 (conversations/conv_pines021_item_purging.eml), D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R002  Consortium Scale

**Priority:** High. D10 marks OE-1 High Priority, and consortium-scale support is necessary for the system to serve its stated 286-branch environment. (D10 marks OE-1 High Priority)

The system must support a library consortium with 286 branches, 17 million annual circulations, and purchasing and processing exceeding 900,000 items per year.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R003  Cross-Branch Performance Reports

**Priority:** High. Cross-branch performance analysis is repeatedly requested across seven documents and supports oversight of the consortium as a whole.

The reports interface must enable analysis of performance across branches.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R004  Role-Based Transfer Access

**Priority:** High. D10 marks CO-4 High Priority, and D16 identifies role-based access control as essential; without it, staff cannot be reliably limited to authorized reporting and transfer actions. (D10 marks CO-4 High Priority; D16's interview notes describe role-based access control as essential)

Administrators must control rights through security groups and roles assigned to individuals, workgroups, and arbitrary staff groups, with changes to role assignments changing permissions. The library automation system must support Global Admin, Local Admin, Library Manager, Staff, and indirect Patron access through the OPAC, with report and transfer permissions appropriate to each role and transfers restricted to authorized roles, including managers, administrators, and transfer coordinators.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D13 (email_staff_login.eml), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R005  Collection Analysis Reports

**Priority:** High. D06 and D15 explicitly mark last-copy reporting critical, and these reports help catalogers avoid inappropriate deletion while supporting collection decisions. (D06 marks last-copy reporting critical; D15 marks the last-copy report as critical)

The system must provide reports on weeding data, collection age, collection value, and last-copy status. Collection-value reports must use purchase-price or other item-record data and cover the entire collection or selected portions, including status- or collection-based selections such as longoverdue items or children's DVDs. Last-copy reports must identify items that are the only copy within a selected branch, library system, consortium, bibliographic work, or collection grouping, including deleted last copies where applicable, so catalogers can update WorldCat and avoid inappropriate deletion.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R006  Item Status and Activity Reports

**Priority:** High. Missing-item reporting is required by the fixed requirements, and the broader status reports also help staff manage overdue and in-transit materials.

The system must provide reports on items that are missing, overdue, in transit, claimed returned, selected by use count, or associated with a fines-stopped reason.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R007  Missing Damaged Reports

**Priority:** High. D05 calls the per-branch report crucial for accountability, and four additional sources request missing or damaged item reporting. (D05 calls the per-branch missing/damaged report crucial for accountability)

The system must report missing and damaged items by branch, including condition notes such as water damage or vandalism and selectable periods such as the preceding 30 days or last quarter.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R008  Transit Report Suite

**Priority:** High. D18 describes in-transit item reports as critical for delivery coordination, and delayed or untracked transfers can disrupt service across branches. (D18 describes in-transit item reports as critical for delivery coordination)

The system must provide reports for items in transit to a destination branch and items in transit by sending branch, including one report combining transit-to and transit-from items that have remained in transit longer than a configurable threshold, defaulting to seven days where specified, using a null arrival date and an overdue departure date; results must be available by branch and library system and sortable by due date.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R009  Activity and Traffic Cross-Tabulation

**Priority:** High. Five source documents request these usage measures, and without cross-tabulation managers lose a key way to compare activity across branches, systems, and patron groups.

The system must provide activity, traffic, and usage reports showing counts of checkouts, check-ins, holds placed, and holds filled, cross-tabulated by terminal, branch, library system, hour, patron age range, patron type, and patron location, and must classify hold-request counts by placement method, including staff desk, public computer, and remote placement.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R010  Checkout and Renewal Reports

**Priority:** High. Checkout and renewal counts directly support the fixed requirement for item-use reporting and help managers understand how materials are used.

The system must provide checkout and renewal reports that count transactions individually and cumulatively by staff checkout, self-checkout, staff renewal, self-checkout renewal, online renewal, and OPAC renewal.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R011  Background Report Processing

**Priority:** High. The fixed open-hours performance requirement calls for reports not to disrupt other services, and background processing helps meet that need for large, slow queries.

Long-running reports, including inactive patron reports in environments with approximately 3.5 million patrons, must execute as background operations or through a queue without occupying the user interface, and the system must cache slow activity-query results for reuse.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R012  Accounting Data Retention

**Priority:** High. Applicable financial retention rules, including required audit-data periods, must be enforced to support accountable records management.

The system must archive financial data according to state and local requirements and enforce applicable retention policies, including seven years of audit data where required.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R013  Assistive Technology Access

**Priority:** High. D16 and D18 identify Section 508 accessibility as a legal requirement and mandatory, making assistive-technology access a compliance obligation. (D10 marks OE-5 High Priority; D16 describes Section 508 compliance as non-negotiable and a legal requirement; D18 describes this as a legal requirement and says Section 508 compliance is mandatory)

The system must satisfy Section 508 accessibility requirements and support screen readers including JAWS and NVDA, screen magnification including ZoomText, and other assistive technologies; web output must include appropriate alt tags, ARIA labels, semantic structure, and standards-compliant HTML.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R014  Branch Management Reports and Templates

**Priority:** High. Multiple source documents request management reports for consortium branches, and without suitable reports and templates branch managers would lack a consistent way to meet routine oversight needs.

The system must provide predefined reports and report templates needed to cover the management reporting needs of all consortium member branches.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R015  Client And Browser Access

**Priority:** High. D10 marks OE-3 High Priority and D18 calls browser/client access critical, so staff access to the system depends on this capability. (D10 marks OE-3 High Priority; D10 marks OE-4 Medium Priority; D18 marks this capability critical)

The system must be accessible through a web browser or Windows-compatible client and support Microsoft Internet Explorer 6.0 or later and Mozilla Firefox 2.0 or later.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R016  Cross-Record Query Designer

**Priority:** High. A cross-record query designer lets staff build reports across the system's principal data areas, and without it many requested analyses would require custom work.

The system must provide a user-friendly query designer across bibliographic, item, patron, transaction, financial, and other record types, with selectable fields, picklists, regular-expression choices, and Boolean operators.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R017  Data Archiving Compliance

**Priority:** High. D10 and D11 require compliant financial-data archiving for auditing, so noncompliant archiving would fail the stated records obligations.

Data archiving must comply with standard accounting practices and state, county, and municipal auditing requirements.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R018  Financial Report Compliance

**Priority:** High. D10 and D11 require financial reports to meet accounting practices and government auditing requirements, so reports that fail those standards would not meet the stated obligation.

Financial reports must comply with standard accounting practices and state, county, and municipal auditing requirements.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R019  Integrated Accessible System Help

**Priority:** High. D10 marks UD-3 High Priority, and accessible, searchable help lets staff learn and use reporting functions without relying solely on direct support. (D10 marks UD-3 High Priority)

The system must provide hierarchical, cross-linked, searchable HTML help that describes and illustrates system functions, is accessible within the system and to screen readers, and includes integrated online help for the reporting interface.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R020  Management Reporting Scope

**Priority:** High. Five sources define management planning, evaluation, and oversight as the reporting system's scope, distinguishing it from patron-facing operations.

The reporting functionality must support management planning, evaluation, and oversight rather than day-to-day patron-facing functions handled by the OPAC and circulation client.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D05 (conversations/conv_pines019_020_missing_intransit.eml), D06 (conversations/conv_pines021_item_purging.eml), D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D16 (interview_sysadmin_2009-05-10.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R021  OPAC Preservation

**Priority:** High. D10 marks CO-5 High Priority, and management reporting that degrades patron access would compromise the underlying library service. (D10 marks CO-5 High Priority; D16's interview notes describe separation of reporting from the OPAC as critical)

Management and reporting functionality must not constrain, slow, or adversely affect OPAC functionality or patron access.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R022  Open-Hours Reporting Performance

**Priority:** High. Because five source documents request this capability and reports that disrupt circulation or OPAC access would undermine core library operations, isolation is needed for the system to remain usable during open hours.

Searches and reports must run during open or peak hours without disrupting circulation, other system functions, or the OPAC; background queues, a separate reporting database or replica, or equivalent isolation must prevent excessive contention with the production database when needed.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R023  Patron Information Removal

**Priority:** High. D12 identifies patron-privacy protection as a compliance requirement, so retained transaction data must have personally identifying information removed. (D12 identifies State-law retention and patron-privacy protection as compliance requirements)

The system must remove personally identifying information about patrons from retained transaction data.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R024  Payment Audit Ledger

**Priority:** High. D11 marks the payment ledger CRITICAL, and tracing applied payments is needed to reconcile patron financial records. (D11 marks this requirement CRITICAL)

The system must maintain a payment ledger identifying the charge or charges to which each patron payment was applied so payments can be traced and reconciled.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R025  Record Data Specifications

**Priority:** High. D10 marks UD-1 High Priority, and accurate data specifications support the cross-record reporting the product must deliver. (D10 marks UD-1 High Priority)

The product must provide complete data specifications and dictionaries for authority, bibliographic, order, item, hold/request, and other accessed records, including field names, data types, and relationships.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R026  Relational Database Support

**Priority:** High. D10 marks CO-1 High Priority, and the requested relational access underpins the system's complex cross-record reporting. (D10 marks CO-1 High Priority)

The system must use and operate with a fully relational database, support complex joins, and not require a denormalized reporting schema that can cause synchronization problems.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R027  Report Accuracy

**Priority:** High. Inaccurate or unreliable reports undermine the system's central purpose of supporting management decisions.

Report output must be tested and demonstrated to be accurate and dependable.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R028  Report Types and Uses

**Priority:** High. Canned, on-demand, and open-template reports give users practical ways to cover routine and changing needs across core record types, making the system usable for its reporting purpose.

The reporting interface must provide canned reports, noncanned on-demand reports based on preselected criteria for maintenance and collection-development activities, and open-template reports with selectable attributes for circulation, items, patrons, bills, and bibliographic records.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R029  Server Platform Support

**Priority:** High. D10 marks OE-2 High Priority, specifying the server platforms the product must support in the target environment. (D10 marks OE-2 High Priority)

The system must operate on Linux and Solaris servers, including Red Hat Enterprise Linux 5 and Solaris 10 on SPARC hardware where specified.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R030  Standards Compliant HTML

**Priority:** High. D10 marks CO-2 High Priority, establishing standards-compliant HTML as a specified product constraint. (D10 marks CO-2 High Priority)

Web interfaces, reports, and online help must produce HTML that validates against applicable web standards.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R031  Transaction Data Retention

**Priority:** High. D12 identifies state-law retention as a compliance requirement, so the system must retain transaction data for the legally required period. (D12 identifies State-law retention and patron-privacy protection as compliance requirements)

The system must retain circulation transaction data for the legally required period.

**Sources:** D12 (email_report_features.eml)

## Requirements: Medium priority

### R032  Historical Reporting

**Priority:** Medium. Historical reporting helps users understand what values and locations were at a past date, but it requires preserved data beyond the system's basic current-state reports.

The system must provide historical reports through preserved data or a reporting warehouse, retrieving values as they existed at a specified date or date range, including past bills and shelving locations.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R033  Material Volume Reporting

**Priority:** Medium. Material-volume reporting helps managers track collection size and recent acquisitions by branch or system, but it is a focused management report. (D01 identifies the Material Volume Report as a key requirement)

The system must report material volume for a specified library system or branch at the current or a historical date, including total items, new acquisitions, material added during selectable periods based on item acquisition dates such as the preceding 30, 60, or 90 days, checked-in items, checked-out items, holds, adult fiction, and board books. Checked-out items must count toward the total, and category groupings must be configurable by library system, such as fiction/non-fiction or format.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R034  Branch Capacity And Demographics

**Priority:** Medium. Branch capacity and demographic analysis helps managers assess local needs, although the reporting system can serve its core purpose without this specific analysis.

The reports interface must enable analysis of branch capacity and patron demographics.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R035  Inventory Capacity Reporting

**Priority:** Medium. Branch capacity comparisons and trends help managers allocate space and monitor growth across the consortium, but the system can provide other oversight reports without them.

The system must provide authorized staff, including branch managers, with inventory and operational capacity reports for monitoring collections and capacity. The capacity report must provide an all-branch view, allow drilldown to an individual branch, show capacity trends such as growth or shrinkage, support comparison for up to 286 branches, allow users to filter and sort branches by region, library type, and current load, and allow users to export capacity-view data in CSV format.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R036  Staff Workflow And Financial Reports

**Priority:** Medium. Staff-workflow and financial reporting helps administrators monitor operations and transactions, but it is one valuable reporting area among several.

The reports interface must enable analysis of staff workflow and financial transactions.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R037  Item Use and Circulation Metrics

**Priority:** Medium. These metrics help staff evaluate the use of uncataloged materials, while core collection and circulation reporting can still operate without this specialized coverage.

Reports must identify usage of uncataloged materials and provide total item-use counts, counts by fiscal year, month, or other usage date range, and circulation statistics including checkout, renewal, and other transactions involving uncataloged materials.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R038  Shelf Space Analysis

**Priority:** Medium. Shelf-space analysis helps managers compare collection allocation with use and identify outliers, but it is a specialized planning tool.

The system must provide shelf-space analysis that compares, side by side, for each material genre and format, the percentage of total circulations, the percentage of the collection, and the percentage of total shelf space so users can identify differences and outliers, with views by branch and for the library system, selectable date ranges such as Q1 or Q2, collection percentages based on item counts, circulation percentages based on checkouts, and shelf-space estimates based on item dimensions or item count when dimensions are unavailable.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R039  Batch Item Transfers

**Priority:** Medium. Batch transfers reduce effort when moving large groups of items, but staff can still perform transfers through other processes if this workflow is deferred.

Authorized staff must be able to transfer selected batches of items between branches and other destinations, including mobile libraries, outreach programs, warehouses, book sales, and event locations, by changing item locations or generating printable pull lists identifying items selected for transfer; the operation must process approximately 9.6 million items without excessive database locking.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R040  Save and Share Queries

**Priority:** Medium. Saving and sharing queries reduces repeated setup for recurring reports, though staff can still run reports by recreating query criteria.

The system must allow staff to save queries, including transfer-candidate queries, reuse them for repeated reporting activities including monthly reuse, and make saved queries available for reuse or sharing.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R041  Select Records for Actions

**Priority:** Medium. Manual selection helps staff refine transfer candidates before acting, but transfer workflows can function without this added selection step.

The system must allow staff to manually select individual records from query results for subsequent administrative actions, including selecting individual titles or items from transfer-query results before executing a transfer, such as selecting 25 items from 100 candidates.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R042  Transfer Candidate Queries

**Priority:** Medium. Transfer-candidate queries help staff identify suitable items using several sources' requested criteria, while transfers can still be initiated through other selection methods.

Staff must be able to query for candidate items for transfer using criteria such as genre, collection area, and circulation inactivity, including items that have not circulated for six months.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R043  Transfer Confirmation Preview

**Priority:** Medium. A preview and confirmation reduce accidental transfers by showing the affected count and locations before execution.

Before execution, the system must show a transfer preview containing the item count and source and destination locations and require staff confirmation.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R044  Transfer Location Updates

**Priority:** Medium. Updating item locations is needed to keep records accurate when a transfer occurs, although it supports a secondary operational workflow.

The system must update the location field and associated item records for selected items moved to a new location.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R045  Transfer Reversion

**Priority:** Medium. Configured reversion helps return items after temporary placements or specified events, but transfers can function without automated returns.

The system must return transferred items to their original locations after a configured period or configured event, including a status change to sold or returned or checkout at the destination.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R046  Batch Item Status Conversion

**Priority:** Medium. Batch status changes can reduce repetitive item-maintenance work across the branches, but the reporting and transfer workflows can operate without this specific action.

The system must provide a workflow that converts many selected items from one status to another in a single batch, such as changing 100 missing items to discard/weed.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R047  Data Quality and Integrity Reports

**Priority:** Medium. Periodic data-quality reports help staff find catalog and item-record problems, but they support maintenance rather than the system’s core reporting workflows.

The system must provide periodic data-quality reports identifying invalid item types, excessively long call numbers, bibliographic records without items, and other data problems.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R048  Hold and Transit Reports

**Priority:** Medium. Hold and transit reports help staff coordinate material movement and resolve delays, though they serve a specialized operational workflow.

The system must provide periodic reports for records with holds, item-level holds, in-transit items with holds, and overdue transit.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R049  Item Change and Inventory Reports

**Priority:** Medium. Item change and inventory reports help staff track collection activity and investigate record changes, but they are not the only way to meet management reporting needs.

The system must provide reports on items that were added, deleted, edited, counted, or created within a specified date range.

**Sources:** D07 (conversations/conv_pines022_deletions.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R050  Item Circulation and Status Reports

**Priority:** Medium. Reports on inactive, last-copy, and missing items support collection management, but this periodic report suite is narrower than the overall reporting purpose.

The system must provide periodic reports for items not checked out for a configurable period, last copies, and missing items.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R051  Confirmed Purge Deletion

**Priority:** Medium. A separate confirmation helps prevent unintended destructive purges, although deletion itself is a specialized workflow.

The system must require a separate confirmation before executing purge deletions.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml)

### R052  Deletion Audit Recording

**Priority:** Medium. Recording completed and denied deletions gives administrators a useful accountability trail, although the reporting system can function without deletion auditing.

The system must record completed and denied deletion attempts, including who performed or attempted each deletion, the record type, record ID, timestamp, user branch, library system, and, where required, the deletion reason.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D07 (conversations/conv_pines022_deletions.eml), D15 (interview_cataloging_2009-05-08.txt)

### R053  Protected Purge Reports

**Priority:** Medium. Read-only candidate reports prevent an inspection step from altering records, providing a valuable safeguard for purge work.

Reports identifying purge candidates must be read-only and must not delete or modify candidate records.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml)

### R054  Purge Candidate Identification

**Priority:** Medium. Customizable purge criteria help staff identify stale or unsuitable records consistently, though identification can be delivered after core reporting.

The system must identify item records eligible for purging using customizable status, duration, and circulation criteria, including missing, discard/weed, or damaged status, time in status, and no circulation for a specified period; criteria must support Boolean combinations such as missing for six months and no circulation for two years.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R055  Check-In Method Reports

**Priority:** Medium. Check-in method counts help managers compare service channels and workload, but are a specialized part of circulation analysis.

The system must provide check-in reports that count check-ins individually and cumulatively by book drop, terminal, staff or user processing, and self-service.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R056  Circulation Attribute Reports

**Priority:** Medium. Reports using patron and item attributes enable useful segmented circulation analysis, though the system can operate without every listed dimension.

The system must provide circulation reports using patron contact information, circulation modifiers, categories, patron county, home branch, and age, as well as item Dewey classification, shelving location, and MARC fields.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R057  Inactive Patron Reporting

**Priority:** Medium. The inactive-patron report can support targeted outreach and workload assignment, but this specialized workflow is not necessary for other management reporting.

The system must provide an inactive patron report for patrons with no circulation and no electronic activity during a configurable preceding period, where the threshold supports any number of days including 30, 90, 180, and 365 and electronic activity includes OPAC or patron-account logins, online holds, online renewals, and integrated digital-resource access. The report must separate patrons with outstanding fines, allow exclusion of patrons marked do-not-disturb, VIP patrons, staff members, and patrons who opted out of communications, include each patron's current mailing address, support CSV export for upload to an outreach system, and list or group results by configurable organizational scopes including the library system, home branch, and county so users can see system totals and assign work to branches.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R058  Null and Blank Field Inclusion

**Priority:** Medium. Including null and blank values helps prevent incomplete demographic data from silently skewing patron reports, though it is an accuracy safeguard within those reports.

Patron queries and reports must include records and values with null or blank fields, including patrons whose optional demographic fields are null or blank, rather than silently excluding them.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R059  Overdue and Volume Reports

**Priority:** Medium. Overdue and circulation-type reports help staff monitor circulation patterns, but they are a subset of the wider reporting scope.

The system must provide reports for overdue items, non-cataloged circulation, and total circulation by type.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R060  Patron Additions and Status

**Priority:** Medium. Addition, expiration, and status reports help staff manage patron accounts, although these administrative reports are not required for every management workflow.

The system must provide patron reports showing additions by month, expiration date, and barred or inactive status.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R061  Patron Counts and Demographics

**Priority:** Medium. Patron counts by demographic and location help branches understand who they serve, but they are one analytical capability within the broader reporting system.

The system must provide a patron report with total counts and counts by age, county, city, ZIP code, and home branch.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R062  Patron Report Filtering

**Priority:** Medium. Filtering patron reports by demographic and organizational attributes supports useful analysis, but the reports interface can still operate without these specific filters and grouping options. (D08 calls these reports essential)

The system must let users filter and group patron queries and reports by age range derived from birth date, ZIP code, county, home branch, patron type, and preferred language, combine filters with AND and OR logic and applicable circulation conditions, and configure age ranges separately for each patron report, including ranges such as 0–5, 6–10, 11–15 or 0–6, 7–12, 13–17, 18–24, and 25–34.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt)

### R063  Report Export Formats

**Priority:** Medium. Excel-compatible, HTML, and CSV output lets staff use results in common tools, but the reports remain usable in the system without each format.

Report output must be available in Excel-compatible, HTML, and CSV formats, with Excel exports avoiding unnecessary duplicate rows.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R064  Acquisitions Cataloging Integration

**Priority:** Medium. Using the enterprise acquisitions and cataloging data avoids duplicating those functions, while those workflows remain outside this system's scope.

Management processes must read and use the data structures and functionality of the enterprise Library Automation System, including Acquisitions and Cataloging, without managing those functions.

**Sources:** D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R065  Anonymized Demographic Statistics

**Priority:** Medium. Anonymized demographic statistics support planning while protecting patron identity, a useful cross-source analysis capability.

The system must provide anonymized transaction and patron statistics by geographic region, ZIP code, age range, and other useful demographic attributes without disclosing personally identifiable information.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R066  Bibliographic Reports

**Priority:** Medium. Bibliographic reports help staff review records and identify missing data, but are one component of the wider management-reporting suite.

The system must provide bibliographic reports for record counts, edited records, records added by user and branch, records without attached volumes or items, and records missing specified MARC fields.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R067  Bills Report Suite

**Priority:** Medium. Bill and debt reports support financial follow-up, but are a specific part of the wider financial reporting capability.

The system must provide reports for current patron bills, detailed payments, forgive/work/goods payments, voids, and aged debt with detailed aging periods.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R068  Board and Executive Reports

**Priority:** Medium. Predefined board and executive reports save leadership time, but those users can still obtain oversight information through other reports.

The system must provide predefined reports for library boards and executive users.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R069  Branch Operation Without Vendor Data

**Priority:** Medium. Branch operations that continue without vendor data improve resilience, though this is a continuity enhancement rather than a prerequisite for core reporting.

Management processes must continue to function at a branch when vendor data is unavailable.

**Sources:** D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R070  Centralized Branch Reporting Service

**Priority:** Medium. A centralized reporting service can give branches a consistent source of information, but the system can provide useful reports without this particular service architecture.

The system must provide a centralized service that accepts input from and serves multiple branches as a single reporting source of truth.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R071  Configuration Migration

**Priority:** Medium. Migrating templates, permissions, and queries reduces configuration rework across environments, but the environments can function without automated migration.

The system must export and import report templates, permission settings, saved queries, and other configuration between development, training, and production environments.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R072  Consortium Statistical Reports

**Priority:** Medium. Consortium-wide statistical reports let the global administrator evaluate network performance, but are a specific reporting scope.

The Global System Administrator must be able to generate statistical reports for the entire library consortium.

**Sources:** D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt)

### R073  Demographic Statistics Preservation

**Priority:** Medium. Preserving demographics after removing patron identifiers supports useful aggregate analysis without compromising privacy, but the reports can operate without that retained detail.

The system must preserve useful demographic statistics when removing personally identifying information from retained transaction data.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R074  Detailed Transaction Retention

**Priority:** Medium. Configurable detailed transaction retention supports historical analysis and retention planning, but its value depends on the reporting period each use case requires.

The system must retain detailed transaction history for a configurable number of days.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R075  Director-Level Financial Reports

**Priority:** Medium. Director-level financial summaries help leadership monitor balances, charges, waivers, and payments, but they are a defined subset of financial reporting.

The system must provide financial reports suitable for library directors and other users requiring director-level financial information, including patron balances by patron, home branch, and library system, fines and charges by period and charge type, waived fines by period and branch, and payments by period, collecting branch, payment channel, and payment type.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R076  Email Report Delivery

**Priority:** Medium. Email delivery makes reports easier to distribute to recipients, but users can still access and export reports through the interface.

The system must deliver reports by email and allow users to enter recipients.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R077  Environment Separation

**Priority:** Medium. D10 marks environment separation Medium Priority, and safe training and development spaces are useful without being prerequisites for live reporting. (D10 marks CO-3 Medium Priority)

The product must provide separate development and training environments, including a training environment safe for experimentation without affecting production.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R078  Error Feedback

**Priority:** Medium. D10 marks UD-4 Medium Priority, and detailed feedback helps administrators diagnose query problems but is not required for basic reporting. (D10 marks UD-4 Medium Priority)

The system must provide high-level error reporting and low-level query-specific feedback to administrators, including relevant table, field, and error type when available.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R079  Financial Record Association

**Priority:** Medium. Associating financial events with patron and item records enables useful reconciliation and joins, but is a specialized data capability.

The system must associate fines, charges, waivers, payments, and ecommerce transactions with relevant patron and item records and support joins between patron and item financial data.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R080  Georgia Annual Report

**Priority:** Medium. A Georgia Annual Report supports state reporting needs, though it is a specific report rather than a general system capability.

The system must provide the Georgia Annual Report as a report for state reporting.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R081  Hold Report Suite

**Priority:** Medium. Hold reports help branches monitor requests and identify stale or unfilled holds, but are a defined circulation subdomain.

The system must provide hold reports for purchase alerts, items sent or received for holds, IntraPINES loans, unfilled holds, annual totals, and stale holds remaining beyond the permitted pickup period.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R082  Immediate Desk Payment Reflection

**Priority:** Medium. Immediate reflection helps staff rely on current payment information, while delayed updates would not prevent the system from providing other financial reports.

A payment made at a staff desk must be reflected immediately.

**Sources:** D11 (email_financial_reports.eml)

### R083  Indefinite Transaction Aggregate Retention

**Priority:** Medium. Retaining aggregates supports long-term trend analysis and applicable retention needs, but aggregate retention can be added later without blocking current reporting workflows.

The system must retain monthly and annual transaction aggregates indefinitely where required.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R084  OPAC Data Querying

**Priority:** Medium. Querying OPAC-created holds and circulation makes patron-interface activity available to management reports without altering operational records.

Management processes must query patron-interface data created in the OPAC, including holds and circulation, without modifying that data.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R085  Patron Behavior Statistics

**Priority:** Medium. Renewal and return-speed statistics help assess patron behavior and material use, but are analytical additions to core reporting.

The system must produce statistics about patron behavior and material use, including return speed, renewal likelihood, renewal rates, and the percentage of branch checkouts that are renewals.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R086  Pivot Table Output

**Priority:** Medium. Pivot-table output helps users summarize and explore results, and multiple sources request it as a useful analysis format.

The reporting system must provide pivot-table output.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R087  Process Documentation

**Priority:** Medium. D10 marks process documentation Medium Priority, and it helps administrators understand imports, validation, and reporting without blocking system operation. (D10 marks UD-2 Medium Priority)

The product must document major processes, including bibliographic import and export, validation against internal and external authority sources, and standard reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R088  Query Criteria Display

**Priority:** Medium. Showing query selections and date criteria makes results easier to interpret and reproduce, though it does not produce the underlying report data.

Report results must display the query selections, report name, and selected date criteria used to produce them.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt)

### R089  Query Designer Administration

**Priority:** Medium. Administrative controls over query fields and tools help manage access and usability, but the query designer remains useful without extensive configuration.

The system must allow administrators to control the tables, fields, and tool access available in the query designer.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R090  Real Time Reporting

**Priority:** Medium. Current-data reporting helps staff see recent activity, but some reporting needs can be met using scheduled or historical data.

The system must support reports using current data in real time, including activity during busy periods.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R091  Report Cancellation

**Priority:** Medium. Cancelling queued or running reports helps reclaim resources and correct mistaken submissions, with four sources requesting the control.

Users must be able to cancel scheduled, queued, or currently running reports, including during processing.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R092  Report Permission Administration

**Priority:** Medium. Fine-grained report permissions help administrators safely share data and tools, complementing the broader access-control capability.

The system must provide fine-grained permissions for creating, cloning, running, and accessing reports, filters, data sets, and shared folders, including administrator-controlled shared folders that allow or prohibit specific report access.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R093  Report Queue Monitoring

**Priority:** Medium. Queue visibility helps users understand delays and failures, and five sources request this useful operational transparency.

Users must be able to see report queue contents, position, number of reports ahead, submission time, and status such as waiting, running, completed, or failed.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R094  Report Queue Prioritization

**Priority:** Medium. D12 describes prioritization as crucial, and controlling queue order can help time-sensitive reports finish ahead of resource-heavy work. (D12 describes report prioritization as crucial)

Authorized users or processes must be able to prioritize selected report types so important reports execute ahead of lower-priority or resource-consuming reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt)

### R095  Report Scheduling

**Priority:** Medium. Scheduling recurring reports reduces repeated staff work and is requested by three sources, but reports can also be run manually.

Users must be able to run reports as soon as possible or schedule them hourly, daily, weekly, monthly, or yearly, including recurring reports that can be edited by changing selections or email addresses.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R096  Report Template Controls

**Priority:** Medium. Shared templates let administrators standardize reports while giving staff controlled flexibility, a useful capability requested by four sources.

Authorized administrators must create shared report templates that staff can run as-is or modify within controlled limits on filters and display fields, without compromising intended results or exposing deleted items; authorized users must be able to clone templates and edit permitted display options.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R097  Run Canned Reports by Period

**Priority:** Medium. Running canned reports for common prior periods supports routine evaluation, while users can still run reports using other available date criteria.

Users must be able to run product-delivered canned reports using yesterday's, last week's, last month's, or last year's data.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R098  Staff Authentication

**Priority:** Medium. Individual authentication preserves accountability for staff activity, while badge login is an optional convenience rather than a core reporting feature.

The system must support optional employee-card or badge login and individual username-and-password login as a fallback; every login must identify the individual staff member and card login must not bypass individual authentication.

**Sources:** D10 (early_draft_srs_galecia.txt), D13 (email_staff_login.eml)

### R099  State Aid Statistics

**Priority:** Medium. State Aid statistics help users prepare a specific reporting submission, but this report can be added separately from core management analytics.

The system must provide Application for State Aid statistics as a report for state reporting.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R100  Track Uncataloged Materials

**Priority:** Medium. Tracking uncataloged materials makes their use visible before catalog records exist, which helps libraries manage these materials but serves a narrower workflow.

The system must track uncataloged items, including paperback books and children's board books, before catalog records exist.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R101  Transaction Analysis Grouping

**Priority:** Medium. Grouping transactions across operational dimensions supports useful trend analysis, but the system can provide other management reports without every grouping.

The system must group transactions for analysis by hour, terminal, branch, library system, transaction type, and selected dimensions.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R102  Transaction Summary Reports

**Priority:** Medium. Summaries by branch and patron grouping help managers compare checkouts and holds, but are a specific set of transaction views.

The system must report holds placed, holds filled, and checkouts by patron, branch, selected branch groups, library system, and county, including checkout and hold subtotals and hold states such as active, frozen, and frozen-until.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R103  Vendor Data Exchange

**Priority:** Medium. Standard-format exchange with vendor systems supports connected management workflows, but reporting can still function when those integrations are unavailable.

Management processes must exchange standard-format data with vendor websites through published APIs or automated transfers, including USMARC21 and EDIFACT.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R104  Workstation Transaction Reports

**Priority:** Medium. Workstation and staff transaction reports support operational review, but cover a narrower audit use than general circulation reporting.

The system must report transactions for a specified date and time, workstation, or staff member.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R105  Separate Item Dates

**Priority:** Medium. Separating edit, circulation, and check-in dates prevents staff from misinterpreting item history, and three sources request the distinctions.

Item reports must expose last-edit date, last-circulation date, and check-in date and time as separate fields; last-edit date changes only when the item is edited, and renewal timestamps must not be treated as check-ins or edits.

**Sources:** D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

## Requirements: Low priority

### R106  Transfer Audit History

**Priority:** Low. Transfer history can reveal movement patterns, but the request appears in one source and is not needed to execute or track a transfer.

The system must record transfer history for each item, including enough history to determine patterns such as five transfers within one year.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R107  Transfer Delay Alerts

**Priority:** Low. Delay alerts can improve follow-up on individual transfers, but notifications are not required to perform or report transfers.

The system must notify designated staff when a transfer is delayed or encounters an issue.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R108  Transfer Undo

**Priority:** Low. Undo helps recover from staff mistakes, but is a single-source safeguard that can be deferred in favor of prevention and auditability.

Staff must be able to undo an erroneous transfer after it has been initiated or completed.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R109  Transit Label Generation

**Priority:** Low. Printable barcode labels can aid physical transit handling, but they are a convenience for one part of the transfer process.

The system must generate printable barcode transit labels for transferred items.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R110  Invalid Patron Branch Report

**Priority:** Low. A report on patrons with invalid home branches helps correct a specific data issue, but this narrow check is not central to system use.

The system must provide a periodic report for patrons with invalid home branches.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R111  Deletion Data Analysis

**Priority:** Low. Analyzing deletion records can help identify patterns after an audit trail exists, but it is a secondary capability built on the audit function.

The system must support counts and queries of deletion data by branch, library system, date range, user, record type, and highest-volume users.

**Sources:** D07 (conversations/conv_pines022_deletions.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R112  Orphan Record Deletion

**Priority:** Low. Quick deletion of orphaned entries streamlines cleanup, but the request is a specialized utility appearing in three sources.

The system must provide a quick method to delete volume entries with their associated copy entries and records with no attached items.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R113  Patron Surveys and Notes

**Priority:** Low. Survey answers and notes may inform selected patron analyses, but this specialized and potentially sensitive information is not needed for most reporting workflows.

The system must provide patron reports showing survey answers and notes.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R114  Staff Account Date Reports

**Priority:** Low. Password-date reporting may help administrators monitor staff accounts, but it is a narrow administrative convenience rather than a central management-reporting need.

The system must provide reports showing staff-account password-change dates and password-expiration dates.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R115  Combine Multiple Report Outputs

**Priority:** Low. Combining several canned reports into one document is a convenient presentation option, but users can still run and review each report separately.

Users must be able to select multiple product-delivered canned reports and combine their output in one document.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R116  Comparative Report Output

**Priority:** Low. Comparative columns add context to selected reports, but the request appears in one source and is a report-format enhancement.

Reports must support comparative columns such as last month's circulation, the previous month's circulation, percentage differences, and the corresponding month of the previous year.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R117  Distribute Materials Rapidly

**Priority:** Low. Rapid distribution with minimal branch labor would improve handling of uncataloged materials, but it is a workflow convenience rather than a reporting-system foundation.

The system must support rapid distribution of uncataloged materials with minimal branch labor.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R118  File Based Filtering

**Priority:** Low. Uploading filter values can simplify large selection tasks, but is a specialized input method requested by two sources.

Users must be able to upload a text file containing values such as barcodes or TCNs and use those values as report filters.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R119  Financial Information Updates

**Priority:** Low. Easy financial updates are useful to authorized staff, but updating financial records is peripheral to the management-reporting purpose.

Authorized staff must be able to update financial information easily.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R120  High Balance Queries

**Priority:** Low. High-balance queries help staff find accounts meeting a chosen threshold, but are a narrow financial-reporting convenience.

Staff must be able to query patron accounts with balances above a user-specified dollar amount.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R121  In House Use Reports

**Priority:** Low. In-house-use reporting measures a narrow category of activity and is requested by one source.

The system must report non-cataloged in-house use by month and cataloged in-house use.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R122  MARC Row Consolidation

**Priority:** Low. Consolidating MARC fields onto one row simplifies a specific kind of report, but is not needed for general bibliographic reporting.

Reports must retrieve specified MARC fields and display them on one row even when the fields are stored across multiple rows.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R123  Notice Reports

**Priority:** Low. Notice counts answer a narrow circulation question and are requested by one source, so they can follow broader report capabilities.

The system must report pre-overdue notices, overdue notices, and holds notices sent.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R124  Report Quick Access

**Priority:** Low. Quick access and hover descriptions make reports easier to find, but are interface refinements rather than core reporting functions.

The reporting interface must provide quick access to canned reports and templates, with hover or popup descriptions for report titles and templates.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R125  Report Recipient Address Book

**Priority:** Low. An address book is a convenience for repeated email delivery, since users can enter recipient addresses without it.

The system must provide an address book for users to store regularly used email addresses.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R126  Survey Name Filtering

**Priority:** Low. Selecting surveys by name is a usability improvement for a narrow filtering task that can be handled through identifiers.

Users must be able to select a survey by name for filtering, with the system resolving the name to its survey identifier internally.

**Sources:** D10 (early_draft_srs_galecia.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

## Blacklist

None.

## Open issues

- **too broad** (R087): This bundles documentation of bibliographic import/export, authority validation, and standard reports. Each is an independently testable documentation capability.
- **too narrow** (R097, R028): R097 is the detail: it specifies prior-period choices for running canned reports. R028 is the parent capability, which already includes product-delivered canned reports.
- **too narrow** (R118, R016): R118 is a specific way to supply filter values for queries. R016 is the parent query-designer capability.
- **too narrow** (R126, R113): R126 is a specific survey-selection filter for patron reports showing survey answers and notes. R113 is the parent survey-report capability.
- **possibly missed**: “Transaction-Safe Batch Transfers” (D04): The system must execute batch item transfers with transaction safety so that updates are applied consistently and do not leave partially completed transfer operations.
- **possibly missed**: “Concurrent Report Execution” (D14): Users must be able to select multiple reports to run concurrently at the same time.
- **possibly missed**: “Patron Interest Analysis” (D17): The reports interface must enable analysis of patrons' interests in support of management planning, evaluation, and oversight.
- **possibly missed**: “Collection Distribution Analysis” (D17): The reports interface must enable analysis of branch capacity and the optimal distribution of the collection across branches.
- **possibly missed**: “Staff Productivity Analysis” (D17): The reports interface must enable analysis of staff productivity for management planning, evaluation, and oversight.
- **possibly missed**: “Financial Transaction Verification” (D17): The reports interface must support tracking and verifying financial transactions for management oversight.

## Coverage

| Document | Path | Requirements | Blacklist |
| --- | --- | --- | --- |
| D01 | conversations/conv_pines014_material_volume.eml | R001, R032, R033, R090 |  |
| D02 | conversations/conv_pines015_capacity_interface.eml | R002, R034, R035, R063 |  |
| D03 | conversations/conv_pines016_shelf_space.eml | R001, R003, R020, R038 |  |
| D04 | conversations/conv_pines018_item_transfer.eml | R004, R039, R040, R041, R042, R043, R044, R045, R106, R107, R108, R109 |  |
| D05 | conversations/conv_pines019_020_missing_intransit.eml | R001, R006, R007, R008, R020 |  |
| D06 | conversations/conv_pines021_item_purging.eml | R001, R005, R006, R016, R020, R028, R046, R050, R051, R052, R053, R054, R066, R112 |  |
| D07 | conversations/conv_pines022_deletions.eml | R049, R052, R111 |  |
| D08 | conversations/conv_pines023_patron_characteristics.eml | R001, R009, R020, R034, R056, R058, R061, R062 |  |
| D09 | conversations/conv_pines024_inactive_patrons.eml | R011, R057, R063 |  |
| D10 | early_draft_srs_galecia.txt | R001, R002, R003, R004, R005, R006, R007, R008, R009, R010, R011, R012, R013, R014, R015, R016, R017, R018, R019, R020, R021, R022, R023, R024, R025, R026, R027, R028, R029, R030, R032, R033, R034, R035, R036, R037, R038, R039, R040, R041, R042, R044, R045, R046, R047, R048, R049, R050, R054, R055, R056, R057, R058, R059, R060, R061, R062, R063, R064, R065, R066, R067, R068, R070, R071, R072, R073, R074, R075, R076, R077, R078, R079, R080, R081, R083, R084, R085, R086, R087, R088, R089, R090, R091, R092, R093, R094, R095, R096, R097, R098, R099, R100, R101, R102, R103, R104, R110, R111, R112, R113, R114, R115, R116, R117, R118, R119, R120, R121, R122, R123, R124, R125, R126 |  |
| D11 | email_financial_reports.eml | R005, R012, R017, R018, R024, R036, R075, R079, R082, R119, R120 |  |
| D12 | email_report_features.eml | R001, R004, R009, R011, R014, R016, R023, R031, R065, R068, R073, R080, R086, R088, R089, R092, R093, R094, R096 |  |
| D13 | email_staff_login.eml | R004, R098 |  |
| D14 | evergreen_reference_2009.txt | R001, R004, R005, R006, R010, R011, R013, R014, R015, R016, R019, R020, R022, R028, R032, R034, R036, R037, R049, R050, R056, R057, R058, R059, R060, R061, R063, R066, R067, R071, R076, R077, R081, R086, R088, R090, R091, R092, R093, R094, R095, R096, R102, R105, R113, R114, R118, R124, R125 |  |
| D15 | interview_cataloging_2009-05-08.txt | R001, R005, R006, R007, R008, R020, R033, R037, R038, R039, R040, R041, R042, R044, R045, R046, R047, R050, R052, R054, R059, R066, R100, R105, R111, R112, R117 |  |
| D16 | interview_sysadmin_2009-05-10.txt | R004, R011, R013, R015, R019, R020, R021, R022, R026, R029, R030, R071, R077 |  |
| D17 | meeting_minutes/meeting_2009-03-15_minutes.txt | R001, R002, R014, R020, R034, R035, R036, R064, R072 |  |
| D18 | meeting_minutes/meeting_2009-07-20_minutes.txt | R001, R002, R003, R004, R005, R006, R007, R008, R011, R013, R014, R015, R019, R020, R021, R022, R025, R026, R029, R030, R034, R035, R036, R038, R047, R064, R068, R070, R071, R075, R077, R078, R084, R087, R103 |  |
| D19 | meeting_tech_subcommittee_2009-06-30.txt | R004, R013, R019, R020, R021, R022, R025, R026, R030, R032, R058, R063, R064, R069, R070, R071, R077, R078, R084, R087, R090, R091, R103, R126 |  |
| D20 | survey_results_2009.txt | R001, R009, R010, R011, R016, R022, R028, R032, R040, R041, R042, R044, R045, R055, R058, R063, R065, R074, R076, R083, R085, R086, R090, R091, R092, R093, R095, R096, R101, R102, R105, R111, R122 |  |
