---
type: Example
title: Sample update report
description: Show the report sections with fictional project data.
status: stable
---

# DevWarden update report

This example uses fictional repositories. It does not describe a real service run.

**1 updated · 1 current · 1 excluded · 1 error**

## Errors — action required

| Repository | Branch | Reason | Diagnostics | Suggested action |
|---|---|---|---|---|
| sample-api | main → main | Local history differs from remote | Ahead: 2. Behind: 4. | Examine the local and remote commits before you change either history. |

## Excluded from updates

| Repository | Reason |
|---|---|
| empty-example | The remote has no branches or code to update. |

## Updated repositories

| Repository | Branch | Commits added | Changes |
|---|---|---|---|
| sample-library | main | 3 | The real report includes a GitHub comparison link. |

## Already up to date

| Repository | Branch |
|---|---|
| sample-ui | main, updated separately while the checkout stays on feature/example |

## Email layout

Download [the HTML example](report.html) and open it in a browser to examine the email layout.
GitHub displays that file as source. It does not run HTML files.
