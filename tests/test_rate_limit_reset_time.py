import asyncio
import time
import unittest
from unittest.mock import Mock, patch, AsyncMock

from tweepy.client import Client
from tweepy.asynchronous.client import AsyncClient
from tweepy.api import API
from tweepy.errors import TooManyRequests


class RateLimitResetTimeTests(unittest.TestCase):
    """Test cases for rate limit reset time functionality across all clients"""

    def setUp(self):
        """Set up test clients and mock data"""
        self.bearer_token = "fake_bearer_token"
        self.consumer_key = "fake_consumer_key"
        self.consumer_secret = "fake_consumer_secret"
        self.access_token = "fake_access_token"
        self.access_token_secret = "fake_access_token_secret"
        
        self.current_time = int(time.time())
        self.reset_time = self.current_time + 900  # 15 minutes from now
        self.reset_time_str = str(self.reset_time)

    def create_mock_429_response(self, include_reset_header=True, sync=True):
        """Helper to create mock 429 response"""
        mock_response = Mock()
        if sync:
            mock_response.status_code = 429
        else:
            mock_response.status = 429
        mock_response.reason = "Too Many Requests"
        
        headers = {}
        if include_reset_header:
            headers["x-rate-limit-reset"] = self.reset_time_str
        mock_response.headers = headers
        
        if not sync:
            # For async client
            mock_response.json = AsyncMock(return_value={
                "errors": [{"message": "Rate limit exceeded"}]
            })
        else:
            mock_response.json.return_value = {
                "errors": [{"message": "Rate limit exceeded"}]
            }
        
        return mock_response

    # Sync Client Tests
    def test_sync_client_rate_limit_with_reset_header_wait_false(self):
        """Test sync client raises TooManyRequests with reset_time when wait_on_rate_limit=False"""
        client = Client(bearer_token=self.bearer_token, wait_on_rate_limit=False)
        mock_response = self.create_mock_429_response(include_reset_header=True)
        
        # Mock the context manager behavior
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with self.assertRaises(TooManyRequests) as cm:
                client.request("GET", "/2/tweets/search/recent")
            
            exception = cm.exception
            self.assertEqual(exception.reset_time, self.reset_time)

    def test_sync_client_rate_limit_without_reset_header_wait_false(self):
        """Test sync client raises TooManyRequests with None reset_time when header missing"""
        client = Client(bearer_token=self.bearer_token, wait_on_rate_limit=False)
        mock_response = self.create_mock_429_response(include_reset_header=False)
        
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with self.assertRaises(TooManyRequests) as cm:
                client.request("GET", "/2/tweets/search/recent")
            
            exception = cm.exception
            self.assertIsNone(exception.reset_time)

    @patch('time.sleep')
    @patch('time.time')
    def test_sync_client_rate_limit_with_reset_header_wait_true(self, mock_time, mock_sleep):
        """Test sync client waits correctly when wait_on_rate_limit=True"""
        mock_time.return_value = self.current_time
        
        client = Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
        mock_response_429 = self.create_mock_429_response(include_reset_header=True)
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        
        # Mock context managers
        mock_response_429.__enter__ = Mock(return_value=mock_response_429)
        mock_response_429.__exit__ = Mock(return_value=None)
        mock_response_200.__enter__ = Mock(return_value=mock_response_200)
        mock_response_200.__exit__ = Mock(return_value=None)
        
        # First call returns 429, second call returns 200
        with patch.object(client.session, 'request', side_effect=[mock_response_429, mock_response_200]):
            result = client.request("GET", "/2/tweets/search/recent")
            
            # Should have slept for the calculated time
            expected_sleep_time = self.reset_time - self.current_time + 1
            mock_sleep.assert_called_once_with(expected_sleep_time)
            self.assertEqual(result, mock_response_200)

    @patch('time.sleep')
    @patch('time.time')
    def test_sync_client_rate_limit_without_reset_header_wait_true(self, mock_time, mock_sleep):
        """Test sync client handles missing header when wait_on_rate_limit=True"""
        mock_time.return_value = self.current_time
        
        client = Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
        mock_response_429 = self.create_mock_429_response(include_reset_header=False)
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        
        mock_response_429.__enter__ = Mock(return_value=mock_response_429)
        mock_response_429.__exit__ = Mock(return_value=None)
        mock_response_200.__enter__ = Mock(return_value=mock_response_200)
        mock_response_200.__exit__ = Mock(return_value=None)
        
        with patch.object(client.session, 'request', side_effect=[mock_response_429, mock_response_200]):
            result = client.request("GET", "/2/tweets/search/recent")
            
            # Should not have slept since no reset time available
            mock_sleep.assert_not_called()
            self.assertEqual(result, mock_response_200)

    # Async Client Tests
    def test_async_client_rate_limit_with_reset_header_wait_false(self):
        """Test async client raises TooManyRequests with reset_time when wait_on_rate_limit=False"""
        async def run_test():
            client = AsyncClient(bearer_token=self.bearer_token, wait_on_rate_limit=False)
            mock_response = self.create_mock_429_response(include_reset_header=True, sync=False)
            
            # Mock async context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.read = AsyncMock()
            
            with patch('aiohttp.ClientSession.request', return_value=mock_response):
                with self.assertRaises(TooManyRequests) as cm:
                    await client.request("GET", "/2/tweets/search/recent")
                
                exception = cm.exception
                self.assertEqual(exception.reset_time, self.reset_time)
        
        asyncio.run(run_test())

    def test_async_client_rate_limit_without_reset_header_wait_false(self):
        """Test async client raises TooManyRequests with None reset_time when header missing"""
        async def run_test():
            client = AsyncClient(bearer_token=self.bearer_token, wait_on_rate_limit=False)
            mock_response = self.create_mock_429_response(include_reset_header=False, sync=False)
            
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_response.read = AsyncMock()
            
            with patch('aiohttp.ClientSession.request', return_value=mock_response):
                with self.assertRaises(TooManyRequests) as cm:
                    await client.request("GET", "/2/tweets/search/recent")
                
                exception = cm.exception
                self.assertIsNone(exception.reset_time)
        
        asyncio.run(run_test())

    def test_async_client_rate_limit_with_reset_header_wait_true(self):
        """Test async client waits correctly when wait_on_rate_limit=True"""
        async def run_test():
            with patch('asyncio.sleep') as mock_sleep, \
                 patch('time.time', return_value=self.current_time):
                
                client = AsyncClient(bearer_token=self.bearer_token, wait_on_rate_limit=True)
                mock_response_429 = self.create_mock_429_response(include_reset_header=True, sync=False)
                mock_response_200 = Mock()
                mock_response_200.status = 200
                
                # Mock async context managers
                mock_response_429.__aenter__ = AsyncMock(return_value=mock_response_429)
                mock_response_429.__aexit__ = AsyncMock(return_value=None)
                mock_response_429.read = AsyncMock()
                
                mock_response_200.__aenter__ = AsyncMock(return_value=mock_response_200)
                mock_response_200.__aexit__ = AsyncMock(return_value=None)
                mock_response_200.read = AsyncMock()
                
                with patch('aiohttp.ClientSession.request', side_effect=[mock_response_429, mock_response_200]):
                    result = await client.request("GET", "/2/tweets/search/recent")
                    
                    expected_sleep_time = self.reset_time - self.current_time + 1
                    mock_sleep.assert_called_once_with(expected_sleep_time)
                    self.assertEqual(result, mock_response_200)
        
        asyncio.run(run_test())

    # API v1 Client Tests
    def test_api_v1_rate_limit_with_reset_time(self):
        """Test API v1 client passes reset_time to TooManyRequests exception"""
        # Create API with fake auth to bypass auth check
        from tweepy.auth import OAuthHandler
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        
        api = API(auth=auth, wait_on_rate_limit=False)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {"x-rate-limit-reset": self.reset_time_str}
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}
        
        with patch.object(api.session, 'request', return_value=mock_response):
            with self.assertRaises(TooManyRequests) as cm:
                api.request("GET", "statuses/user_timeline")
            
            exception = cm.exception
            self.assertEqual(exception.reset_time, self.reset_time)

    def test_api_v1_rate_limit_without_reset_time(self):
        """Test API v1 client handles missing reset_time"""
        # Create API with fake auth to bypass auth check
        from tweepy.auth import OAuthHandler
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        
        api = API(auth=auth, wait_on_rate_limit=False)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {}  # No reset time header
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}
        
        with patch.object(api.session, 'request', return_value=mock_response):
            with self.assertRaises(TooManyRequests) as cm:
                api.request("GET", "statuses/user_timeline")
            
            exception = cm.exception
            self.assertIsNone(exception.reset_time)


class RateLimitIntegrationTests(unittest.TestCase):
    """Integration tests showing how applications can use the reset_time feature"""

    def test_application_can_handle_reset_time(self):
        """Test that applications can access and use reset_time information"""
        client = Client(bearer_token="fake_token", wait_on_rate_limit=False)
        current_time = int(time.time())
        reset_time = current_time + 600  # 10 minutes from now
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {"x-rate-limit-reset": str(reset_time)}
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        
        with patch.object(client.session, 'request', return_value=mock_response), \
             patch('time.time', return_value=current_time):
            
            try:
                client.request("GET", "/2/tweets/search/recent")
                self.fail("Should have raised TooManyRequests")
            except TooManyRequests as e:
                # Application can now implement custom rate limit handling
                if e.reset_time:
                    sleep_time = e.reset_time - current_time
                    self.assertEqual(sleep_time, 600)
                    
                    # Application could show user-friendly message
                    import time as time_module
                    reset_time_str = time_module.ctime(e.reset_time)
                    self.assertIsInstance(reset_time_str, str)
                    
                    # Application could implement custom backoff
                    self.assertGreater(sleep_time, 0)
                else:
                    self.fail("reset_time should be available")

    def test_backward_compatibility_maintained(self):
        """Test that existing applications continue to work unchanged"""
        client = Client(bearer_token="fake_token", wait_on_rate_limit=False)
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.reason = "Too Many Requests"
        mock_response.headers = {}  # No reset header
        mock_response.json.return_value = {"errors": [{"message": "Rate limit exceeded"}]}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        
        with patch.object(client.session, 'request', return_value=mock_response):
            # Old application code that doesn't know about reset_time
            try:
                client.request("GET", "/2/tweets/search/recent")
                self.fail("Should have raised TooManyRequests")
            except TooManyRequests as e:
                # Should still work as before
                self.assertIsInstance(e, TooManyRequests)
                self.assertEqual(e.response.status_code, 429)
                # New attribute should be None when not available
                self.assertIsNone(e.reset_time)


if __name__ == '__main__':
    unittest.main()