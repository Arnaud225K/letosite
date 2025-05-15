from pathlib import Path
from django.test import TestCase
from unidecode import unidecode
import os

from .parser import parse_data
import urllib3
import requests




class TestParser(TestCase):
	def test_parser(self):
		
		yaml_url = 'https://aquapolis.ru/media/astrio/feed/forpartners_quantity_default.yml'
		response = requests.get(yaml_url)

		if response.status_code == 200:
			parsed_data = parse_data(response.content.decode('utf-8'))

			# Check if categories and offers are not empty
			self.assertIsNotNone(parsed_data)
			self.assertIn('categories', parsed_data)
			self.assertIn('offers', parsed_data)
			
			# Check if categories and offers are not empty
			self.assertGreater(len(parsed_data['categories']), 0)
			self.assertGreater(len(parsed_data['offers']), 0)

			# Print all categories hierarchically
			def print_categories(categories, level=0):
				indent = "  " * level  # Indentation based on level
				for category in categories:
					print(f"{indent}- ID: {category['id']}, Name: {category['name']}")
					print_categories(category['children'], level + 1)

			print("\nCategories:")
			print_categories(parsed_data['categories'])

			# Print the first offer if available
			if parsed_data['offers']:
				print("\nFirst Offer:")
				print(parsed_data['offers'][0])
            # Print all offers
			
			# def print_offers(offers):
			# 	for offer in offers:
			# 		print("Offer Details:")
			# 		for key, value in offer.items():
			# 			print(f"{key}: {value}")
			# 		print("-" * 40)  # Separator between offers
			
			# print("\nOffers:")
			# print_offers(parsed_data['offers'])
		
		else:
			print("Error server 500")