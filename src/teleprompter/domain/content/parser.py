"""Parse markdown files and convert to HTML for display."""

import re

import markdown

from teleprompter.core.configuration import get_config
from teleprompter.core.protocols import ContentParserProtocol
from teleprompter.infrastructure.logging import LoggerMixin


class LoadingState:
    """Represents different loading states."""

    IDLE = "idle"
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"


class MarkdownParsingError(Exception):
    """Custom exception for markdown parsing errors."""

    pass


class FileLoadingError(Exception):
    """Custom exception for file loading errors."""

    pass


class MarkdownParser(ContentParserProtocol, LoggerMixin):
    """Handle markdown parsing and HTML conversion with enhanced error handling.

    This class implements the ContentParserProtocol to provide markdown
    parsing functionality for the teleprompter application.
    """

    def __init__(self):
        """Initialize the markdown parser with extensions."""
        self.config = get_config()
        self.md = markdown.Markdown(extensions=["extra", "nl2br"])
        self.css = self._generate_css()
        self.current_state = LoadingState.IDLE
        self.last_error = None

    def _generate_css(self) -> str:
        """Generate CSS for teleprompter styling with enhanced typography."""
        # Get configuration values with defaults
        bg_color = self.config.get("BACKGROUND_COLOR", "#000000")
        text_color = self.config.get("TEXT_COLOR", "#FFFFFF")
        font_family = self.config.get("DEFAULT_FONT_FAMILY", "Arial, sans-serif")
        font_size = self.config.get("DEFAULT_FONT_SIZE", 24)
        accent_color = self.config.get("ACCENT_COLOR", "#4A90E2")
        # max_file_size = self.config.get('MAX_FILE_SIZE', 1048576)  # Unused variable
        # primary_colors = self.config.get('PRIMARY_COLORS', {  # Unused variable
        #     "400": "#42a5f5",
        #     "500": "#2196f3",
        #     "600": "#1e88e5"
        # })

        return f"""<style>
            /* Reset and base typography */
            * {{
                box-sizing: border-box;
            }}

            body {{
                background-color: {bg_color};
                color: {text_color};
                font-family: {font_family};
                font-size: {font_size}px;
                font-weight: 400;
                line-height: 1.6;
                letter-spacing: 0.01em;
                padding: 40px 20px;
                margin: 0;
                text-align: center;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;

                /* Add bottom padding for better scrolling experience */
                padding-bottom: 50vh;
            }}

            /* Enhanced heading typography */
            h1, h2, h3, h4, h5, h6 {{
                color: {text_color};
                margin: 1.5em 0 0.8em 0;
                font-weight: 600;
                letter-spacing: -0.02em;
                line-height: 1.2;
            }}

            h1 {{
                font-size: 2.5em;
                font-weight: 700;
                margin-top: 0;
            }}
            h2 {{
                font-size: 2.0em;
                font-weight: 650;
            }}
            h3 {{
                font-size: 1.7em;
                font-weight: 600;
            }}
            h4 {{
                font-size: 1.5em;
                font-weight: 600;
            }}
            h5 {{
                font-size: 1.3em;
                font-weight: 500;
            }}
            h6 {{
                font-size: 1.1em;
                font-weight: 500;
            }}

            /* Improved paragraph spacing */
            p {{
                margin: 1.2em 0;
                max-width: 80%;
                margin-left: auto;
                margin-right: auto;
            }}

            /* Better list styling */
            ul, ol {{
                text-align: left;
                display: inline-block;
                margin: 1.5em 0;
                padding-left: 2em;
                max-width: 80%;
            }}

            li {{
                margin: 0.5em 0;
                line-height: 1.6;
            }}

            /* Enhanced link styling */
            a {{
                color: {accent_color};
                text-decoration: none;
                border-bottom: 1px solid {accent_color};
                transition: all 0.2s ease;
            }}

            a:hover {{
                color: {text_color};
                border-bottom-color: {text_color};
            }}

            /* Code styling */
            code {{
                background-color: rgba(255, 255, 255, 0.1);
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: Monaco, 'Courier New', monospace;
                font-size: 0.9em;
            }}

            pre {{
                background-color: rgba(255, 255, 255, 0.05);
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
                margin: 1.5em auto;
                max-width: 90%;
            }}

            /* Blockquote styling */
            blockquote {{
                border-left: 4px solid {accent_color};
                padding-left: 1.5em;
                margin: 1.5em auto;
                font-style: italic;
                max-width: 80%;
                opacity: 0.9;
            }}

            /* Table styling */
            table {{
                margin: 1.5em auto;
                border-collapse: collapse;
                max-width: 90%;
            }}

            th, td {{
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 0.8em;
                text-align: left;
            }}

            th {{
                background-color: rgba(255, 255, 255, 0.1);
                font-weight: 600;
            }}

            /* Emphasis styling */
            strong {{
                font-weight: 600;
                color: {text_color};
            }}

            em {{
                font-style: italic;
                color: {accent_color};
            }}

            /* Horizontal rule */
            hr {{
                border: none;
                height: 1px;
                background: linear-gradient(to right, transparent, {accent_color}, transparent);
                margin: 2em auto;
                max-width: 60%;
            }}
</style>"""

    def parse_file(self, file_path: str) -> str:
        """Parse a markdown file and return HTML content."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check file size
            max_size = self.config.get("MAX_FILE_SIZE", 1048576)
            if len(content.encode("utf-8")) > max_size:
                raise ValueError(f"File size exceeds maximum of {max_size} bytes")

            # Convert markdown to HTML
            html_content = self.md.convert(content)

            # Generate full HTML document
            return self._create_html_document(html_content)

        except Exception as e:
            raise ValueError(f"Error parsing markdown file: {str(e)}") from e

    def parse_content(self, markdown_text: str) -> str:
        """Parse markdown text and return HTML content."""
        try:
            # Convert markdown to HTML
            html_content = self.md.convert(markdown_text)

            # Generate full HTML document
            return self._create_html_document(html_content)

        except Exception as e:
            raise ValueError(f"Error parsing markdown content: {str(e)}") from e

    def _create_html_document(self, body_content: str) -> str:
        """Create a complete HTML document with CSS styling."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teleprompter</title>
    {self.css}
</head>
<body>
    {body_content}
</body>
</html>"""

    def get_loading_state(self) -> str:
        """Get the current loading state."""
        return self.current_state

    def get_last_error(self) -> str:
        """Get the last error message."""
        return self.last_error

    def _set_state(self, state: str, error_message: str = None):
        """Set the loading state and optional error message."""
        self.current_state = state
        if error_message:
            self.last_error = error_message
        elif state == LoadingState.SUCCESS:
            self.last_error = None

    def _generate_error_html(
        self, error_message: str, error_type: str = "File Error"
    ) -> str:
        """Generate HTML for error display with retry options."""
        return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Error Loading Content</title>
            {self.css}
            <style>
                .error-container {{
                    max-width: 600px;
                    margin: 20vh auto;
                    padding: 40px;
                    text-align: center;
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 rgba(220, 53, 69, 0.1),
                        stop: 1 rgba(220, 53, 69, 0.05));
                    border: 2px solid rgba(220, 53, 69, 0.3);
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(220, 53, 69, 0.2);
                }}

                .error-icon {{
                    font-size: 48px;
                    color: #dc3545;
                    margin-bottom: 20px;
                }}

                .error-title {{
                    font-size: 24px;
                    font-weight: 600;
                    color: #dc3545;
                    margin-bottom: 16px;
                }}

                .error-message {{
                    font-size: 16px;
                    color: {self.config.get("TEXT_COLOR", "#FFFFFF")};
                    margin-bottom: 24px;
                    line-height: 1.5;
                }}

                .error-suggestions {{
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.7);
                    margin-top: 20px;
                }}

                .suggestion-list {{
                    list-style: none;
                    padding: 0;
                    margin: 16px 0;
                }}

                .suggestion-list li {{
                    margin: 8px 0;
                    padding: 8px 16px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-title">{error_type}</div>
                <div class="error-message">{error_message}</div>

                <div class="error-suggestions">
                    <strong>Try these solutions:</strong>
                    <ul class="suggestion-list">
                        <li>📁 Check that the file exists and is accessible</li>
                        <li>📝 Verify the file contains valid Markdown content</li>
                        <li>🔒 Ensure you have permission to read the file</li>
                        <li>🔄 Try opening a different file</li>
                    </ul>
                </div>
            </div>
</body>
</html>"""

    def _generate_loading_html(self) -> str:
        """Generate HTML for loading state display."""
        return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Loading Content</title>
            {self.css}
            <style>
                .loading-container {{
                    max-width: 400px;
                    margin: 30vh auto;
                    padding: 40px;
                    text-align: center;
                }}

                .loading-spinner {{
                    width: 48px;
                    height: 48px;
                    border: 4px solid rgba(255, 255, 255, 0.1);
                    border-left: 4px solid #42a5f5;
                    border-radius: 50%;
                    margin: 0 auto 24px;
                    animation: spin 1s linear infinite;
                }}

                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}

                .loading-text {{
                    font-size: 18px;
                    color: {self.config.get("TEXT_COLOR", "#FFFFFF")};
                    margin-bottom: 8px;
                }}

                .loading-subtitle {{
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.6);
                }}
            </style>
        </head>
        <body>
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading Content</div>
                <div class="loading-subtitle">Please wait while we prepare your document...</div>
            </div>
</body>
</html>"""

    def _generate_empty_state_html(self) -> str:
        """Generate HTML for empty state display when no file is loaded."""
        # Get configuration values with defaults
        text_color = self.config.get("TEXT_COLOR", "#FFFFFF")
        accent_color = self.config.get("ACCENT_COLOR", "#4A90E2")
        primary_colors = self.config.get(
            "PRIMARY_COLORS", {"500": "#2196f3", "600": "#1e88e5"}
        )

        return f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Teleprompter</title>
            {self.css}
            <style>
                .empty-container {{
                    max-width: 600px;
                    margin: 20vh auto;
                    padding: 40px;
                    text-align: center;
                }}

                .empty-icon {{
                    font-size: 72px;
                    margin-bottom: 24px;
                    opacity: 0.6;
                }}

                .empty-title {{
                    font-size: 28px;
                    font-weight: 600;
                    color: {text_color};
                    margin-bottom: 16px;
                }}

                .empty-subtitle {{
                    font-size: 18px;
                    color: rgba(255, 255, 255, 0.7);
                    margin-bottom: 32px;
                    line-height: 1.5;
                }}

                .empty-actions {{
                    margin-top: 32px;
                }}

                .empty-suggestion {{
                    display: inline-block;
                    margin: 8px 16px;
                    padding: 12px 24px;
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 {primary_colors["600"]},
                        stop: 1 {primary_colors["500"]});
                    border-radius: 8px;
                    color: white;
                    text-decoration: none;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
                }}

                .empty-suggestion:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
                }}

                .feature-list {{
                    list-style: none;
                    padding: 0;
                    margin: 32px 0;
                    text-align: left;
                    display: inline-block;
                }}

                .feature-list li {{
                    margin: 12px 0;
                    padding: 8px 0;
                    font-size: 16px;
                    color: rgba(255, 255, 255, 0.8);
                }}

                /* Qt WebEngine doesn't fully support ::before with content */
                .feature-list li {{
                    list-style: none;
                    position: relative;
                    padding-left: 24px;
                }}

                .keyboard-shortcuts {{
                    margin-top: 32px;
                    padding: 24px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .shortcuts-title {{
                    font-size: 16px;
                    font-weight: 600;
                    margin-bottom: 16px;
                    color: {accent_color};
                }}

                .shortcut-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                    font-size: 14px;
                }}

                .shortcut-key {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-family: monospace;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="empty-container">
                <div class="empty-icon">📖</div>
                <div class="empty-title">Welcome to Teleprompter</div>
                <div class="empty-subtitle">
                    Transform your presentations with smooth, professional teleprompter scrolling
                </div>

                <ul class="feature-list">
                    <li>✨ Smooth auto-scrolling with adjustable speed</li>
                    <li>✨ Voice control with pause on silence</li>
                    <li>✨ Beautiful typography and themes</li>
                    <li>✨ Reading progress tracking</li>
                    <li>✨ Keyboard shortcuts for easy control</li>
                    <li>✨ Markdown support with live preview</li>
                </ul>

                <div class="empty-actions">
                    <div class="empty-suggestion">Press Ctrl+O to open a file</div>
                </div>

                <div class="keyboard-shortcuts">
                    <div class="shortcuts-title">Keyboard Shortcuts</div>
                    <div class="shortcut-row">
                        <span>Open File</span>
                        <span class="shortcut-key">Ctrl+O</span>
                    </div>
                    <div class="shortcut-row">
                        <span>Play/Pause</span>
                        <span class="shortcut-key">Space</span>
                    </div>
                    <div class="shortcut-row">
                        <span>Increase Speed</span>
                        <span class="shortcut-key">+</span>
                    </div>
                    <div class="shortcut-row">
                        <span>Decrease Speed</span>
                        <span class="shortcut-key">-</span>
                    </div>
                    <div class="shortcut-row">
                        <span>Reset Position</span>
                        <span class="shortcut-key">R</span>
                    </div>
                    <div class="shortcut-row">
                        <span>Toggle Voice Control</span>
                        <span class="shortcut-key">V</span>
                    </div>
                </div>
            </div>
</body>
</html>"""

    def parse(self, content: str) -> str:
        """Parse markdown content and return HTML.

        This method provides compatibility with ContentParserProtocol.
        """
        return self.parse_content(content)

    def get_word_count(self, content: str) -> int:
        """Get word count from content.

        Args:
            content: Markdown content

        Returns:
            Number of words in the content
        """
        # Strip markdown syntax for accurate word count

        # Remove markdown headers
        text = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)
        # Remove markdown emphasis
        text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
        # Remove markdown links
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Remove markdown images
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)
        # Remove code blocks
        text = re.sub(r"```[^`]*```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "", text)

        # Split by whitespace and count non-empty strings
        words = text.split()
        return len(words)
