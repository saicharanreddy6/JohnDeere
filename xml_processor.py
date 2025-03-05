import xml.etree.ElementTree as ET
import csv
import logging

# Set up logging for production use
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class XMLProcessor:
    """
    Processes an XML file by extracting text data based on sections and subsections.
    In the version I used, each <omsection> element is considered a section. If it contains
    <block> children, each block is treated as a subsection; otherwise, the section's
    own content is used. Any <para> elements are collected and any table elements are
    converted to Markdown.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = self.parse_xml_file()

    def parse_xml_file(self):
        """Parses the XML file and returns an ElementTree."""
        try:
            tree = ET.parse(self.file_path)
            logging.info(f"Successfully parsed XML file: {self.file_path}")
            return tree
        except Exception as e:
            logging.error(f"Error parsing XML file: {e}")
            raise

    def get_full_text(self, element):
        """Recursively collects and returns all text from an element."""
        return " ".join(element.itertext()).strip() if element is not None else ""

    def extract_data(self):
        """
        Extracts text content from each <omsection> (section) and its child <block>
        elements (subsections). Returns a list of dictionaries with keys: 'section',
        'subsection', and 'content'.
        """
        root = self.tree.getroot()
        data = []
        # Use "omsection" as the section element.
        for section in root.findall(".//omsection"):
            section_head = section.find("head")
            section_title = self.get_full_text(section_head) if section_head is not None else "No Section Title"
            blocks = section.findall("block")
            if not blocks:
                # No block elements; extract content directly from the section.
                content = self.get_content_from_element(section)
                data.append({
                    'section': section_title,
                    'subsection': '',
                    'content': content
                })
            else:
                for block in blocks:
                    block_head = block.find("head")
                    subsection_title = self.get_full_text(block_head) if block_head is not None else "No Subsection Title"
                    content = self.get_content_from_element(block)
                    data.append({
                        'section': section_title,
                        'subsection': subsection_title,
                        'content': content
                    })
        return data

    def get_content_from_element(self, element):
        """
        Extracts text from all <para> elements within the given element.
        Also converts any contained <table> elements to Markdown.
        """
        texts = []
        # Extract text from <para> tags
        for para in element.findall(".//para"):
            para_text = para.text.strip() if para.text else ""
            if para_text:
                texts.append(para_text)
        # Convert table elements to Markdown if present
        for table in element.findall(".//table"):
            md_table = self.convert_table_to_markdown(table)
            if md_table:
                texts.append(md_table)
        return "\n".join(texts)

    def convert_table_to_markdown(self, table_element):
        """
        Converts an XML table (with rows containing <entry> or <cell> elements) to Markdown.
        Assumes the first row is the header.
        """
        rows = []
        for row in table_element.findall(".//row"):
            # Try to extract cells from <entry> tags (common in complex DTDs)
            cells = [cell.text.strip() if cell.text else "" for cell in row.findall(".//entry")]
            if not cells:
                # Fallback: use <cell> if <entry> is not found.
                cells = [cell.text.strip() if cell.text else "" for cell in row.findall(".//cell")]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        header = rows[0]
        separator = ["---"] * len(header)
        md_lines = []
        md_lines.append("| " + " | ".join(header) + " |")
        md_lines.append("| " + " | ".join(separator) + " |")
        for row in rows[1:]:
            md_lines.append("| " + " | ".join(row) + " |")
        return "\n".join(md_lines)

    def store_data_in_csv(self, data, output_file):
        """
        Writes the extracted data to a CSV file. 'data' is a list of dictionaries with
        keys: 'section', 'subsection', and 'content'.
        """
        try:
            with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ['section', 'subsection', 'content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            logging.info(f"Data successfully written to CSV file: {output_file}")
        except Exception as e:
            logging.error(f"Error writing CSV file: {e}")
            raise


def main():
    input_file = "omdxe11330.xml"  # Ensure this file is in your working directory
    output_csv = "output.csv"
    try:
        processor = XMLProcessor(input_file)
        data = processor.extract_data()
        processor.store_data_in_csv(data, output_csv)
        print(f"CSV file '{output_csv}' generated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
