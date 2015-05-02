import unittest
import os
from unittest.mock import MagicMock,patch
import sys
sys.path.append("../")
import DockerInstances
from DockerInstances import DockerInstance, DockerFileNotFoundError

class TestInitialization(unittest.TestCase):

	def test_invalid_path(self):
		with self.assertRaises(FileNotFoundError):
			instance = DockerInstance("invalidpath","")
	def test_path_not_directory(self):
		with self.assertRaises(ValueError):
			instance = DockerInstance("/home/deploy/demokratikollen/deployment/tests/test_generic_docker_instance.py","")
	def test_docker_file_exists(self):
		with self.assertRaises(DockerFileNotFoundError):
			instance = DockerInstance(".","")

	def test_valid_path(self):
		os.path.exists = MagicMock(return_value=True)
		os.path.isdir = MagicMock(return_value=True)
		try:
			instance = DockerInstance(".","")
		except:
			self.fail("Failed eventhough correct path")

	@patch('DockerInstances.os')
	def test_sets_tag(self, MockOs):
		tag = 'test'
		instance = DockerInstance(".", tag)
		self.assertEqual(instance.tag,tag)

class TestImageBuilding(unittest.TestCase):
	@patch('DockerInstances.os')
	@patch('DockerInstances.Client')
	def test_correct_parameters(self, MockClient, MockOs):
		instance = DockerInstance(".", "")
		instance.build_image()

		MockClient.assert_called_with(base_url='unix://var/run/docker.sock')
		MockClient.return_value.build.assert_called_with(rm=True,path=instance.path_to_files,tag=instance.tag)

	@patch('DockerInstances.os')
	@patch('DockerInstances.Client')
	def test_records_output(self, MockClient, MockOs):
		build_output = ["Line 1", "Line 2"]

		MockClient.return_value.build.return_value = build_output

		instance = DockerInstance(".", "")
		instance.build_image()

		self.assertEqual(instance.build_output ,build_output)

