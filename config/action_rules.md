# Action Rules

The first implementation is read-only. These values describe suggestions, not platform writes.

## Data Quality Status

| Status | Meaning | Allowed Recommendation Level |
| --- | --- | --- |
| ready | Data is complete enough for budget/material suggestions. | P0/P1/P2 |
| partial | Key metrics exist but platform, attribution, or context is incomplete. | P1/P2 only, medium or low confidence |
| blocked | Data is not trustworthy for budget/material decisions. | data repair only |
| inactive_no_data | The platform or project has no usable rows in the window. | no_action_no_data only |

## Read-only Action Taxonomy

| Action | Meaning | Default Observe Window |
| --- | --- | --- |
| add_budget | Recommend a mature scale-up candidate. | next complete day |
| small_add | Recommend a small scale-up validation. | next complete day |
| maintain | Keep current budget and observe. | 24h |
| test_budget | Keep or open a small test budget after human review. | 2-3 complete days |
| reduce_or_reallocate | Recommend reducing or moving budget after human review. | next complete day |
| pause_candidate | Candidate for human-reviewed pause. | next complete day |
| refresh_creative | Recommend new variants or creative refresh. | 2-3 complete days |
| data_gap_check | Fix attribution, mapping, account, or source-data issues before judging. | immediate |
| no_action_no_data | No platform action because no usable data exists. | next report |

## Forbidden Write Actions

The CLI and reports must reject direct platform write actions such as `set_budget`, `pause_ad`, `create_ad`, `publish_ad`, `delete_ad`, or `update_bid`.

