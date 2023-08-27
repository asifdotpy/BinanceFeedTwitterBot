from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, Mock

class CreatorProfileTests(TestCase):
    @patch('creatorProfile.views.cache')
    @patch('creatorProfile.views.requests')
    def test_creator_details_not_in_cache(self, mock_requests, mock_cache):
        # Set up mock objects
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.content = b'<html></html>'
        mock_requests.get.return_value = mock_response
        
        # Get the URL for the creator_details view
        url = reverse('creator_details')
        
        # Send a GET request to the creator_details view
        response = self.client.get(url)
        
        # Check that the cache.get method was called with the correct arguments
        mock_cache.get.assert_called_once_with('creator_info')
        
        # Check that the requests.get method was called with the correct arguments
        mock_requests.get.assert_called_once()
        
        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
    
    @patch('creatorProfile.views.cache')
    @patch('creatorProfile.views.requests')
    def test_creator_details_exception(self, mock_requests, mock_cache):
        # Set up mock objects to raise an exception
        mock_cache.get.side_effect = Exception('Test exception')
        
        # Get the URL for the creator_details view
        url = reverse('creator_details')
        
        # Send a GET request to the creator_details view
        response = self.client.get(url)
        
        # Check that the response status code is 500 (Internal Server Error)
        self.assertEqual(response.status_code, 500)
        
        # Check that the response contains the expected error message
        self.assertJSONEqual(response.content, {'message': 'Something went wrong. Please try again later.'})

