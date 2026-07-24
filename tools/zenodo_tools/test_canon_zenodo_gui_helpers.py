#!/usr/bin/env python3
"""Unit tests for canon Zenodo discovery / Update Config helpers (no network)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import publish_canon_zenodo as pc


class FakeAutomation:
    base_url = "https://zenodo.org"

    def __init__(self, deposits=None, versions_by_anchor=None):
        self.deposits = deposits or []
        self.versions_by_anchor = versions_by_anchor or {}
        self.uploaded_files = []
        self.metadata_puts = []
        self.edit_calls = []
        self.publish_calls = []

    def get_deposit_info(self, deposit_id: str, quiet: bool = False):
        for d in self.deposits:
            if str(d.get("id")) == str(deposit_id):
                return d
        return None

    def list_record_versions(self, anchor: str):
        return list(self.versions_by_anchor.get(anchor, self.versions_by_anchor.get("*", [])))

    def list_deposits(self, published_only=False, limit=100):
        if published_only:
            return [d for d in self.deposits if d.get("submitted")]
        return list(self.deposits)

    def fetch_record_by_doi(self, doi: str):
        return {"id": "21249056", "doi": doi}

    def create_new_version(self, record_id: str):
        return {
            "deposit_id": "999001",
            "doi": "10.5281/zenodo.999001",
            "html_url": "https://zenodo.org/deposit/999001",
        }

    def edit_deposit(self, deposit_id: str) -> bool:
        self.edit_calls.append(deposit_id)
        return True

    def publish_deposit(self, deposit_id: str) -> bool:
        self.publish_calls.append(deposit_id)
        return True


class ResolveAnchorTests(unittest.TestCase):
    def test_anchor_ignores_non_canon_local_head(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.23",
                source="local",
                doi="10.5281/zenodo.21249060",
                deposit_id="21249060",
                has_config=True,
                title="Distributed Governance",
            ),
            pc.CanonVersionInfo(
                version="0.8.19",
                source="local",
                doi="10.5281/zenodo.21249056",
                deposit_id="21249056",
                has_config=True,
                title="Swirl-String-Theory Canon v0.8.19",
            ),
        ]
        auto = FakeAutomation(
            deposits=[
                {
                    "id": 21249060,
                    "conceptrecid": "99999999",
                    "submitted": False,
                    "state": "unsubmitted",
                    "metadata": {"title": "Distributed Governance", "conceptrecid": "99999999"},
                },
                {
                    "id": 21249056,
                    "conceptrecid": pc.CANON_CONCEPT_RECID,
                    "submitted": True,
                    "state": "done",
                    "metadata": {
                        "title": "Swirl-String-Theory Canon v0.8.19",
                        "conceptrecid": pc.CANON_CONCEPT_RECID,
                    },
                    "doi": "10.5281/zenodo.21249056",
                },
            ]
        )
        anchor = pc.resolve_canon_concept_anchor(local, auto)
        self.assertEqual(anchor, "10.5281/zenodo.21249056")

    def test_anchor_skips_canon_draft_prefers_published(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.20",
                source="local",
                doi="10.5281/zenodo.21530432",
                deposit_id="21530432",
                has_config=True,
            ),
            pc.CanonVersionInfo(
                version="0.8.19",
                source="local",
                doi="10.5281/zenodo.21249056",
                deposit_id="21249056",
                has_config=True,
            ),
        ]
        auto = FakeAutomation(
            deposits=[
                {
                    "id": 21530432,
                    "conceptrecid": pc.CANON_CONCEPT_RECID,
                    "submitted": False,
                    "state": "unsubmitted",
                    "metadata": {
                        "title": "Swirl-String-Theory Canon v0.8.20",
                        "conceptrecid": pc.CANON_CONCEPT_RECID,
                        "prereserve_doi": {"doi": "10.5281/zenodo.21530432"},
                    },
                },
                {
                    "id": 21249056,
                    "conceptrecid": pc.CANON_CONCEPT_RECID,
                    "submitted": True,
                    "state": "done",
                    "doi": "10.5281/zenodo.21249056",
                    "metadata": {
                        "title": "Swirl-String-Theory Canon v0.8.19",
                        "conceptrecid": pc.CANON_CONCEPT_RECID,
                    },
                },
            ]
        )
        self.assertEqual(
            pc.resolve_canon_concept_anchor(local, auto),
            "10.5281/zenodo.21249056",
        )

    def test_anchor_falls_back_to_concept_doi(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.23",
                source="local",
                doi="10.5281/zenodo.21249060",
                deposit_id="21249060",
                has_config=True,
            ),
        ]
        auto = FakeAutomation(
            deposits=[
                {
                    "id": 21249060,
                    "conceptrecid": "1",
                    "metadata": {"title": "Other Paper", "conceptrecid": "1"},
                }
            ]
        )
        self.assertEqual(pc.resolve_canon_concept_anchor(local, auto), pc.CONCEPT_DOI)


class DraftListingTests(unittest.TestCase):
    def test_orphan_draft_kept_in_list(self):
        auto = FakeAutomation(
            versions_by_anchor={
                pc.CONCEPT_DOI: [
                    {
                        "id": 1,
                        "title": "Swirl-String-Theory Canon v0.8.19 — Canonical Reference",
                        "version": "v0.8.19",
                        "doi": "10.5281/zenodo.1",
                        "is_published": True,
                        "links": {},
                    }
                ]
            },
            deposits=[
                {
                    "id": 999,
                    "submitted": False,
                    "metadata": {
                        "title": "Swirl-String-Theory Canon — untitled draft",
                        "prereserve_doi": {"doi": "10.5281/zenodo.999"},
                    },
                    "links": {"html": "https://zenodo.org/deposit/999"},
                },
                {
                    "id": 888,
                    "submitted": False,
                    "metadata": {
                        "title": "Rotating-Frame Unification in Swirl-String Theory:",
                        "prereserve_doi": {"doi": "10.5281/zenodo.888"},
                    },
                    "links": {},
                },
            ],
        )
        with patch.object(pc, "resolve_canon_concept_anchor", return_value=pc.CONCEPT_DOI):
            online = pc.fetch_online_canon_versions(auto, local=[])
        drafts = pc.list_online_drafts(online)
        self.assertTrue(any(d.deposit_id == "999" for d in drafts))
        self.assertFalse(any(d.deposit_id == "888" for d in drafts))
        orphan = next(d for d in drafts if d.deposit_id == "999")
        self.assertTrue(pc.is_orphan_online_version(orphan.version))

    def test_canon_title_heuristic(self):
        self.assertTrue(pc.is_canon_deposit_title("Swirl-String-Theory Canon v0.8.20"))
        self.assertFalse(pc.is_canon_deposit_title("Rotating-Frame Unification in Swirl-String Theory:"))
        self.assertFalse(pc.is_canon_deposit_title("Physics Anomalies: Canonical Synthesis via Swirl-String"))


class BindAndUpdateTests(unittest.TestCase):
    def test_bind_draft_writes_config_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edition = root / "v0.8.21"
            edition.mkdir()
            tex = edition / "SST_CANON-v0.8.21.tex"
            tex.write_text(
                r"\newcommand{\paperdoi}{10.5281/zenodo.OLD}" + "\n"
                r"\title{Test}" + "\n",
                encoding="utf-8",
            )
            auto = FakeAutomation(
                deposits=[
                    {
                        "id": 555,
                        "submitted": False,
                        "metadata": {
                            "title": "Swirl-String-Theory Canon draft",
                            "prereserve_doi": {"doi": "10.5281/zenodo.555"},
                        },
                        "links": {"html": "https://zenodo.org/deposit/555"},
                    }
                ],
                versions_by_anchor={
                    pc.CONCEPT_DOI: [
                        {
                            "id": 555,
                            "title": "Swirl-String-Theory Canon draft",
                            "version": "",
                            "doi": "10.5281/zenodo.555",
                            "is_published": False,
                            "links": {"html": "https://zenodo.org/deposit/555"},
                            "metadata": {
                                "title": "Swirl-String-Theory Canon draft",
                                "prereserve_doi": {"doi": "10.5281/zenodo.555"},
                            },
                        }
                    ]
                },
            )

            def fake_update(automation, deposit_id, config_data):
                automation.metadata_puts.append((deposit_id, config_data))
                return True

            with patch.object(pc, "been_processed_root", return_value=root), \
                 patch.object(pc, "get_canon_keywords", return_value=["sst"]), \
                 patch.object(pc, "get_edition_changelog", return_value={"0.8.21": "test"}), \
                 patch.object(pc, "tex_file_relative_path", return_value="SST-CANON/been_processed/v0.8.21/SST_CANON-v0.8.21.tex"), \
                 patch("publish_canon_zenodo.update_zenodo_metadata", side_effect=fake_update), \
                 patch.object(pc, "extract_metadata_from_latex", return_value={"title": "T", "description": ""}):
                result = pc.bind_draft_to_local_version(
                    "555",
                    "0.8.21",
                    automation=auto,
                    dry_run=False,
                )

            self.assertTrue(result.success, result.message)
            cfg = json.loads((edition / "SST_CANON-v0.8.21.zenodo.json").read_text(encoding="utf-8"))
            self.assertEqual(cfg["deposit_id"], "555")
            self.assertEqual(cfg["doi"], "10.5281/zenodo.555")
            self.assertTrue(auto.metadata_puts)
            self.assertFalse(auto.uploaded_files)

    def test_update_config_no_pdf_dry_run_no_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edition = root / "v0.8.20"
            edition.mkdir()
            tex = edition / "SST_CANON-v0.8.20.tex"
            tex.write_text(r"\newcommand{\paperdoi}{10.5281/zenodo.21527848}" + "\n", encoding="utf-8")
            cfg_path = edition / "SST_CANON-v0.8.20.zenodo.json"
            cfg_path.write_text(
                json.dumps({
                    "title": "t",
                    "doi": "10.5281/zenodo.21527848",
                    "deposit_id": "21527848",
                    "description": "old",
                }),
                encoding="utf-8",
            )
            auto = FakeAutomation()
            local = [
                pc.CanonVersionInfo(
                    version="0.8.20",
                    source="local",
                    doi="10.5281/zenodo.21527848",
                    deposit_id="21527848",
                    has_config=True,
                    has_tex=True,
                )
            ]
            online = [
                pc.CanonVersionInfo(
                    version="0.8.20",
                    source="online",
                    doi="10.5281/zenodo.21527848",
                    deposit_id="21527848",
                    state="draft",
                    html_url="https://zenodo.org/deposit/21527848",
                )
            ]
            with patch.object(pc, "been_processed_root", return_value=root), \
                 patch.object(pc, "scan_local_canon_versions", return_value=local), \
                 patch.object(pc, "fetch_online_canon_versions", return_value=online), \
                 patch.object(pc, "is_known_canon_version", return_value=True):
                result = pc.update_config_no_pdf(
                    "0.8.20",
                    automation=auto,
                    dry_run=True,
                )
            self.assertTrue(result.success, result.message)
            self.assertIn("no PDF", result.message)
            self.assertFalse(auto.uploaded_files)
            self.assertFalse(auto.metadata_puts)


class DedupeHelpersTests(unittest.TestCase):
    def test_list_bindable_skips_published(self):
        local = [
            pc.CanonVersionInfo(version="0.8.19", source="local", has_tex=True),
            pc.CanonVersionInfo(version="0.8.21", source="local", has_tex=True),
        ]
        online = [
            pc.CanonVersionInfo(
                version="0.8.19", source="online", state="published", deposit_id="1"
            ),
            pc.CanonVersionInfo(
                version="0.8.20", source="online", state="draft", deposit_id="2"
            ),
        ]
        bindable = pc.list_bindable_local_versions(local, online, draft_deposit_id="2")
        self.assertEqual([v.version for v in bindable], ["0.8.21"])


class StaleDepositTests(unittest.TestCase):
    def test_stale_deposit_blocks_push_allows_mint(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.20",
                source="local",
                doi="10.5281/zenodo.21527848",
                deposit_id="21527848",
                has_tex=True,
                has_config=True,
                has_pdf=True,
                pdf_doi_ok=True,
            )
        ]
        online = [
            pc.CanonVersionInfo(
                version="0.8.19",
                source="online",
                doi="10.5281/zenodo.21249056",
                deposit_id="21249056",
                state="published",
            )
        ]
        with patch.object(
            pc,
            "read_config_data",
            return_value={
                "doi": "10.5281/zenodo.21527848",
                "deposit_id": "21527848",
            },
        ), patch.object(pc, "main_tex", return_value=Path("dummy.tex")), \
           patch("publish_canon_zenodo.expected_canon_pdf_path") as exp, \
           patch("publish_canon_zenodo.resolve_pdf_path") as res:
            exp.return_value = MagicMock(is_file=lambda: True)
            res.return_value = MagicMock(is_file=lambda: True)
            can_push, can_mint, errors = pc.validate_version_for_push("0.8.20", local, online)
        self.assertFalse(can_push)
        self.assertTrue(can_mint)
        self.assertTrue(any("bestaat niet" in e for e in errors))

        statuses = pc.compare_versions(local, online)
        st = next(s for s in statuses if s.version == "0.8.20")
        self.assertEqual(st.status, "stale_deposit")
        self.assertTrue(st.can_mint_doi)
        self.assertFalse(st.can_push)

    def test_mint_skips_early_return_when_stale(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.20",
                source="local",
                doi="10.5281/zenodo.21527848",
                deposit_id="21527848",
                has_tex=True,
                has_config=True,
            )
        ]
        online: list[pc.CanonVersionInfo] = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edition = root / "v0.8.20"
            edition.mkdir()
            tex = edition / "SST_CANON-v0.8.20.tex"
            tex.write_text(
                r"\newcommand{\paperdoi}{10.5281/zenodo.21527848}" + "\n",
                encoding="utf-8",
            )
            (edition / "SST_CANON-v0.8.20.zenodo.json").write_text(
                json.dumps({"doi": "10.5281/zenodo.21527848", "deposit_id": "21527848"}),
                encoding="utf-8",
            )
            auto = FakeAutomation()
            with patch.object(pc, "been_processed_root", return_value=root), \
                 patch.object(pc, "scan_local_canon_versions", return_value=local), \
                 patch.object(pc, "fetch_online_canon_versions", return_value=online), \
                 patch.object(pc, "is_known_canon_version", return_value=True), \
                 patch.object(pc, "get_edition_changelog", return_value={"0.8.20": "x"}), \
                 patch.object(pc, "tex_file_relative_path", return_value="x.tex"):
                result = pc.mint_version_doi("0.8.20", automation=auto, dry_run=True, force=True)
            self.assertTrue(result.success)
            self.assertIn("Dry run OK", result.message)
            self.assertTrue(any("create new version" in a.lower() or "Would create" in a for a in result.actions))


class ApiErrorClassifyTests(unittest.TestCase):
    def test_404_suggests_remint(self):
        action, hint = pc.classify_zenodo_api_error(404, "Not Found", "get_deposit_info")
        self.assertEqual(action, "remint")
        self.assertIn("Remint", hint)

    def test_403_suggests_token(self):
        action, _ = pc.classify_zenodo_api_error(403, "Forbidden", "create_new_version")
        self.assertEqual(action, "check_token")

    def test_apply_attaches_fields(self):
        auto = FakeAutomation()
        auto.last_api_error = {
            "operation": "create_new_version",
            "status": 404,
            "detail": "Record not found",
            "url": "https://zenodo.org/api/x",
        }
        result = pc.PushResult(version="0.8.20", success=False)
        pc.apply_automation_api_error(result, auto, "Failed to create new Zenodo version")
        self.assertEqual(result.api_status, 404)
        self.assertEqual(result.suggested_action, "remint")
        self.assertIn("404", result.message)


class RemintRefreshTests(unittest.TestCase):
    def test_older_published_not_stale_when_new_draft_exists(self):
        local = [
            pc.CanonVersionInfo(
                version="0.8.19",
                source="local",
                doi="10.5281/zenodo.21249056",
                deposit_id="21249056",
                has_tex=True,
                has_config=True,
                has_pdf=True,
                pdf_doi_ok=True,
            ),
            pc.CanonVersionInfo(
                version="0.8.20",
                source="local",
                doi="10.5281/zenodo.21530432",
                deposit_id="21530432",
                has_tex=True,
                has_config=True,
            ),
        ]
        online = [
            pc.CanonVersionInfo(
                version="0.8.19",
                source="online",
                doi="10.5281/zenodo.21249056",
                deposit_id="21249056",
                state="published",
            ),
            pc.CanonVersionInfo(
                version="0.8.20",
                source="online",
                doi="10.5281/zenodo.21530432",
                deposit_id="21530432",
                state="draft",
            ),
        ]
        self.assertFalse(pc.local_deposit_is_stale("0.8.19", local, online))
        self.assertFalse(pc.local_deposit_is_stale("0.8.20", local, online))

        # Incomplete online list (only draft) must not mark 0.8.19 stale if DOI matches
        # when we somehow only have DOI via a published sibling restored later —
        # here: deposit missing from list but same version+doi published entry absent
        # → still stale. With published entry present → not stale (above).

        # False-positive scenario from remint: only draft online, 0.8.19 local deposit
        # not in list → WITHOUT doi match online for 0.8.19 would be stale.
        online_draft_only = [
            pc.CanonVersionInfo(
                version="0.8.20",
                source="online",
                doi="10.5281/zenodo.21530432",
                deposit_id="21530432",
                state="draft",
            ),
        ]
        self.assertTrue(pc.local_deposit_is_stale("0.8.19", local, online_draft_only))

        # Anchor must skip draft and pick published when probing deposits
        auto = FakeAutomation(
            deposits=[
                {
                    "id": 21530432,
                    "conceptrecid": pc.CANON_CONCEPT_RECID,
                    "submitted": False,
                    "state": "unsubmitted",
                    "metadata": {
                        "title": "Swirl-String-Theory Canon v0.8.20",
                        "conceptrecid": pc.CANON_CONCEPT_RECID,
                    },
                },
                {
                    "id": 21249056,
                    "conceptrecid": pc.CANON_CONCEPT_RECID,
                    "submitted": True,
                    "state": "done",
                    "doi": "10.5281/zenodo.21249056",
                    "metadata": {
                        "title": "Swirl-String-Theory Canon v0.8.19",
                        "conceptrecid": pc.CANON_CONCEPT_RECID,
                    },
                },
            ],
            versions_by_anchor={
                "10.5281/zenodo.21249056": [
                    {
                        "id": 21249056,
                        "title": "Swirl-String-Theory Canon v0.8.19 — Canonical Reference",
                        "version": "v0.8.19",
                        "doi": "10.5281/zenodo.21249056",
                        "is_published": True,
                        "links": {},
                    },
                    {
                        "id": 21530432,
                        "title": "Swirl-String-Theory Canon v0.8.20 — Canonical Reference",
                        "version": "v0.8.20",
                        "doi": "10.5281/zenodo.21530432",
                        "is_published": False,
                        "links": {},
                        "metadata": {
                            "title": "Swirl-String-Theory Canon v0.8.20 — Canonical Reference",
                            "prereserve_doi": {"doi": "10.5281/zenodo.21530432"},
                        },
                    },
                ]
            },
        )
        with patch.object(pc, "resolve_canon_concept_anchor", wraps=pc.resolve_canon_concept_anchor):
            fetched = pc.fetch_online_canon_versions(auto, local)
        self.assertEqual(pc.resolve_canon_concept_anchor(local, auto), "10.5281/zenodo.21249056")
        pubs = {v.version for v in pc.list_online_published(fetched)}
        drafts = {v.version for v in pc.list_online_drafts(fetched)}
        self.assertIn("0.8.19", pubs)
        self.assertIn("0.8.20", drafts)
        self.assertFalse(pc.local_deposit_is_stale("0.8.19", local, fetched))

        with patch.object(pc, "read_config_data") as cfg_reader:
            def _cfg(ver):
                if ver == "0.8.19":
                    return {"doi": "10.5281/zenodo.21249056", "deposit_id": "21249056"}
                return {"doi": "10.5281/zenodo.21530432", "deposit_id": "21530432"}

            cfg_reader.side_effect = _cfg
            statuses = pc.compare_versions(local, fetched)
        st19 = next(s for s in statuses if s.version == "0.8.19")
        self.assertNotEqual(st19.status, "stale_deposit")
        self.assertEqual(st19.status, "published")


class UpdateDoiInCanonTexTests(unittest.TestCase):
    def test_fills_empty_paperdoi(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = Path(tmp) / "doc.tex"
            tex.write_text(
                "%! DOI = 10.5281/zenodo.OLD\n"
                r"\newcommand{\paperdoi}{}" + "\n"
                r"\title{Test}" + "\n",
                encoding="utf-8",
            )
            doi = "10.5281/zenodo.21531586"
            pc.update_doi_in_canon_tex(tex, doi)
            content = tex.read_text(encoding="utf-8")
            self.assertIn(f"%! DOI = {doi}", content)
            self.assertIn(rf"\newcommand{{\paperdoi}}{{{doi}}}", content)
            self.assertNotIn(r"\newcommand{\paperdoi}{}", content)

    def test_replaces_nonempty_paperdoi(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = Path(tmp) / "doc.tex"
            tex.write_text(
                r"\newcommand{\paperdoi}{10.5281/zenodo.OLD}" + "\n",
                encoding="utf-8",
            )
            doi = "10.5281/zenodo.21531586"
            pc.update_doi_in_canon_tex(tex, doi)
            content = tex.read_text(encoding="utf-8")
            self.assertIn(f"%! DOI = {doi}", content)
            self.assertIn(rf"\newcommand{{\paperdoi}}{{{doi}}}", content)
            self.assertNotIn("10.5281/zenodo.OLD", content)

    def test_inserts_paperdoi_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tex = Path(tmp) / "doc.tex"
            tex.write_text(r"\title{Test}" + "\n", encoding="utf-8")
            doi = "10.5281/zenodo.21531586"
            pc.update_doi_in_canon_tex(tex, doi)
            content = tex.read_text(encoding="utf-8")
            self.assertTrue(content.startswith(f"%! DOI = {doi}\n"))
            self.assertIn(rf"\newcommand{{\paperdoi}}{{{doi}}}", content)


if __name__ == "__main__":
    unittest.main()
