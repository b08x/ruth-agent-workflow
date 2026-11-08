# Known Gaps in OpenGAP Port

This note records known gaps and trade-offs resulting from porting R.U.T.H. from Mistral Vibe configuration to OpenGAP:

1. **Dropped Empty Skills:**
   Three placeholder or empty skills listed in the legacy Vibe configuration (`documentation`, `readme-generator`, `code-insights-reports`) were dropped because they lacked actionable implementations.

2. **Web Search Capability:**
   Ruth's Vibe-native web-search connector (`connector_web_search_*`) has no native OpenGAP tool equivalent in the standard tool surface. Web research tasks must fall back to local MCP or external tools.

3. **Instruction Length in update-docs:**
   The `skills/update-docs/SKILL.md` instruction body is 25,852 characters (~6,318 tokens), which exceeds the OpenGAP recommended guidance of ~20,000 characters (<5,000 tokens). Per the port plan, the skill content is preserved intact with an acceptable validator warning.
