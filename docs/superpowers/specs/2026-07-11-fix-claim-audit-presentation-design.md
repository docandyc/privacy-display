# English Manuscript Claim-Audit and Presentation Repair Design

## Objective

Revise the current IEEE Access manuscript so that its research question, contribution statements, results narrative, figures, tables, discussion, and conclusion all support one coherent argument: the paper reports a bounded profile-level conventional-OCR measurement under one UVC link and maps the conditions under which that observation fails.

## Chosen Approach

Use a failure-boundary-centered revision without converting the article into a formal `Negative Result` submission. Existing measurements remain unchanged. Pending author and user-study placeholders remain pending.

## Argument Architecture

1. **Supported observation**: the three evaluated profiles have different conventional-OCR recovery rates in the matched fixed-setting archive.
2. **Causal boundary**: the experiment does not identify temporal sparsity as the cause because luminance, overlays, timing, camera behavior, and collection order are not isolated.
3. **Usability boundary**: the readability-priority profile is linked only to the planned short-duration transcription and immediate-rating study; no general or long-term usability claim is made.
4. **Security boundary**: high-suppression is an exploratory stress profile, not an effective general privacy defense.
5. **Primary contribution**: preprocessing, VLM, temporal integration, and inversion-slot attacks define the failure boundary of the observed conventional-OCR reduction.

## Source Changes

- Rewrite the abstract, core research question, contribution list, key findings, discussion, limitations, and conclusion to remove defense/measurement ambiguity.
- Replace `controlled` language where the archive does not support experimental control.
- Reduce repeated appearances of the 94.5/17.8/5.6 result and repeated disclaimers while retaining one clear statement in each section that needs it.
- Standardize terminology for conventional OCR, character recovery, the matched common-setting pool, and the 150-frame temporal mean.
- Clarify interval and unit semantics in Table 4, Figure 4, Table 9, and the synthetic OCR reduction table.
- Modify Figure 2 visual labels so the diagram does not claim that human output is proven readable or that the camera fragment is universally unreadable.
- Retitle and narrow the supplementary document to match the reported detection diagnostics and tracking audit.

## Layout Strategy

- Prefer shortening captions and repeated prose before moving core evidence.
- Keep the primary matched OCR table, explicit-field table, preprocessing table, and VLM boundary evidence in the main manuscript.
- Preserve the current two-column IEEE Access template.
- Target 19 pages and enforce a hard ceiling of 20 pages in this pass.

## Verification

- Compile both LaTeX documents from clean dependency order.
- Check logs for undefined references/citations and newly introduced overfull boxes.
- Render all pages and inspect a contact sheet plus pages containing modified figures/tables.
- Search for unsupported phrases, old Figure 2 labels, inconsistent metric names, and accidental changes to placeholders.

## Out of Scope

- New data collection, model calls, OCR reruns, statistical recomputation, literature additions, artifact-repository cleanup, and completion of author/user-study placeholders.
