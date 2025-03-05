import xml.etree.ElementTree as ET
import csv
import io
import unittest

from xml_processor import XMLProcessor  # Make sure xml_processor.py is in the same directory

class TestXMLProcessor(unittest.TestCase):
    def setUp(self):
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<document>
    <omsection>
       <head>Section Title 1</head>
       <block>
          <head>Subsection Title 1.1</head>
          <para>Content of subsection 1.1.</para>
       </block>
       <block>
          <head>Subsection Title 1.2</head>
          <para>Content of subsection 1.2.</para>
       </block>
    </omsection>
    <omsection>
       <head>Section Title 2</head>
       <para>Content of section 2 without block.</para>
    </omsection>
</document>
"""
        self.test_xml_file = io.StringIO(self.sample_xml)
        self.tree = ET.ElementTree(file=self.test_xml_file)
        self.processor = XMLProcessor.__new__(XMLProcessor)
        self.processor.tree = self.tree

    def test_extract_data(self):
        data = self.processor.extract_data()
        # Expect three entries: two for section 1 (with blocks) and one for section 2 (without block)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['section'], "Section Title 1")
        self.assertEqual(data[0]['subsection'], "Subsection Title 1.1")
        self.assertEqual(data[0]['content'], "Content of subsection 1.1.")
        self.assertEqual(data[1]['subsection'], "Subsection Title 1.2")
        self.assertEqual(data[1]['content'], "Content of subsection 1.2.")
        self.assertEqual(data[2]['section'], "Section Title 2")
        self.assertEqual(data[2]['subsection'], "")
        self.assertEqual(data[2]['content'], "Content of section 2 without block.")

    def test_store_data_in_csv(self):
        data = self.processor.extract_data()
        output = io.StringIO()
        fieldnames = ['section', 'subsection', 'content']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        csv_content = output.getvalue()
        self.assertIn("section,subsection,content", csv_content)
        self.assertIn("Section Title 1", csv_content)
        self.assertIn("Subsection Title 1.1", csv_content)
        self.assertIn("Content of subsection 1.1.", csv_content)
        output.close()


if __name__ == "__main__":
    unittest.main()
