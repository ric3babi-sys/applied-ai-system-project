import pytest

import app as pawpal_app
from app import parse_month_word_date


class TestReliabilityMetrics:
    """Reliability-focused tests for critical natural language scheduling behavior."""

    def setup_method(self):
        pawpal_app.clearAllData()
        pawpal_app.st.session_state.clear()
        pawpal_app.init_pawpal_session()

    def test_month_word_date_parser_accepts_full_month_names(self):
        """Verify the parser accepts full month names in both orders."""
        assert parse_month_word_date("Feed Mochi on August 25 2026 at 18:00") == "2026-08-25"
        assert parse_month_word_date("Feed Mochi on 25 August 2026 at 18:00") == "2026-08-25"

    def test_month_word_date_parser_accepts_abbreviated_month_names(self):
        """Verify the parser accepts abbreviated month names in both orders."""
        assert parse_month_word_date("Feed Mochi on Aug 25, 2026 at 18:00") == "2026-08-25"
        assert parse_month_word_date("Feed Mochi on 25 Aug 2026 at 18:00") == "2026-08-25"

    def test_natural_language_schedule_supports_month_word_dates(self):
        """Verify the natural language scheduler accepts month-word date inputs."""
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result_full = pawpal_app.execute_natural_language_input(
            "Feed Mochi on August 25 2026 at 18:00"
        )
        result_short = pawpal_app.execute_natural_language_input(
            "Feed Mochi on Aug 25, 2026 at 18:00"
        )

        assert result_full['success'] is True
        assert result_short['success'] is True
        assert "Scheduled on 2026-08-25 at 18:00" in result_full.get('details', "")
        assert "Scheduled on 2026-08-25 at 18:00" in result_short.get('details', "")

    def test_month_word_date_parser_rejects_invalid_month_word(self):
        """Verify the parser rejects invalid month words that should not parse."""
        assert parse_month_word_date("Feed Mochi on Feber 25 2026 at 18:00") is None
        assert parse_month_word_date("Feed Mochi on 25 Feber 2026 at 18:00") is None

    def test_month_word_date_parser_accepts_day_suffixes(self):
        """Verify the parser accepts day suffixes in month-word date formats."""
        assert parse_month_word_date("Feed Mochi on 25th August 2026 at 18:00") == "2026-08-25"
        assert parse_month_word_date("Feed Mochi on August 25th 2026 at 18:00") == "2026-08-25"
        assert parse_month_word_date("Feed Mochi on 25th Aug 2026 at 18:00") == "2026-08-25"
        assert parse_month_word_date("Feed Mochi on Aug 25th 2026 at 18:00") == "2026-08-25"

    def test_natural_language_schedule_accepts_day_suffix_month_word_dates(self):
        """Verify the app accepts day-suffix month-word natural language schedule commands."""
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result_full = pawpal_app.execute_natural_language_input(
            "Feed Mochi on 25th August 2026 at 18:00"
        )
        result_short = pawpal_app.execute_natural_language_input(
            "Feed Mochi on Aug 25th 2026 at 18:00"
        )

        assert result_full['success'] is True
        assert result_short['success'] is True
        assert "Scheduled on 2026-08-25 at 18:00" in result_full.get('details', "")
        assert "Scheduled on 2026-08-25 at 18:00" in result_short.get('details', "")

    def test_natural_language_schedule_rejects_date_without_time(self):
        """Verify commands with a date but no HH:MM time are rejected."""
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result = pawpal_app.execute_natural_language_input(
            "Feed Mochi on August 25 2026"
        )

        assert result['success'] is False
        assert "time" in result['message'].lower()

    def test_natural_language_schedule_rejects_invalid_time_format(self):
        """Verify commands with invalid time formats are rejected."""
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result = pawpal_app.execute_natural_language_input(
            "Feed Mochi on Aug 25 2026 at 6pm"
        )

        assert result['success'] is False
        assert "time" in result['message'].lower()

    def test_natural_language_schedule_with_time_only_creates_task(self):
        """Verify commands with time but no date create a task without a schedule."""
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result = pawpal_app.execute_natural_language_input("Feed Mochi at 18:00")

        assert result['success'] is True
        assert result.get('details') is None
        pet = pawpal_app.find_pet_by_name("Mochi")
        task = pawpal_app.find_task_for_pet(pet, 1)
        assert task is not None

    @pytest.mark.parametrize(
        "command",
        [
            "feed Mochi on August 25 2026 at 18:00",
            "feed Mochi on 25 August 2026 at 18:00",
            "feed Mochi on Aug 25, 2026 at 18:00",
            "feed Mochi on 25 Aug 2026 at 18:00",
            "walk Mochi on August 25 2026 at 09:00",
            "walk Mochi on 25 August 2026 at 09:00",
            "walk Mochi on Aug 25, 2026 at 09:00",
            "walk Mochi on 25 Aug 2026 at 09:00",
            "Feed PET Mochi on Aug 25 2026 at 18:00",
            "WALK pet Mochi on August 25 2026 at 09:00",
        ],
    )
    def test_natural_language_command_variants_schedule_successfully(self, command):
        """Verify a set of natural language schedule variants are accepted and parsed."""
        pawpal_app.clearAllData()
        pawpal_app.st.session_state.clear()
        pawpal_app.init_pawpal_session()
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result = pawpal_app.execute_natural_language_input(command)

        assert result['success'] is True, f"Command failed: {command}"
        assert "Scheduled on 2026-08-25" in result.get('details', ""), f"No schedule created for: {command}"

    @pytest.mark.parametrize(
        "command",
        [
            "Feed Mochi on August 25 2026 at 6pm",
            "Feed Mochi on Aug 25 2026 at 1800",
            "Feed Mochi on 25th August 2026",
            "Feed Mochi on Aug 25 2026",
            "Feed Mochi at 6pm",
        ],
    )
    def test_natural_language_command_variants_reject_invalid_time_or_date(self, command):
        """Verify invalid time/date variants are rejected consistently."""
        pawpal_app.clearAllData()
        pawpal_app.st.session_state.clear()
        pawpal_app.init_pawpal_session()
        pawpal_app.execute_natural_language_input("Add owner Jordan")
        pawpal_app.execute_natural_language_input("Add pet Mochi for Jordan")

        result = pawpal_app.execute_natural_language_input(command)

        assert result['success'] is False, f"Unexpected success for invalid command: {command}"
        assert "time" in result['message'].lower() or "could not identify" in result['message'].lower()
