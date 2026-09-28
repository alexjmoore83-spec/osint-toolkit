# OSINT Framework Toolkit - Specification

## Project Overview
- **Project Name:** OSINT Framework Toolkit
- **Type:** Web Application (Single Page App)
- **Core Functionality:** A curated collection of free OSINT (Open Source Intelligence) tools organized by category, similar to osintframework.com
- **Target Users:** Security researchers, investigators, journalists, OSINT enthusiasts

## UI/UX Specification

### Layout Structure
- **Header:** Fixed top navigation with logo and dark mode toggle
- **Sidebar:** Collapsible category navigation (left side)
- **Main Content:** Tool cards organized by category with expandable subcategories
- **Footer:** Notes, credits, and links to original project

### Responsive Breakpoints
- Mobile: < 768px (sidebar becomes drawer)
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Visual Design
- **Color Palette:**
  - Primary: #1a1a2e (dark navy)
  - Secondary: #16213e (deep blue)
  - Accent: #0f3460 (medium blue)
  - Highlight: #e94560 (coral red)
  - Text Primary: #eaeaea
  - Text Secondary: #a0a0a0
  - Background: #0f0f1a
  - Card Background: #1a1a2e
  - Border: #2a2a4a

- **Typography:**
  - Font Family: 'JetBrains Mono' for code/links, 'Outfit' for headings, 'Source Sans Pro' for body
  - Headings: 24px (h1), 20px (h2), 16px (h3)
  - Body: 14px
  - Small: 12px

- **Spacing:**
  - Base unit: 8px
  - Card padding: 16px
  - Section gaps: 24px

- **Visual Effects:**
  - Subtle glow on hover for tool cards
  - Smooth expand/collapse animations for categories
  - Gradient accents on category headers
  - Box shadows: 0 4px 6px rgba(0, 0, 0, 0.3)

### Components
1. **Category Card:** Expandable section with category icon, name, and tool count
2. **Tool Card:** Individual tool with name, description, type badge (T/D/R/M), and link
3. **Search Bar:** Filter tools across all categories
4. **Dark Mode Toggle:** Sun/moon icon button
5. **Sidebar Navigation:** Sticky sidebar with category links
6. **Badge Indicators:**
   - (T) - Tool must be installed locally
   - (D) - Google Dork
   - (R) - Requires registration
   - (M) - Manual URL edit required

## Functionality Specification

### Core Features
1. **Category Navigation:** Click to expand/collapse categories
2. **Tool Display:** Show tool name, description, URL, and type badges
3. **Search:** Real-time filtering of tools by name or description
4. **Dark Mode:** Toggle between light and dark themes
5. **External Links:** Open tools in new tabs
6. **Tool Types:** Visual indicators for different tool types
7. **Local Storage:** Remember dark mode preference

### Categories to Include (similar to osintframework.com)
1. Training
2. Documentation / Evidence Capture
3. OpSec
4. Threat Intelligence
5. Exploits & Advisories
6. Malicious File Analysis
7. AI Tools
8. Tools
9. Encoding / Decoding
10. Classifieds
11. Digital Currency
12. Dark Web
13. Mobile Emulation
14. Metadata
15. Language Translation
16. Archives
17. Forums / Blogs / IRC
18. Search Engines
19. Geolocation Tools / Maps
20. Transportation
21. Business Records
22. Public Records
23. Telephone Numbers
24. Dating
25. People Search Engines
26. Instant Messaging
27. Social Networks
28. Images / Videos / Docs
29. IP & MAC Address
30. Domain Name
31. Email Address
32. Username

### User Interactions
- Click category header to expand/collapse
- Click tool link to open in new tab
- Type in search to filter tools
- Click dark mode toggle to switch themes

## Acceptance Criteria
1. All 32 categories are displayed and expandable
2. Each category contains relevant OSINT tools with valid URLs
3. Search filters tools in real-time
4. Dark mode toggle works and persists preference
5. All external links open in new tabs
6. Responsive design works on mobile/tablet/desktop
7. Page loads without errors
8. All tool type badges (T, D, R, M) are displayed correctly
