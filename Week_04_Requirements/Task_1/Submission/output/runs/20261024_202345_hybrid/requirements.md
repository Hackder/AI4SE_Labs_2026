# Software Requirements Specification

This document specifies the requirements for Library Management Reporting System, derived by an agentic refinement network from 20 input documents. It contains 136 requirements and 6 blacklisted (discarded) items. Requirement numbers are assigned in document order, are unique within this document and are not stable across runs.

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
| Branch | A library location within a library system or consortium. |
| Consortium | A group of library systems or locations sharing the library automation and management reporting environment. |
| Item | A physical library copy represented by an item record. |
| MARC | Machine-Readable Cataloging, the record format used to represent bibliographic data. |
| OPAC | The Online Public Access Catalog through which patrons access library catalog services. |
| Patron | A person who uses a library's resources or services. |
| Report template | A reusable report definition with specified selection criteria and display options. |

## Requirements: High priority

### R001  Current Last-Copy Reports

**Priority:** High. D06 and D15 explicitly call the last-copy report critical, and staff across the consortium depend on identifying the sole remaining copy at branch and consortium scopes. (D06 marks the last-copy report critical; D15 calls it critical)

The system must provide reports identifying Items that are the only copy within a selected scope, including an individual Branch and the entire Consortium.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R002  Administer Report Permissions

**Priority:** High. Fine-grained report permissions protect sensitive datasets across multiple sources and complement the system's stated role-based access controls.

The system must provide fine-grained, role-administered permissions controlling who may create, clone, run, and access reports. Administrators must be able to create shared folders that allow or disallow access to specific reports and ad hoc reports on specified data sets.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D20 (survey_results_2009.txt)

### R003  Assistive Technology Access

**Priority:** High. D10 marks assistive technology support High Priority, while D16 calls accessibility non-negotiable and D18 describes Section 508 compliance as mandatory. (D10 marks this High Priority; D16 calls accessibility non-negotiable and D18 calls Section 508 compliance mandatory)

The system must support screen readers, screen-magnification software, and other assistive technologies, including JAWS, NVDA, and ZoomText, and comply with Section 508 accessibility requirements.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R004  Client Access Platforms and Browsers

**Priority:** High. D10 marks Client Access Platforms as High Priority, making support for the specified client access methods a stated high-priority source requirement. (D10 marks Client Access Platforms as High Priority and Supported Web Browsers as Medium Priority)

The system must be accessible through a web browser or a Windows-compatible client; when accessed through a web browser, it must support Microsoft Internet Explorer version 6.0 or later and Mozilla Firefox version 2.0 or later.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R005  Consortium Scale Support

**Priority:** High. D10 marks consortium-scale support High Priority, and the specified locations, circulation, and processing volumes define the system's operating context. (D10 marks this High Priority)

The system must support a library consortium with 286 locations, 17 million annual circulations, and purchasing or processing more than 900,000 items per year.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R006  Financial Audit Compliance

**Priority:** High. The requirement explicitly calls for compliance with applicable state, county, and municipal auditing requirements, so financial reporting must meet those obligations.

The system's reports and archived data must comply with standard accounting practice and applicable state, county, and municipal auditing requirements.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R007  Item Status Reports

**Priority:** High. The fixed Last Copy Reports requirement depends on identifying last copies, and the requested item-status reports also cover missing and in-transit items used in collection management.

The system must provide periodic management reports identifying items that have not been checked out for a specified number of days, items with item-level holds, in-transit items with outstanding holds, last copies, and missing items.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R008  Multi-Record Query Interface

**Priority:** High. D10, D12, and D18 request querying across major record types, and without a flexible query interface users would be unable to build many of the system’s core reports.

The system must provide a user-friendly query-design interface for bibliographic, item, patron, transaction, and financial records. Users must be able to select fields, choose values from picklists, select regular expressions from a dropdown, and use Boolean operators.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R009  Non-Disruptive Report Processing

**Priority:** High. D10 marks open-hours report processing High Priority, and D14, D16, and D18 also address avoiding disruption to live services. (D10 marks the open-hours operating requirement High Priority)

The system must process searches and reports during open hours without disrupting other system functions, including circulation and patron access to the OPAC. Long-running reports must be capable of background processing or other isolation from operational activity.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R010  Online System Help

**Priority:** High. D10 marks online system help High Priority, and the requirement is repeated across five sources, including accessibility for screen-reader users. (D10 marks this High Priority)

The system must provide online HTML help that is hierarchical, cross-linked, and describes and illustrates system functions. Staff must be able to find help without leaving the system, and the help must be accessible to screen-reader users.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R011  Payment Audit Ledger

**Priority:** High. D11 calls the financial audit trail critical, and finance staff need payment-to-charge detail to trace and reconcile accounts. (D11 calls the financial audit trail critical)

The system must maintain a ledger of patron payments identifying the specific charges to which each payment was applied, so finance staff can trace payments and reconcile accounts.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D20 (survey_results_2009.txt)

### R012  Preserve OPAC Functionality

**Priority:** High. D10 marks OPAC preservation High Priority, and D16 calls separation from OPAC functionality critical because reporting must not impair patron access. (D10 marks this High Priority; D16 calls OPAC separation critical)

Management reporting functionality must not constrain or adversely affect the functionality or performance of the Online Public Access Catalog.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R013  Privacy-Protecting Transaction Archives

**Priority:** High. D12 states that State law requires transaction retention and privacy protection, making the archive behavior a compliance obligation. (D12 states that State law requires this transaction retention and privacy protection for compliance)

The system must archive transaction data for the period required by applicable law while protecting patron privacy by removing personally identifiable information and retaining useful demographic statistics.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R014  Record Data Specifications

**Priority:** High. D10 marks complete record data specifications High Priority, and these details support administration and interpretation across the system's record types. (D10 marks this High Priority)

Product documentation must provide complete data specifications for authority, bibliographic, order, item, hold/request, and other records maintained or accessed by the Management Processes, including field names, data types, and relationships.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R015  Relational Database Support

**Priority:** High. D10 marks relational database support High Priority, and the requirement is repeated across four sources for reporting against relational data. (D10 marks the relational database requirement High Priority)

The system must use and work with a fully relational database structure and support reporting queries across relational data. It must not require a denormalized reporting schema synchronized with the live database.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R016  Role-Based Access Control

**Priority:** High. D10 marks role-based access High Priority, and the requirement is repeated in several sources for controlling staff and administrator permissions. (D10 marks this High Priority)

The system must control user rights through security groups or roles assigned to individuals, workgroups, and staff groups, and allow administrators to manage permissions through role assignment. Roles must support access appropriate to staff, managers, local administrators, and global administrators.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D13 (email_staff_login.eml), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R017  Server Operating Environment

**Priority:** High. D10 marks Linux or Solaris operation High Priority, and D16 and D18 also specify those server environments. (D10 marks this High Priority)

The system must operate on Linux or Solaris servers, including the Linux and Solaris environments used for production and disaster recovery.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R018  Standards-Compliant HTML

**Priority:** High. D10 marks standards-compliant HTML High Priority, with three other sources also specifying the output requirement. (D10 marks this High Priority)

The system must produce standards-compliant HTML for web interfaces, help content, and report output.

**Sources:** D10 (early_draft_srs_galecia.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R019  Transit Location Reports

**Priority:** High. D18 explicitly records in-transit item reports as critical, and delivery coordination depends on knowing sending and destination locations. (D18 records in-transit item reports as critical)

The system must report items in transit by sending library and destination library, and provide reports of items currently in transit between locations for delivery coordination.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R020  Enforce Archive Retention

**Priority:** High. The requirement specifies retention periods required for audits, including seven years where state and local rules apply, making enforcement a compliance obligation.

The system must enforce data-archiving retention policies required for audits, including a seven-year retention period where applicable under state and local requirements.

**Sources:** D11 (email_financial_reports.eml), D12 (email_report_features.eml)

### R021  Read-Only OPAC Data Access

**Priority:** High. Read-only OPAC access protects patron-facing holds and circulation data from management-process changes, aligning with the multi-source requirement to preserve OPAC functionality.

Management Processes must interact with the OPAC patron interface by querying data such as holds and circulation transactions, without modifying that data.

**Sources:** D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

## Requirements: Medium priority

### R022  Material Volume Reporting

**Priority:** Medium. The reports support collection planning, but the system can provide its broader reporting workflows without every requested volume breakdown. (D01 calls this a key requirement)

The system must report material volume for a specified library at the current time or a selected historical point, separating new acquisitions, items on the shelf, items in circulation, and totals. Users must be able to break results down by categories such as total items, holds, adult fiction, and board books, customize categories, and report volume added in periods such as the last 30, 60, or 90 days.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R023  Branch Capacity Interface

**Priority:** Medium. D02, D10, and D17 support a branch-capacity overview that helps authorized staff compare locations, though reporting can operate without this specialized view.

The system must provide authorized users, including branch managers, with an overview of capacity across all Branches using a defined capacity measure, with the ability to drill into individual Branches, sort and filter by region, library type, and current load, view growth or shrinkage trends, and export the information to CSV.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R024  Shelf Space Usage Report

**Priority:** Medium. The comparisons help libraries make collection and shelf-space decisions, but they are a specialized analysis rather than a prerequisite for core reporting.

The system must compare, for each material genre and format, the percentage of total circulations, the percentage of the collection, and the percentage of total shelf space. Results must be available per library and system-wide, support date-range comparisons, and provide a side-by-side library comparison view. When shelf-space measurements are unavailable, the system must estimate shelf space using available item dimensions or item count as a proxy.

**Sources:** D03 (conversations/conv_pines016_shelf_space.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R025  Generate Transfer Pull Lists

**Priority:** Medium. Printable pull lists help staff retrieve selected items accurately, while transfers can still be coordinated through other procedures.

The system must generate printable pull lists identifying items selected for transfer so staff can retrieve them for movement.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt)

### R026  Preview Pending Transfers

**Priority:** Medium. A preview and confirmation reduce accidental transfer changes, but they support rather than enable the system's broader workflows.

Before applying a transfer, the system must show a preview of the proposed changes, including the number of items and their source and destination locations, and require confirmation before making the changes.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R027  Query and Select Transfer Candidates

**Priority:** Medium. D04, D15, and D20 request selecting transfer candidates, which makes transfer workflows more targeted but is not needed for reporting or other core functions.

The system must allow authorized staff to query candidate materials for transfer or other administrative processing using conditions such as material type, section, genre, or circulation history, and to manually select individual titles or items, including only part of a larger candidate set, for subsequent processing.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R028  Restrict Transfer Permissions

**Priority:** Medium. Role restrictions reduce the risk of unauthorized transfers, although this control applies to a narrower workflow than the system's general access management.

The system must restrict item transfers to authorized roles, including managers, administrators, or transfer coordinators, and prevent unauthorized staff from performing transfers.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R029  Revert Transferred Items

**Priority:** Medium. D04, D10, D15, and D20 request reversion to manage temporary transfers, but transfers can still be handled without automatic or criteria-based returns. (D04 calls automatic reversion important)

The system must automatically or manually return transferred Items to their original Branches after a configured period or when configured criteria are met, including time-based conditions and Item-status or destination events.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R030  Save Reusable Queries

**Priority:** Medium. Reusable queries reduce repeated setup for recurring tasks, although users can still run those tasks by recreating queries. (D04 calls saving queries for repeated use crucial)

The system must allow users to save queries for repeated use, including recurring transfer and reporting tasks.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R031  Transfer History Records

**Priority:** Medium. Transfer history helps staff audit movements and answer item-history questions, but it is specific to the transfer utility.

The system must retain transfer activity for audit and expose item transfer history so staff can review completed and reverted transfers and determine how often an item has moved.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R032  Transfer Item Batches

**Priority:** Medium. Staff need batch transfers to update item locations across the varied branches and other locations described in the sources, though other reporting and library operations can function without this utility.

The system must provide authorized staff with a utility to transfer batches of selected Items between Branches or other locations, including mobile libraries, outreach collections, warehouses, book sales, and event locations, and to update the selected Items’ location records to the transfer destination.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R033  Delayed Transit Items Report

**Priority:** Medium. The report helps staff investigate overdue transit items, while the broader system can operate without this particular exception report.

The system must generate one report of items that have remained in transit longer than a configurable number of days, with views per branch and system-wide. The report must combine transit-to and transit-from items, identify items with no arrival date and an overdue departure date, and allow sorting by due date. Seven days is suggested as the default threshold.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R034  Missing Damaged Items Report

**Priority:** Medium. Branch-level missing and damaged-item trends inform collection oversight, but this specialized report is not needed for other reporting workflows.

The system must provide a report of missing and damaged items by branch. The report must include item condition notes and support date ranges for trend analysis.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R035  Audit Record Deletions

**Priority:** Medium. Deletion audit records help administrators investigate changes across several source documents, but the system's reporting workflows can run without the audit feature.

The system must retain an audit record of successful deletions, including record type, record identifier, timestamp, user, and user location. This tracking must cover purge activity and other record deletions.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D07 (conversations/conv_pines022_deletions.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt), D20 (survey_results_2009.txt)

### R036  Batch Item Status Conversion

**Priority:** Medium. The three source documents support batch status changes as a useful collection-management workflow, while staff can still change item statuses individually without it.

The system must support converting multiple Items from one status to another in a batch, such as changing Items from missing to discard or weed.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R037  Confirm Purge Deletions

**Priority:** Medium. A separate confirmation step helps prevent accidental purge deletions, but it supports rather than enables candidate identification and review.

The system must require a separate confirmation step before executing purge deletions, distinct from identifying and reviewing candidates.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml)

### R038  Delete Itemless Records

**Priority:** Medium. Removing itemless records helps keep the catalog clean, although users can operate the reporting system without this cleanup method.

The system must provide a method to delete records that have no items attached during collection cleanup.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R039  Delete Volumes With Copies

**Priority:** Medium. Deleting volumes with associated copies supports collection cleanup, but it is a specialized maintenance operation rather than a general reporting dependency.

The system must provide a method to delete volume entries together with their associated copy entries during collection cleanup.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R040  Deleted Last-Copy Reports

**Priority:** Medium. Catalogers can use this report to update WorldCat when a former last copy is deleted, but the system can operate without this specialized historical report.

The system must provide reports identifying deleted Items that were previously the last copy in a library system or facility, supporting catalogers' WorldCat updates.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R041  Identify Purge Candidates

**Priority:** Medium. Customizable purge criteria help staff identify records for collection cleanup, but review and deletion workflows can be delivered separately. (D06 marks the last-copy report critical; this note does not apply to purge-candidate identification)

The system must identify item records eligible for purging using customizable, combinable criteria, including status (such as missing, discard/weed, or damaged), time spent in a status, and time since last circulation.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R042  Status Conversion Assistance

**Priority:** Medium. Requested in three source documents, this workflow would help staff identify items for status conversion, while the conversion task itself can be handled through other means.

The system must provide a report or workflow to assist with converting multiple Items from one status to another.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R043  Filter Patron Reports

**Priority:** Medium. D08 and D10 request configurable patron filters that support program planning, while the source’s emphasis on importance does not make this capability necessary for system operation. (D08 describes these reports as essential for program planning)

The system must allow patron queries and reports to be limited by age ranges calculated from Patrons' birth dates, ZIP code, county of residence, home Branch, patron type, and preferred language. Users must be able to configure the age brackets used for filtering, including user-defined brackets such as 0–5, 6–10, and 11–15, and combine these filters with other conditions using AND and OR logic.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt)

### R044  Group Patron Reports

**Priority:** Medium. D08 and D10 request demographic groupings and aggregates that support program planning, but the system can run without this specialized analysis. (D08 describes these reports as essential for program planning)

The system must group patron queries and reports by age ranges calculated from Patrons' birth dates, ZIP code, county of residence, home Branch, patron type, and preferred language, using configurable age brackets such as 0–5, 6–10, and 11–15, and show aggregates such as circulation counts and patron counts for each group.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt)

### R045  Include Null Report Values

**Priority:** Medium. Including blank values makes results more complete across several reporting contexts, although other system functions do not depend on this behavior.

Report results must include records with null or blank values rather than silently excluding them, including patrons with unpopulated optional demographic fields.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R046  Export Inactive Patron Results

**Priority:** Medium. CSV export makes inactive-patron results easier to analyze and share, but the report remains usable without this additional output option.

The system must allow users to export inactive patron report results to CSV.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml)

### R047  Generate Inactive Patron Reports

**Priority:** Medium. These reports help libraries review inactive accounts and outstanding fines at useful organizational levels, although they are a specialized management task.

The system must generate lists of patrons with no circulation or electronic activity during a configurable number of days. Electronic activity includes account or OPAC logins, online holds, online renewals, and logged access to integrated digital collections. Users must be able to select System, Home Library, County, or another required organizational level, include current mailing addresses, separately identify patrons with outstanding fines, and exclude specified categories such as do-not-disturb, VIP, staff, or opted-out patrons.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml), D10 (early_draft_srs_galecia.txt)

### R048  Process Reports in Background

**Priority:** Medium. Background processing helps staff retrieve results without waiting on a long-running inactive-patron report, though this report-specific convenience builds on broader processing capabilities.

The system must support background processing of inactive patron reports and retrieval of completed results.

**Sources:** D09 (conversations/conv_pines024_inactive_patrons.eml)

### R049  Add Authorized Canned Reports

**Priority:** Medium. Adding authorized canned reports lets staff tailor the report catalog to their work, while the existing reports and templates can still support reporting without this capability.

Authorized users must be able to add canned reports according to their permissions.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R050  Anonymized Demographic Statistics

**Priority:** Medium. Anonymized demographic statistics support planning while protecting patron identity, but they are one analytical use of the reporting system.

The system must produce demographic statistics, including transactions by geographic region and age range, using anonymized data that does not identify individual patrons.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R051  Associate Financial Records

**Priority:** Medium. Linking financial records with patron and item records supports useful account and collection analysis, although general reporting can proceed without every such association.

The system must associate fines, charges, waivers, and ecommerce transactions with Patron and Item records.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R052  Bibliographic Record Reports

**Priority:** Medium. D10 requests periodic checks for records with holds or without items, helping catalogers identify records that may need attention.

The system must provide periodic management reports identifying bibliographic records with holds and bibliographic records without item records.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R053  Cancel Report Execution

**Priority:** Medium. Cancellation helps users recover from unwanted or resource-intensive report runs, but it is a control around execution rather than a reporting prerequisite.

Users must be able to cancel a report that is scheduled or currently running.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R054  Cataloged and Non-Cataloged Circulation

**Priority:** Medium. Combined cataloged and non-cataloged circulation counts provide a more complete view of use, though reports can still cover cataloged circulation without them.

The system must provide reports of non-cataloged circulation and total circulation, including combined counts for cataloged and non-cataloged circulation.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R055  Circulation Attribute Breakdowns

**Priority:** Medium. D10, D14, and D20 request circulation breakdowns by operational and patron attributes, providing useful analysis beyond overall totals.

The system must provide circulation reports broken down by modifier, category, Dewey classification, shelving location, MARC fields, patron county, home library, and age.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt)

### R056  Circulation Transaction Counts

**Priority:** Medium. D10, D14, and D20 request detailed circulation counts that help libraries monitor service activity across staff and self-service channels.

The system must provide circulation reports with individual and cumulative counts for check-ins by book drop, terminal, staff user, and self-service method, distinguish check-ins from renewals in check-in date and time reporting, and count checkouts and renewals by staff checkout, self-checkout, staff renewal, self-checkout renewal, online renewal, and OPAC renewal.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R057  Clone Report Template Variants

**Priority:** Medium. D10, D12, D17, and D20 request cloning templates, allowing authorized users to adapt a report without replacing the original.

Authorized users must be able to clone an existing report template into a separate variant.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R058  Collection Age And Value Reports

**Priority:** Medium. D10 and D14 request collection age and value views that help staff assess materials by call number or shelving location.

The system must provide reports showing collection age or value by call number or shelving location.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R059  Collection Value Reports

**Priority:** Medium. Collection value reports can inform budgeting and collection review, though the system can provide its main operational reporting without valuations.

The system must report item values based on item-record data for the entire collection or a selected portion, including items selected by status, format, collection, call number, or shelving location.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml), D14 (evergreen_reference_2009.txt)

### R060  Configuration Migration

**Priority:** Medium. D10 assigns configuration migration Medium Priority, and it would simplify moving tested reports and permissions into production, though configurations can be managed manually. (D10 marks development and training environments with configuration migration Medium Priority)

The reporting system must provide export and import functionality to migrate configurations, including report templates, permission settings, saved queries, and other configuration, between development or training environments and the production environment.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R061  Create PINES-Wide Templates

**Priority:** Medium. D10, D12, D17, and D20 request PINES-wide templates so authorized users can share consistent reports across the consortium.

Authorized users must be able to create report templates for PINES libraries.

**Sources:** D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R062  Create Staff Report Templates

**Priority:** Medium. D10, D12, D17, and D20 request staff-accessible templates, which can make recurring reports consistent and easier to run.

Administrators must be able to create report templates that are available to staff.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R063  Cross-Tabulated Activity Reports

**Priority:** Medium. D10, D12, and D18 request cross-tabulated activity reports that help managers analyze service patterns across locations, times, and patron groups.

The system must provide predefined activity reports containing checkouts, check-ins, holds placed, and holds filled, with cross-tabulation by terminal, Branch, system, hour, Patron age range, Patron type, and Patron location.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R064  Current Bills Report

**Priority:** Medium. Current-bill reporting in D10 and D14 helps staff and finance teams review patron debts, complementing the fixed payment-audit capability.

The system must provide a report of bills currently owed by patrons.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R065  Data Quality Validation Reports

**Priority:** Medium. Requested across three source documents, these reports help staff identify and correct catalog data problems, though they are not needed for routine reporting to function.

The system must provide periodic management reports identifying data-quality problems, including Items with invalid item types, Items with excessively long call numbers, and bibliographic records without item records.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R066  Display Report Criteria

**Priority:** Medium. Showing criteria with results improves interpretability and reproducibility, though reports can still run without this presentation feature.

The system must display the query selections and clearly defined selection criteria with report results. Results must also identify the report name and selected date criteria.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt)

### R067  Edit Canned Report Fields

**Priority:** Medium. Editing displayed fields helps staff adapt canned reports to local needs, such as including shelving locations, but they can still use reports with their existing fields.

Authorized users must be able to edit the display fields of existing canned reports, such as adding shelving location.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R068  Error Reporting and Feedback

**Priority:** Medium. D10 marks administrator error feedback Medium Priority, so it can aid troubleshooting without being necessary for report execution. (D10 marks this Medium Priority)

The system must provide high-level error reporting and feedback and low-level query-specific feedback through the front-end interface for Local and Global System Administrators.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R069  Fines and Charges Reports

**Priority:** Medium. D10 and D11 request fines-and-charges reports by period and type, providing useful financial oversight beyond account-level balances.

The system must report fines and charges by time period and charge type.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R070  Group Transaction Reports

**Priority:** Medium. Grouping transactions by time and location helps managers analyze activity, but it is one of several useful report dimensions.

The system must group transactions by hour, terminal, branch, and system and support queries for all transactions or transaction types, including check-ins, checkouts, fines collected, and patron registrations.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R071  Historical Reporting

**Priority:** Medium. Historical snapshots support comparisons and audits across several sources, but the system can deliver current reporting without this capability.

The system must support reporting on data as it existed at a specified prior date or date range, including historical shelving locations and snapshots of bills. This reporting capability does not prescribe a particular storage architecture.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R072  Hold Fulfillment Reports

**Priority:** Medium. D10 and D14 request reports on unfilled, stale, and annual holds, helping staff monitor hold-service performance and follow-up needs.

The system must provide reports of unfilled holds, annual hold counts, and stale holds awaiting pickup.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R073  Hold Shipment Reports

**Priority:** Medium. D10 and D14 request reports of items sent or received for holds, which help staff monitor hold fulfillment between locations.

The system must provide reports of items sent or received for holds.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R074  Identify Material Use

**Priority:** Medium. D10 and D15 request identifying use of uncataloged materials, helping libraries assess how those materials are being used.

The system must identify the use of uncataloged materials.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R075  Item Activity Reports

**Priority:** Medium. D10, D14, and D15 request broad item-activity reporting that supports collection management, while other system functions can operate without every listed activity view.

The system must provide item reports for items added, deleted, edited, counted, currently checked out, overdue, long overdue, missing, in transit, claimed returned, or created within a date range. These item reports must show the last edit date based only on item edits, and circulation activity must not change or be included in that date.

**Sources:** D05 (conversations/conv_pines019_020_missing_intransit.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R076  Item Selection And Weeding Reports

**Priority:** Medium. D10 and D14 request use-count, fines-stopped, and weeding information that helps staff make collection-maintenance decisions.

The system must provide item reports that select items by use count or fines-stopped reason and provide weeding information.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R077  Item Usage Reports

**Priority:** Medium. Item-use and last-circulation data support collection and weeding decisions, but these analyses are not required for other reporting workflows.

The system must report total item-use counts and counts for selected date ranges, including fiscal-year and monthly use, and provide last-circulation dates and weeding data such as date of last circulation and circulation count.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R078  Missing MARC Fields

**Priority:** Medium. D10 and D14 request missing-MARC-field checks that help catalogers find incomplete bibliographic data.

The system must report bibliographic records missing specified MARC fields.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R079  Modify Permitted Report Selections

**Priority:** Medium. D10, D12, D17, and D20 request controlled template changes, giving staff flexibility while helping preserve dependable report results.

Staff must be able to run report templates as-is or modify only permitted selections, with changes preserving dependable results.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R080  On-Demand Report Interface

**Priority:** Medium. Editing criteria before execution gives users control over preset reports, though other reporting modes can cover the same general need.

The system must provide an on-demand reporting interface for preset maintenance, collection-development, and similar reports, allowing users to edit selection criteria and display options before execution.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R081  Open Template Reporting

**Priority:** Medium. Open-template reporting makes common data attributes available for flexible analysis, but it is one interface option among several.

The system must provide open-template reporting with circulation, item, patron, bill, and bibliographic attributes available for filtering and display.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R082  Overdue Item Reports

**Priority:** Medium. Overdue-item reports with contact information, requested in D10, D14, and D20, support follow-up on unreturned materials.

The system must provide reports of overdue items with relevant contact information.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R083  Patron Account Balance Reports

**Priority:** Medium. D10 and D11 request patron balance reports that help staff and managers review financial obligations at multiple organizational levels.

The system must report patron account balances by patron, home library, and system.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R084  Patron Count Reports

**Priority:** Medium. D10 and D14 request patron counts and additions, useful for monitoring service populations and enrollment trends.

The system must provide reports for patron counts and patron additions.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R085  Patron Demographic Reports

**Priority:** Medium. D10 and D14 request demographic reports across multiple categories, supporting service planning while remaining an analytical rather than operational workflow.

The system must provide reports of patrons by demographic category, age, county, city, ZIP code, home library, and profile group.

**Sources:** D08 (conversations/conv_pines023_patron_characteristics.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt)

### R086  Patron Status Reports

**Priority:** Medium. D10 and D14 request status and survey reports that help staff identify patron-account conditions and review survey responses.

The system must provide reports of patrons by survey response, expiration date, inactive or barred status, and note wording, as well as reports of voter survey responses.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R087  Payment Reports

**Priority:** Medium. D10 and D11 request payment breakdowns by period, method, and collecting library, supporting routine financial review.

The system must report payments by time period, payment method, and collecting library.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R088  Payments Received Report

**Priority:** Medium. Detailed payment reporting requested in D10 and D14 helps finance staff review receipts alongside the fixed payment ledger.

The system must provide a detailed report of payments received.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R089  Prioritize Report Queue

**Priority:** Medium. Queue prioritization can get time-sensitive board reports ahead of resource-intensive jobs, though the sources' emphasis does not make it a core requirement. (D12 describes report prioritization as crucial and states that important reports should be able to jump the queue)

The system must allow designated report types, such as board reports, to be prioritized ahead of lower-priority or resource-consuming reports in the execution queue.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R090  Process Description Documentation

**Priority:** Medium. D10 marks high-level process documentation Medium Priority, making it useful for understanding workflows but less urgent than operating capabilities. (D10 marks this Medium Priority)

Product documentation must provide high-level descriptions of major processes, including bibliographic record import and export, validation against internal and external authority sources, and standard reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R091  Query Financial Records

**Priority:** Medium. D10 and D11 request joined financial queries, including searches above a balance threshold, to help staff investigate accounts and charges.

The system must support financial queries that join fines, charges, waivers, and ecommerce transactions with Patron and Item records and allow users to query accounts above a specified balance.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R092  Real-Time Reporting

**Priority:** Medium. Current-data reports help monitor live activity, but not every management report requires real-time results.

The system must support reports using current data in real time, including reports used to monitor current activity.

**Sources:** D01 (conversations/conv_pines014_material_volume.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R093  Records Without Volumes

**Priority:** Medium. D10 and D14 request identifying records without volumes, helping catalogers find collection gaps and cleanup needs.

The system must report bibliographic records without attached volumes.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R094  Report Output Formats

**Priority:** Medium. Multiple output formats make results easier to analyze and share, but the reporting system can operate with a narrower set of formats.

The system must provide reports in Excel, HTML, CSV, and pivot-table formats.

**Sources:** D02 (conversations/conv_pines015_capacity_interface.eml), D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt), D20 (survey_results_2009.txt)

### R095  Report Queue Visibility

**Priority:** Medium. Queue status helps staff understand report progress across several sources, but it does not determine whether reports can execute.

Staff must be able to view their report's queue position, the number of reports ahead, submission time, and status, including waiting, running, completed, or failed.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D14 (evergreen_reference_2009.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D20 (survey_results_2009.txt)

### R096  Report Uncataloged Material Transactions

**Priority:** Medium. D10 and D15 request including uncataloged transactions in circulation statistics, helping avoid incomplete activity reporting.

The system must include transactions involving uncataloged materials in circulation statistics and reports.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D15 (interview_cataloging_2009-05-08.txt)

### R097  Run and Schedule Canned Reports

**Priority:** Medium. D10, D14, and D20 request reusable canned reports with scheduling, reducing repeated staff effort while leaving basic reporting possible without automation.

The system must provide canned reports that users can run immediately or schedule to run ASAP, hourly, daily, weekly, monthly, or yearly. Users must be able to edit recurring reports by adding or removing report selections and changing the report's email recipients.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R098  Separate System Environments

**Priority:** Medium. D10 marks development and training environments with configuration migration as Medium Priority, and D16, D18, and D19 also request separate environments for safer practice and testing. (D10 marks development and training environments with configuration migration Medium Priority)

The system must provide separate development, training, and production environments, with the training environment allowing staff to practice without risking production data.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D16 (interview_sysadmin_2009-05-10.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R099  Single-Row MARC Reporting

**Priority:** Medium. Single-row MARC extraction makes selected bibliographic fields easier to use in reports, but it is a specialized data presentation need.

The system must extract selected MARC fields for reports and display those fields on a single row of report data, including when the fields are stored across multiple rows.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R100  Staff Login Methods

**Priority:** Medium. Individual authentication and staff identification support accountable access, while the optional card method remains a convenience.

The system must support individual staff authentication using traditional username and password and an optional streamlined method such as an employee-card swipe. Card-based login must not be required or bypass individual authentication, and the system must identify which staff member is logged in.

**Sources:** D10 (early_draft_srs_galecia.txt), D13 (email_staff_login.eml), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

### R101  State-Aid Statistics Reports

**Priority:** Medium. D10, D12, and D18 request predefined statistics for boards and state-aid reporting, reducing the effort to assemble those external reports.

The system must provide predefined reports for library boards and other external consumers containing the basic statistics required by the Georgia Annual Report and Application for State Aid.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml)

### R102  Table and Field Access Control

**Priority:** Medium. Table- and field-level controls add useful protection for sensitive data, while the fixed role-based access requirements provide a broader security foundation.

The system must allow administrators to control staff access to tables and fields.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R103  Track Library Payments

**Priority:** Medium. D10 and D11 request tracking waivers and payments by library, providing useful local financial oversight.

The system must track fines waived and payments by library.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R104  Track Uncataloged Material Inventory

**Priority:** Medium. D10 and D15 request inventory tracking for uncataloged materials, allowing branches to account for materials before individual records are complete.

The system must track uncataloged materials, including paperback books and children's board books, as inventory before individual catalog records are complete.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R105  Transaction History Retention

**Priority:** Medium. Retaining detailed and aggregate transactions supports historical analysis, but the requested retention policy is not identified as a legal obligation here.

The system must retain detailed transaction history for a configurable number of days and retain monthly and annual aggregate information indefinitely.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R106  Transaction Summary Reports

**Priority:** Medium. These summaries help compare hold and checkout activity across organizational scopes, but they are one analytical report family.

The system must report holds placed, holds filled, and checkouts per patron, library, selected group of libraries, system, or county. Reports must display checkout and placed-hold counts per patron and subtotal holds by type, including active, frozen, and frozen-until holds.

**Sources:** D10 (early_draft_srs_galecia.txt), D12 (email_report_features.eml), D20 (survey_results_2009.txt)

### R107  Update Financial Information

**Priority:** Medium. Promptly reflected financial updates help keep reports and account review current, though the requirement is limited to the financial workflow.

The system must allow financial information to be updated and reflected promptly.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R108  Waived Fine Reports

**Priority:** Medium. D10 and D11 request waived-fine reporting by time and branch, helping managers review an important part of library financial activity.

The system must report fines waived by time period and Branch.

**Sources:** D10 (early_draft_srs_galecia.txt), D11 (email_financial_reports.eml)

### R109  Workstation Transaction Reports

**Priority:** Medium. Workstation- and staff-level transaction reports help analyze activity and workflow, though the system can provide general transaction reporting without them.

The system must report transactions by specified date and time, workstation, or staff member to support analysis of activity and staff workflow.

**Sources:** D10 (early_draft_srs_galecia.txt), D17 (meeting_minutes/meeting_2009-03-15_minutes.txt)

### R110  Vendor Data Integration

**Priority:** Medium. Vendor data exchange supports purchasing and processing workflows, but the request is limited to two sources and allows locations without particular vendor data.

The system must support data exchange with vendor websites through published APIs or automated transfers of standard-format data files, including USMARC21 and EDIFACT, while accommodating locations where particular vendor data is unavailable.

**Sources:** D10 (early_draft_srs_galecia.txt), D18 (meeting_minutes/meeting_2009-07-20_minutes.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R111  Prevent Duplicate Export Rows

**Priority:** Medium. Preventing unintended duplicate export rows improves the usability of exported data, though the single-source feature does not block other report functions.

Report exports must avoid unintended duplicate rows so exported data can be used without repeated records.

**Sources:** D20 (survey_results_2009.txt)

## Requirements: Low priority

### R112  Alert Transfer Problems

**Priority:** Low. Problem alerts can help staff respond sooner, but delayed-transfer notification is a single-source convenience rather than a prerequisite for tracking transfers.

The system must notify responsible staff when an item transfer is delayed or encounters an issue.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R113  Print Transit Labels

**Priority:** Low. Barcode transit labels can simplify physical handling, but staff can move items without this single-source printing feature.

The system must generate printable transit labels containing barcodes for items being transferred.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R114  Share Transfer Queries

**Priority:** Low. Sharing queries is a convenience for teams, but the single-source request does not make it necessary for users to run their own transfer queries.

The system must allow authorized users to share saved transfer queries with other authorized users.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R115  Undo Completed Transfers

**Priority:** Low. Undoing a completed transfer is a useful recovery option, but it is a single-source safeguard rather than a core reporting capability.

The system must allow an authorized user to undo an item transfer when an incorrect transfer has been completed.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

### R116  Review Purge Candidates

**Priority:** Low. Read-only candidate reports provide a convenient review step, but the request appears in only D06 and is not required to identify candidates.

The system must provide read-only reports of item records identified as purge candidates so users can review them without changing or deleting records through the reports.

**Sources:** D06 (conversations/conv_pines021_item_purging.eml)

### R117  Report Deletion Activity

**Priority:** Low. Deletion activity summaries help administrators review patterns, but the single-source request is an additional analysis rather than a core workflow.

The system must report deletion activity for a selected period, including totals and breakdowns by record type, location, system, and user, and identify users with the highest deletion counts.

**Sources:** D07 (conversations/conv_pines022_deletions.eml), D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

### R118  Track Denied Deletions

**Priority:** Low. Tracking denied attempts can help administrators investigate unusual behavior, but it is requested only in D07 and does not block ordinary deletion auditing.

The system must track deletion attempts that are denied so administrators can identify attempted deletions of records that users should not delete.

**Sources:** D07 (conversations/conv_pines022_deletions.eml)

### R119  Bibliographic Record Counts

**Priority:** Low. Bibliographic record counts by user and library are a useful management metric, but this specific report appears in only D10 and D14.

The system must report counts of bibliographic records, including records added by each user and library.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R120  Combine Reports Into Documents

**Priority:** Low. Combining canned reports into one document is a convenience requested in D10, D14, and D20, but separate report results remain usable.

The system must allow users to select multiple canned reports to run together and view their results in one document.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R121  Comparative Report Columns

**Priority:** Low. Comparative period columns can make trends easier to interpret, but this is a specialized output enhancement.

The system must support report outputs with comparative columns for periods such as last month's circulation, the previous month's circulation, percentage difference, the corresponding month of the previous year, and percentage difference between those periods.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R122  Edited Record Counts

**Priority:** Low. Edited-record counts provide a narrow staff-activity measure requested in D10 and D14, and the system can operate without it.

The system must report counts of edited bibliographic records.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R123  Email Report Delivery

**Priority:** Low. Email delivery and saved recipients add convenience, but users can retrieve and share reports through other means.

The system must allow users to deliver reports by email, enter recipients, and select recipients from an address book of regularly used addresses.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt), D20 (survey_results_2009.txt)

### R124  Filter Surveys By Name

**Priority:** Low. Selecting surveys by name is a usability improvement for a narrow report filter, and users can otherwise enter the identifier.

Users must be able to select a survey by its name rather than entering its identifier, and the system must resolve the name to the corresponding survey record.

**Sources:** D10 (early_draft_srs_galecia.txt), D19 (meeting_tech_subcommittee_2009-06-30.txt)

### R125  Forgive Work Goods Report

**Priority:** Low. This specialized breakdown of forgive, work, and goods payments is requested in D10 and D14 but is narrower than general payment reporting.

The system must provide a detailed report of forgive, work, and goods payments.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R126  Hold Purchase Alert Reports

**Priority:** Low. Hold purchase alert reports are a narrow operational report requested only in D10 and D14.

The system must provide reports identifying hold purchase alerts.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R127  In-House Use Reports

**Priority:** Low. In-house use counts add a limited view of material use, but the request appears only in D10 and other circulation reports remain available.

The system must report non-cataloged in-house use counts by month and cataloged in-house use counts.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R128  IntraPINES Loan Reports

**Priority:** Low. IntraPINES loan reports are a specialized reporting need requested in D10 and D14, and are not needed for general reporting workflows.

The system must provide reports of IntraPINES loans by system or facility.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R129  Notice Activity Reports

**Priority:** Low. Notice activity reports provide a useful service snapshot, but this limited report family is only specified in D10.

The system must support reports on pre-overdue notices, overdue notices, and holds notices sent.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R130  Patron Behavior Statistics

**Priority:** Low. Predictive behavior measures can inform planning, but the specialized statistics are requested by only two sources and are not core operations.

The system must produce statistics for understanding and predicting patron behavior and material use, including average return speed for a particular book, likelihood of renewal, renewal rates, and the percentage of branch checkouts that are renewals.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R131  Patron Library Validation Reports

**Priority:** Low. Invalid-home-library checks are a useful data-cleanup report, but this specific request appears only in D10.

The system must provide periodic management reports identifying patrons with invalid home libraries.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R132  Report Hold Placement Methods

**Priority:** Low. Hold-placement channels offer a useful service-use breakdown, but the single-source detail is not necessary for hold reporting generally.

The system must count hold requests and report how each hold was placed, including at a staff desk, at a public computer inside the library, or remotely.

**Sources:** D10 (early_draft_srs_galecia.txt), D20 (survey_results_2009.txt)

### R133  Staff Account Reports

**Priority:** Low. Staff-account reports on password changes and expiration are a useful administrative check, but the specific reporting need appears only in D10 and D14.

The system must provide reports of staff accounts by password-change date and account expiration.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R134  Upload Report Filters

**Priority:** Low. Uploading barcode or TCN filters can save time for selected tasks, but users can filter reports through other query methods.

Users must be able to upload a text file containing values such as barcodes or TCNs and use those values to filter a report.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

### R135  Voids Report

**Priority:** Low. A dedicated voids report is a useful financial review tool, but D10 and D14 request it as a specialized report rather than a core workflow.

The system must provide a detailed report of voids.

**Sources:** D10 (early_draft_srs_galecia.txt)

### R136  Aged Debt Report

**Priority:** Low. The aged-debt report is requested only in D14 and is a specialized extension of current-bill reporting.

The system must provide an aged-debt report with detailed debt information.

**Sources:** D10 (early_draft_srs_galecia.txt), D14 (evergreen_reference_2009.txt)

## Blacklist

### B01  Efficient Batch Processing

The system must process batch location updates efficiently for an inventory of approximately 9.6 million items and avoid database locking problems by processing updates in smaller batches.

**Sources:** D04 (conversations/conv_pines018_item_transfer.eml)

**Reason:** The candidate prescribes implementation and performance handling (smaller batches and avoidance of database locking) rather than a distinct user-facing capability or testable system quality. D04 mentions this only as a technical concern; the transfer capability is retained separately.

### B02  Report Output Validation

Report output must be tested and proven accurate for its intended reporting purpose.

**Sources:** D10 (early_draft_srs_galecia.txt)

**Reason:** This is a testing and QA process, not a capability or quality stated as a product behavior. D10's specification text calls for tested and proven output, but the candidate does not define a testable product requirement.

### B03  Centralized Multi-Location Service

Management Processes must be consolidated at a central location that accepts input from and provides services to multiple library locations, supporting a single source of truth for reporting.

**Sources:** D19 (meeting_tech_subcommittee_2009-06-30.txt)

**Reason:** D19 labels central consolidation as an assumption rather than a required system capability; the source does not make this an explicit product requirement.

### B04  Enterprise ILS Integration

The management processes must use the data structures and functionality of an enterprise-level Library Automation System, including its Acquisitions and Cataloging modules, rather than independently managing those functions.

**Sources:** D18 (meeting_minutes/meeting_2009-07-20_minutes.txt)

**Reason:** D18 presents this as an assumption and dependency on the enterprise library system, not as a capability required of the reporting product.

### B05  Library Automation Integration

Management Processes must rely on and read the data structures and functionality of the enterprise-level Library Automation System, including its Acquisitions and Cataloging modules, without managing acquisitions or cataloging data.

**Sources:** D19 (meeting_tech_subcommittee_2009-06-30.txt)

**Reason:** D19 presents this as an assumption and dependency on the enterprise library system, not as a capability required of the reporting product.

### B06  Distribute Materials Rapidly

**Priority:** Medium. D10 and D15 request rapid distribution with minimal branch labor, improving handling of uncataloged materials while not replacing core circulation workflows.

The system must support rapid distribution of uncataloged materials with minimal Branch labor.

**Sources:** D10 (early_draft_srs_galecia.txt), D15 (interview_cataloging_2009-05-08.txt)

**Reason:** Distribute Materials Rapidly is discarded because its sources, D10 and D15, support the general goals of rapid distribution and minimal Branch labor but do not specify a concrete system capability or testable measure for either outcome.

## Open issues

### Stakeholder questions

- What specific metrics or configured limits define branch capacity? (D02)
- How should shelf space be estimated when measurements are not directly tracked: from item dimensions, item count, or another method? (D03)
- Should checkout at a transfer destination trigger automatic reversion, or should checked-out items remain there while unused items revert? (D04)
- What threshold should be used for the delayed in-transit report beyond the suggested configurable default of seven days? (D05)
- Which electronic activities count toward inactivity when digital-resource access is not integrated or logged? (D09)
- How many years must transaction data be retained under applicable State law? (D12)

### Review issues

- **duplicate** (R001, R007): Both require a report identifying last-copy items. R007 includes last copies among its item-status reports, duplicating that capability in R001.
- **duplicate** (R052, R065): Both require a report identifying bibliographic records without item records. That report capability is listed in each requirement.
- **too narrow** (R025, R032): R025 is the printable pull-list output for the transfer utility in R032, rather than a standalone system capability.
- **too narrow** (R026, R032): R026 specifies the preview and confirmation step within the transfer utility described by R032.
- **too narrow** (R028, R032): R028 is a transfer-specific authorization rule for the utility in R032, rather than a separate capability.
- **too narrow** (R046, R047): R046 specifies CSV export for the inactive-patron results generated by R047; it is an output option of that report.
- **too narrow** (R048, R047): R048 specifies background processing and retrieval for the inactive-patron reports in R047; it is a report-specific execution detail.
- **possibly missed**: “Execute Purge Deletions” (D06): The system must allow authorized users to delete selected item records identified as purge candidates after the required confirmation step.
- **possibly missed**: “Report Quick Access Interface” (D14): The system must provide a quick-access interface for reports with pop-up descriptions of available reports or functions.
- **possibly missed**: “Report Title Tooltips” (D14): The system must provide hover tooltips for report titles.
- **possibly missed**: “Efficient Uncataloged Processing” (D15): The system must support rapid distribution of uncataloged materials while minimizing the amount of branch labor required per item.
- **possibly missed**: “Analyze Patron Interests” (D17): The system must provide management analysis of patron demographics and interests to support planning and evaluation of library services.
- **possibly missed**: “Verify Financial Transactions” (D17): The system must support tracking and verification of financial transactions for management oversight.
- **possibly missed**: “Cross-Branch Comparison Reports” (D18): The system must provide reports that compare library or branch results across multiple branches or library systems.
- **possibly missed**: “Predefined Executive Reports” (D18): The system must provide predefined reports for board and executive users through an Executive Reports interface.
- **possibly missed**: “Centralized Multi-Location Operations” (D19): The Management Processes system must be consolidated at a central location and accept input from and provide services to multiple library locations.

## Coverage

| Document | Path | Requirements | Blacklist |
| --- | --- | --- | --- |
| D01 | conversations/conv_pines014_material_volume.eml | R022, R071, R092 |  |
| D02 | conversations/conv_pines015_capacity_interface.eml | R005, R023, R071, R094 |  |
| D03 | conversations/conv_pines016_shelf_space.eml | R024 |  |
| D04 | conversations/conv_pines018_item_transfer.eml | R008, R016, R025, R026, R027, R028, R029, R030, R031, R032, R112, R113, R114, R115 | B01 |
| D05 | conversations/conv_pines019_020_missing_intransit.eml | R007, R019, R033, R034, R075 |  |
| D06 | conversations/conv_pines021_item_purging.eml | R001, R007, R035, R036, R037, R038, R039, R041, R042, R116 |  |
| D07 | conversations/conv_pines022_deletions.eml | R035, R117, R118 |  |
| D08 | conversations/conv_pines023_patron_characteristics.eml | R008, R043, R044, R045, R055, R070, R085 |  |
| D09 | conversations/conv_pines024_inactive_patrons.eml | R009, R046, R047, R048 |  |
| D10 | early_draft_srs_galecia.txt | R001, R002, R003, R004, R005, R006, R007, R008, R009, R010, R011, R012, R013, R014, R015, R016, R017, R018, R019, R022, R023, R024, R025, R027, R029, R030, R032, R033, R034, R035, R036, R038, R039, R040, R041, R042, R043, R044, R045, R047, R049, R050, R051, R052, R053, R054, R055, R056, R057, R058, R059, R060, R062, R063, R064, R065, R066, R067, R068, R069, R070, R071, R072, R073, R074, R075, R076, R077, R078, R079, R080, R081, R082, R083, R084, R085, R086, R087, R088, R089, R090, R091, R092, R093, R094, R095, R096, R097, R098, R099, R100, R101, R102, R103, R104, R105, R106, R107, R108, R109, R110, R117, R119, R120, R121, R122, R123, R124, R125, R126, R127, R128, R129, R130, R131, R132, R133, R134, R135, R136 | B02, B06 |
| D11 | email_financial_reports.eml | R006, R011, R020, R051, R059, R069, R083, R087, R091, R103, R107, R108 |  |
| D12 | email_report_features.eml | R002, R008, R013, R016, R020, R050, R055, R056, R057, R062, R063, R066, R070, R079, R089, R095, R101, R106 |  |
| D13 | email_staff_login.eml | R016, R100 |  |
| D14 | evergreen_reference_2009.txt | R001, R002, R003, R005, R007, R008, R009, R010, R030, R045, R053, R054, R055, R056, R058, R059, R060, R064, R065, R066, R067, R071, R072, R075, R076, R077, R078, R080, R081, R082, R084, R085, R086, R088, R089, R092, R093, R094, R095, R096, R097, R098, R119, R120, R122, R123, R126, R133, R134, R136 |  |
| D15 | interview_cataloging_2009-05-08.txt | R001, R007, R019, R022, R024, R027, R029, R030, R032, R033, R034, R035, R036, R038, R039, R041, R042, R052, R054, R065, R074, R075, R096, R104, R117 | B06 |
| D16 | interview_sysadmin_2009-05-10.txt | R002, R003, R004, R009, R010, R012, R015, R016, R017, R018, R060, R098 |  |
| D17 | meeting_minutes/meeting_2009-03-15_minutes.txt | R023, R061, R077, R085, R109 |  |
| D18 | meeting_minutes/meeting_2009-07-20_minutes.txt | R003, R004, R005, R009, R010, R012, R014, R015, R016, R017, R018, R019, R021, R023, R024, R034, R050, R060, R061, R065, R068, R076, R077, R089, R090, R095, R098, R100, R110 | B04 |
| D19 | meeting_tech_subcommittee_2009-06-30.txt | R003, R009, R010, R012, R014, R015, R016, R018, R021, R045, R053, R060, R068, R071, R092, R094, R098, R110, R124 | B03, B05 |
| D20 | survey_results_2009.txt | R002, R008, R009, R011, R027, R029, R030, R032, R035, R045, R050, R053, R056, R062, R070, R071, R077, R079, R092, R094, R095, R097, R099, R105, R106, R111, R123, R130, R132 |  |
