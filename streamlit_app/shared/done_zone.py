"""Shared Zone C (done stage) renderer for all workflow pages.

UX-F-04 / UX-010:
- Inline report preview (first 3000 chars, expandable)
- Case ID displayed as st.code() for easy selection
- Location path hidden in "Technical details" expander
- Primary "Start Another [Workflow]" button in main content area
- Download button for final_report.en.md
"""

from __future__ import annotations

from pathlib import Path


def render_done_zone(
    st,
    case_id: str,
    client_name: str,
    report_path: Path,
    workflow_label: str,
    session_state_keys: list[str],
    stage_key: str,
    enable_workpaper: bool = False,
) -> None:
    """Render Zone C (done stage) with report preview, download, and reset.

    Args:
        st:                  Streamlit module passed from the page.
        case_id:             The case ID for this run.
        client_name:         Client name (used in download filename).
        report_path:         Path to final_report.en.md.
        workflow_label:      Human-readable workflow name, e.g. "Investigation".
        session_state_keys:  All session_state keys to clear on "Start Another".
        stage_key:           Session state key controlling the stage machine (e.g. "inv_stage").
        enable_workpaper:    When True, renders a secondary "Generate Interim Workpaper" button (WORK-03).
    """
    st.success(f"{workflow_label} complete — Case ID: `{case_id}`")

    # Download buttons — docx left (primary), md right (secondary) per ux-specs.md:386
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8")
        safe_client = client_name.replace(" ", "_")
        docx_path = report_path.with_suffix(".docx")
        col_docx, col_md = st.columns(2)
        if docx_path.exists():
            with col_docx:
                st.download_button(
                    label="Download Word document",
                    data=docx_path.read_bytes(),
                    file_name=f"{workflow_label.replace(' ', '_')}_{safe_client}_{case_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        with col_md:
            st.download_button(
                label="Download Markdown backup",
                data=report_text,
                file_name=f"{workflow_label.replace(' ', '_')}_{safe_client}_{case_id}.md",
                mime="text/markdown",
            )

        # Inline preview (UX-010)
        with st.expander("Preview report", expanded=False):
            preview = report_text[:3000]
            st.markdown(preview)
            if len(report_text) > 3000:
                if st.button("Show full report in preview", key=f"full_preview_{case_id}"):
                    st.markdown(report_text[3000:])
    else:
        st.warning("No output was generated. Check the pipeline log and try again.")

    # Case ID as st.code() for easy selection (UX-010)
    st.markdown("**Case ID:**")
    st.code(case_id, language=None)

    # Technical details — collapsed by default (UX-010)
    with st.expander("Technical details", expanded=False):
        st.caption(f"Case folder: cases/{case_id}/")
        st.caption(f"Audit log: cases/{case_id}/audit_log.jsonl")

    # Workpaper button — secondary, below primary download (WORK-03)
    if enable_workpaper:
        st.divider()
        wp_key = f"wp_done_{case_id}"
        if st.button("Generate Interim Workpaper", key=wp_key):
            with st.spinner("Generating workpaper..."):
                try:
                    from workflows.workpaper import WorkpaperGenerator
                    gen = WorkpaperGenerator()
                    wp_path = gen.generate(case_id, {"document_count": 0})
                    st.success(f"Workpaper created: {wp_path.name}")
                    st.download_button(
                        label=f"Download {wp_path.name}",
                        data=wp_path.read_bytes(),
                        file_name=wp_path.name,
                        mime="text/markdown",
                        key=f"wp_dl_done_{case_id}",
                    )
                except Exception as e:
                    st.error(f"Workpaper generation failed: {e}")

    # Primary "Start Another" CTA in main content area (UX-010)
    if st.button(f"Start Another {workflow_label}", type="primary", key=f"restart_{case_id}"):
        for k in session_state_keys:
            st.session_state.pop(k, None)
        st.session_state[stage_key] = "intake"
        st.rerun()
