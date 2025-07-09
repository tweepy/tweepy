import time
import unittest
from unittest.mock import Mock

from tweepy.errors import TooManyRequests, HTTPException


class TooManyRequestsTests(unittest.TestCase):
    """Test cases for TooManyRequests exception with reset_time feature"""

    def setUp(self):
        """Set up mock response for testing"""
        self.mock_response = Mock()
        self.mock_response.status_code = 429
        self.mock_response.reason = "Too Many Requests"
        self.mock_response.json.return_value = {
            "errors": [{"message": "Rate limit exceeded"}]
        }
        
        self.test_reset_time = int(time.time()) + 900  # 15 minutes from now

    def test_too_many_requests_with_reset_time(self):
        """Test that TooManyRequests exception stores reset_time correctly"""
        exception = TooManyRequests(self.mock_response, reset_time=self.test_reset_time)
        
        self.assertEqual(exception.reset_time, self.test_reset_time)
        self.assertIsInstance(exception, HTTPException)
        self.assertEqual(str(exception), "429 Too Many Requests\nRate limit exceeded")

    def test_too_many_requests_without_reset_time(self):
        """Test that TooManyRequests exception handles None reset_time"""
        exception = TooManyRequests(self.mock_response)
        
        self.assertIsNone(exception.reset_time)
        self.assertIsInstance(exception, HTTPException)

    def test_too_many_requests_explicit_none_reset_time(self):
        """Test that TooManyRequests exception handles explicit None reset_time"""
        exception = TooManyRequests(self.mock_response, reset_time=None)
        
        self.assertIsNone(exception.reset_time)
        self.assertIsInstance(exception, HTTPException)

    def test_too_many_requests_with_response_json(self):
        """Test that TooManyRequests exception works with response_json parameter"""
        response_json = {"errors": [{"message": "Custom rate limit message"}]}
        exception = TooManyRequests(
            self.mock_response, 
            response_json=response_json, 
            reset_time=self.test_reset_time
        )
        
        self.assertEqual(exception.reset_time, self.test_reset_time)
        self.assertEqual(str(exception), "429 Too Many Requests\nCustom rate limit message")

    def test_too_many_requests_backward_compatibility(self):
        """Test that old constructor usage still works (backward compatibility)"""
        # This is how TooManyRequests was called before the enhancement
        exception = TooManyRequests(self.mock_response)
        
        self.assertIsNone(exception.reset_time)
        self.assertIsInstance(exception, HTTPException)
        # Should still have all the original HTTPException functionality
        self.assertEqual(exception.response, self.mock_response)

    def test_too_many_requests_inheritance(self):
        """Test that TooManyRequests still properly inherits from HTTPException"""
        exception = TooManyRequests(self.mock_response, reset_time=self.test_reset_time)
        
        # Should inherit all HTTPException attributes
        self.assertTrue(hasattr(exception, 'response'))
        self.assertTrue(hasattr(exception, 'api_errors'))
        self.assertTrue(hasattr(exception, 'api_codes'))
        self.assertTrue(hasattr(exception, 'api_messages'))
        
        # Should have the new reset_time attribute
        self.assertTrue(hasattr(exception, 'reset_time'))
        self.assertEqual(exception.reset_time, self.test_reset_time)

    def test_too_many_requests_with_zero_reset_time(self):
        """Test that TooManyRequests exception handles zero reset_time"""
        exception = TooManyRequests(self.mock_response, reset_time=0)
        
        self.assertEqual(exception.reset_time, 0)

    def test_too_many_requests_with_negative_reset_time(self):
        """Test that TooManyRequests exception handles negative reset_time (past time)"""
        past_time = int(time.time()) - 3600  # 1 hour ago
        exception = TooManyRequests(self.mock_response, reset_time=past_time)
        
        self.assertEqual(exception.reset_time, past_time)

    def test_too_many_requests_reset_time_type(self):
        """Test that reset_time can be different integer types"""
        # Test with string that can be converted to int (as it comes from headers)
        exception1 = TooManyRequests(self.mock_response, reset_time=str(self.test_reset_time))
        self.assertEqual(exception1.reset_time, str(self.test_reset_time))
        
        # Test with actual int
        exception2 = TooManyRequests(self.mock_response, reset_time=self.test_reset_time)
        self.assertEqual(exception2.reset_time, self.test_reset_time)


if __name__ == '__main__':
    unittest.main()