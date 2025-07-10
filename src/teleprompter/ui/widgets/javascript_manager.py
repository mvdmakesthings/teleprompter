"""JavaScript code management for the teleprompter widget."""


class JavaScriptManager:
    """Manages JavaScript code for the teleprompter widget."""

    @staticmethod
    def get_scroll_behavior_script() -> str:
        """Get JavaScript for smooth scrolling behavior."""
        return """
        (function() {
            let lastScrollTime = 0;
            let scrollTimeout = null;
            let lastWheelDelta = 0;

            // Enhanced smooth scrolling
            window.smoothScrollTo = function(targetY, duration = 500) {
                const startY = window.pageYOffset;
                const distance = targetY - startY;
                const startTime = performance.now();

                function animation(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);

                    // Easing function
                    const easeInOutCubic = progress < 0.5
                        ? 4 * progress * progress * progress
                        : 1 - Math.pow(-2 * progress + 2, 3) / 2;

                    window.scrollTo(0, startY + distance * easeInOutCubic);

                    if (progress < 1) {
                        requestAnimationFrame(animation);
                    }
                }

                requestAnimationFrame(animation);
            };

            // Track manual scrolling
            let isManualScroll = false;
            let manualScrollTimeout = null;

            window.addEventListener('wheel', function(e) {
                isManualScroll = true;
                lastWheelDelta = e.deltaY;
                clearTimeout(manualScrollTimeout);
                manualScrollTimeout = setTimeout(() => {
                    isManualScroll = false;
                    window.manualScrollDetected();
                }, 150);
            }, { passive: true });

            // Track scroll events for progress updates
            let scrollUpdateTimeout = null;
            let lastScrollTop = -1;

            window.addEventListener('scroll', function(e) {
                const currentScrollTop = window.pageYOffset || (document.documentElement ? document.documentElement.scrollTop : 0);

                // Only trigger update if position actually changed
                if (Math.abs(currentScrollTop - lastScrollTop) > 1) {
                    lastScrollTop = currentScrollTop;

                    // Throttle scroll events
                    clearTimeout(scrollUpdateTimeout);
                    scrollUpdateTimeout = setTimeout(() => {
                        if (window.onScrollUpdate) {
                            window.onScrollUpdate(currentScrollTop);
                        }
                    }, 16); // ~60fps updates
                }
            }, { passive: true });

            // Function to handle manual scroll detection
            window.manualScrollDetected = function() {
                // This function is called when manual scroll is detected
                // Can be used for analytics or other purposes
                console.log('Manual scroll detected');
            };

            // Provide scroll info
            window.getScrollInfo = function() {
                return {
                    scrollTop: window.pageYOffset,
                    scrollHeight: document.documentElement.scrollHeight,
                    clientHeight: window.innerHeight,
                    isManualScroll: isManualScroll,
                    lastWheelDelta: lastWheelDelta
                };
            };

            // Scroll by pixels
            window.scrollByPixels = function(pixels) {
                if (!isManualScroll) {
                    window.scrollBy({
                        top: pixels,
                        behavior: 'auto'
                    });
                }
            };

            console.log('Scroll behavior initialized');
        })();
        """

    @staticmethod
    def get_font_size_script(font_size: int, padding: int) -> str:
        """Get JavaScript for applying font size.

        Args:
            font_size: The font size in pixels
            padding: The bottom padding percentage
        """
        return f"""
        (function() {{
            const style = document.createElement('style');
            style.textContent = `
                body {{
                    font-size: {font_size}px !important;
                    line-height: 1.6 !important;
                    padding-bottom: {padding}vh !important;
                }}

                h1 {{ font-size: {font_size * 2.5}px !important; }}
                h2 {{ font-size: {font_size * 2.0}px !important; }}
                h3 {{ font-size: {font_size * 1.7}px !important; }}
                h4 {{ font-size: {font_size * 1.5}px !important; }}
                h5 {{ font-size: {font_size * 1.3}px !important; }}
                h6 {{ font-size: {font_size * 1.1}px !important; }}

                p, li, td, th {{
                    font-size: {font_size}px !important;
                }}

                code {{
                    font-size: {font_size * 0.9}px !important;
                }}

                pre {{
                    font-size: {font_size * 0.85}px !important;
                }}

                blockquote {{
                    font-size: {font_size * 0.95}px !important;
                }}

                .empty-title {{
                    font-size: {font_size * 1.75}px !important;
                }}

                .empty-subtitle {{
                    font-size: {font_size * 1.25}px !important;
                }}

                .error-title {{
                    font-size: {font_size * 1.5}px !important;
                }}

                .error-message {{
                    font-size: {font_size}px !important;
                }}

                .loading-text {{
                    font-size: {font_size * 1.25}px !important;
                }}

                /* Responsive adjustments */
                @media (max-width: 768px) {{
                    body {{ font-size: {font_size * 0.9}px !important; }}
                    h1 {{ font-size: {font_size * 2.0}px !important; }}
                    h2 {{ font-size: {font_size * 1.75}px !important; }}
                }}
            `;

            // Remove any existing font size styles
            const existingStyle = document.getElementById('teleprompter-font-style');
            if (existingStyle) {{
                existingStyle.remove();
            }}

            style.id = 'teleprompter-font-style';
            document.head.appendChild(style);

            console.log('Font size applied:', '{font_size}px');
        }})();
        """

    @staticmethod
    def get_section_navigation_script() -> str:
        """Get JavaScript for section navigation."""
        return """
        (function() {
            // Find all headings
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            const sections = [];

            headings.forEach((heading, index) => {
                const rect = heading.getBoundingClientRect();
                sections.push({
                    index: index,
                    element: heading,
                    text: heading.textContent,
                    level: parseInt(heading.tagName[1]),
                    top: rect.top + window.pageYOffset,
                    id: heading.id || `section-${index}`
                });
            });

            // Store sections for navigation
            window.documentSections = sections;

            // Navigate to section
            window.navigateToSection = function(index) {
                if (index >= 0 && index < sections.length) {
                    const section = sections[index];
                    const offset = 50; // Offset from top
                    window.smoothScrollTo(section.top - offset, 300);
                    return true;
                }
                return false;
            };

            // Find current section
            window.getCurrentSection = function() {
                const scrollTop = window.pageYOffset;
                const windowHeight = window.innerHeight;
                const threshold = windowHeight * 0.3; // 30% from top

                for (let i = sections.length - 1; i >= 0; i--) {
                    if (sections[i].top <= scrollTop + threshold) {
                        return i;
                    }
                }
                return 0;
            };

            // Get section info
            window.getSectionInfo = function() {
                return {
                    sections: sections.map(s => ({
                        text: s.text,
                        level: s.level,
                        id: s.id
                    })),
                    current: window.getCurrentSection(),
                    total: sections.length
                };
            };

            console.log('Section navigation initialized:', sections.length, 'sections found');
        })();
        """

    @staticmethod
    def get_cursor_visibility_script(visible: bool) -> str:
        """Get JavaScript for cursor visibility control.

        Args:
            visible: Whether the cursor should be visible
        """
        cursor_style = "none" if not visible else "auto"
        return f"""
        (function() {{
            document.body.style.cursor = '{cursor_style}';

            // Apply to all elements
            const style = document.createElement('style');
            style.textContent = `
                * {{
                    cursor: {cursor_style} !important;
                }}
            `;

            // Remove existing cursor style
            const existingStyle = document.getElementById('teleprompter-cursor-style');
            if (existingStyle) {{
                existingStyle.remove();
            }}

            style.id = 'teleprompter-cursor-style';
            document.head.appendChild(style);
        }})();
        """

    @staticmethod
    def get_highlight_current_section_script() -> str:
        """Get JavaScript for highlighting the current section."""
        return """
        (function() {
            let lastHighlighted = null;

            window.highlightCurrentSection = function() {
                const current = window.getCurrentSection();
                if (current !== lastHighlighted && window.documentSections) {
                    // Remove previous highlight
                    if (lastHighlighted !== null && window.documentSections[lastHighlighted]) {
                        const prevElement = window.documentSections[lastHighlighted].element;
                        prevElement.classList.remove('current-section');
                        // Remove marker if it exists
                        const prevMarker = prevElement.querySelector('.current-section-marker');
                        if (prevMarker) {
                            prevMarker.remove();
                        }
                    }

                    // Add current highlight
                    if (window.documentSections[current]) {
                        const currElement = window.documentSections[current].element;
                        currElement.classList.add('current-section');
                        // Add marker element
                        const marker = document.createElement('span');
                        marker.className = 'current-section-marker';
                        marker.textContent = '▶';
                        currElement.insertBefore(marker, currElement.firstChild);
                        lastHighlighted = current;
                    }
                }
            };

            // Style for highlighted section
            const style = document.createElement('style');
            style.textContent = `
                .current-section {
                    position: relative;
                    padding-left: 20px;
                    transition: padding-left 0.3s ease;
                }

                /* Use a span element for the marker instead of ::before */
                .current-section-marker {
                    position: absolute;
                    left: 0;
                    color: #0078d4;
                    animation: pulse 1.5s infinite;
                }

                @keyframes pulse {
                    0% { opacity: 0.6; }
                    50% { opacity: 1; }
                    100% { opacity: 0.6; }
                }
            `;
            document.head.appendChild(style);
        })();
        """

    @staticmethod
    def scroll_to_position(position: float) -> str:
        """Get JavaScript to scroll to a specific position.

        Args:
            position: The position to scroll to (in pixels)
        """
        return f"window.scrollTo(0, {position});"

    @staticmethod
    def get_scroll_position() -> str:
        """Get JavaScript to retrieve current scroll position."""
        return "window.pageYOffset"

    @staticmethod
    def get_document_height() -> str:
        """Get JavaScript to retrieve document height."""
        return "document.documentElement.scrollHeight - window.innerHeight"
