"""Parse markdown files and convert to HTML for display."""

import markdown

from . import config


class MarkdownParser:
    """Handle markdown parsing and HTML conversion."""

    def __init__(self):
        """Initialize the markdown parser with extensions."""
        self.md = markdown.Markdown(extensions=['extra', 'nl2br'])
        self.css = self._generate_css()

    def _generate_css(self) -> str:
        """Generate CSS for teleprompter styling."""
        return f"""
        <style>
            body {{
                background-color: {config.BACKGROUND_COLOR};
                color: {config.TEXT_COLOR};
                font-family: {config.DEFAULT_FONT_FAMILY}, sans-serif;
                font-size: {config.DEFAULT_FONT_SIZE}px;
                line-height: 1.6;
                padding: 20px;
                margin: 0;
                text-align: center;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {config.TEXT_COLOR};
                margin: 20px 0;
            }}
            h1 {{ font-size: 2.5em; }}
            h2 {{ font-size: 2.0em; }}
            h3 {{ font-size: 1.7em; }}
            h4 {{ font-size: 1.5em; }}
            h5 {{ font-size: 1.3em; }}
            h6 {{ font-size: 1.1em; }}
            p {{
                margin: 15px 0;
            }}
            ul, ol {{
                text-align: left;
                display: inline-block;
                margin: 15px 0;
            }}
            a {{
                color: {config.TEXT_COLOR};
                text-decoration: underline;
            }}
            strong {{
                font-weight: bold;
            }}
            em {{
                font-style: italic;
            }}
        </style>
        """

    def parse_file(self, file_path: str) -> str:
        """Parse a markdown file and return HTML content."""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Check file size
            if len(content.encode('utf-8')) > config.MAX_FILE_SIZE:
                raise ValueError(f"File size exceeds {config.MAX_FILE_SIZE / 1024 / 1024}MB limit")

            return self.parse_content(content)
        except Exception as e:
            raise Exception(f"Error reading markdown file: {str(e)}") from e

    def parse_content(self, content: str) -> str:
        """Parse markdown content and return HTML with styling."""
        html_content = self.md.convert(content)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            {self.css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

    def update_font_size(self, size: int) -> str:
        """Update CSS with new font size."""
        self.css = self._generate_css().replace(
            f"font-size: {config.DEFAULT_FONT_SIZE}px;",
            f"font-size: {size}px;"
        )
        return self.css
