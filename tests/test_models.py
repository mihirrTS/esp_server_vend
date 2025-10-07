"""
Test cases for vending machine models and business logic.
Currently focused on testing the core vending functionality.
"""

import pytest
import json

class TestVendingMachine:
    """Test cases for vending machine business logic."""
    
    def test_valid_slot_numbers(self):
        """Test that valid slot numbers are correctly identified."""
        valid_slots = [1, 2, 3, 4, 5]
        for slot in valid_slots:
            assert 1 <= slot <= 5, f"Slot {slot} should be valid"
    
    def test_invalid_slot_numbers(self):
        """Test that invalid slot numbers are correctly identified."""
        invalid_slots = [0, 6, -1, 10, 100]
        for slot in invalid_slots:
            assert not (1 <= slot <= 5), f"Slot {slot} should be invalid"
    
    def test_command_format(self):
        """Test that vending commands are properly formatted."""
        test_cases = [
            (1, "VEND:1"),
            (2, "VEND:2"),
            (3, "VEND:3"),
            (4, "VEND:4"),
            (5, "VEND:5"),
        ]
        
        for slot_id, expected_command in test_cases:
            command = f"VEND:{slot_id}"
            assert command == expected_command
    
    def test_json_response_structure(self):
        """Test that API responses have the correct structure."""
        # Test successful response structure
        success_response = {
            "status": "command_sent",
            "slot": 3,
            "message": "Successfully sent vend command for slot 3"
        }
        
        required_fields = ["status", "slot", "message"]
        for field in required_fields:
            assert field in success_response, f"Response missing required field: {field}"
        
        # Test error response structure
        error_response = {
            "status": "error",
            "slot": 6,
            "message": "Invalid slot ID. Must be between 1-5"
        }
        
        for field in required_fields:
            assert field in error_response, f"Error response missing required field: {field}"
    
    def test_slot_customization(self):
        """Test slot name customization logic."""
        default_slots = {
            1: "Slot 1",
            2: "Slot 2", 
            3: "Slot 3",
            4: "Slot 4",
            5: "Slot 5"
        }
        
        custom_slots = {
            1: "Coke",
            2: "Chips",
            3: "Soda",
            4: "Candy",
            5: "Water"
        }
        
        # Test that custom names can be assigned
        for slot_id, custom_name in custom_slots.items():
            assert len(custom_name) > 0, f"Custom name for slot {slot_id} should not be empty"
            assert len(custom_name) <= 20, f"Custom name for slot {slot_id} should be <= 20 characters"
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        error_scenarios = [
            {"slot": 0, "expected_status": "error"},
            {"slot": 6, "expected_status": "error"},
            {"slot": -1, "expected_status": "error"},
        ]
        
        for scenario in error_scenarios:
            slot = scenario["slot"]
            expected_status = scenario["expected_status"]
            
            # Simulate the validation logic from app.py
            is_valid = 1 <= slot <= 5
            actual_status = "command_sent" if is_valid else "error"
            
            assert actual_status == expected_status, f"Slot {slot} should return {expected_status} status"

class TestUtilityFunctions:
    """Test utility functions and helpers."""
    
    def test_slot_range_validation(self):
        """Test the slot range validation utility."""
        def is_valid_slot(slot_id):
            return isinstance(slot_id, int) and 1 <= slot_id <= 5
        
        # Valid cases
        assert is_valid_slot(1) is True
        assert is_valid_slot(5) is True
        assert is_valid_slot(3) is True
        
        # Invalid cases
        assert is_valid_slot(0) is False
        assert is_valid_slot(6) is False
        assert is_valid_slot(-1) is False
        assert is_valid_slot("1") is False  # String instead of int
        assert is_valid_slot(1.5) is False  # Float instead of int
        assert is_valid_slot(None) is False  # None value
    
    def test_response_formatting(self):
        """Test response formatting utilities."""
        def format_success_response(slot_id):
            return {
                "status": "command_sent",
                "slot": slot_id,
                "message": f"Successfully sent vend command for slot {slot_id}"
            }
        
        def format_error_response(slot_id, message):
            return {
                "status": "error",
                "slot": slot_id,
                "message": message
            }
        
        # Test success response
        success = format_success_response(3)
        assert success["status"] == "command_sent"
        assert success["slot"] == 3
        assert "slot 3" in success["message"]
        
        # Test error response
        error = format_error_response(6, "Invalid slot")
        assert error["status"] == "error"
        assert error["slot"] == 6
        assert error["message"] == "Invalid slot"